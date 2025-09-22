from django.shortcuts import render
from django.conf import settings
from sso.models import EveCharater
from esi.views import item_name, solar_system_name
from doctrines.models import Doctrine
from .models import Fats, FleetType, SRP, SRPShips
import requests
import random
import string

def create_srp_id(length = 10):
    characters = string.ascii_lowercase + string.digits
    return ''.join(random.choices(characters, k=length))


def create_fats(characterId, doctrineId, fleetTypeId, fleetName):
    character = EveCharater.objects.get(characterId = characterId)
    doctrine = Doctrine.objects.get(id = doctrineId)
    fleetType = FleetType.objects.get(id = fleetTypeId)

    headers = {
        "Accept-Language": "",
        "If-None-Match": "",
        "X-Compatibility-Date": "2020-01-01",
        "X-Tenant": "",
        "Accept": "application/json",
        "Authorization": f"Bearer {character.accessToken}"
    }

    response = requests.get(f'{settings.EVE_ESI_API_URL}/characters/{character.characterId}/fleet', headers= headers)

    if response.status_code == 200:
        data_fc = response.json()
        if character.characterId == data_fc["fleet_boss_id"]:
            response = requests.get(f'{settings.EVE_ESI_API_URL}/fleets/{data_fc["fleet_id"]}/members', headers= headers)
            
            if response.status_code == 200:
                data_members = response.json()
                for member in data_members:
                    fat = Fats.objects.create(
                        name = fleetName,
                        characterFC = character,
                        character = EveCharater.objects.get(characterId = member["character_id"]),
                        fleetType = fleetType,
                        doctrine = doctrine,
                        solarSystem = solar_system_name(member["solar_system_id"]),
                        ship = item_name(member["ship_type_id"])
                    )
                    fat.save()

                    if fat.character == character:
                        srp_id = create_srp_id()
                        new_srp = SRP.objects.create(
                            srp_id = srp_id,
                            status = 0,
                            srp_cost = 0,
                            fleet = fat
                        )

                        new_srp.save()


def create_srp_request(zkill_id, srp):

    # URL = https://zkillboard.com/api/kills/killID/129938002/
    headers_zkill = {"Accept-Encoding": "gzip"}
    headers_eve = {
        "Accept-Language": "",
        "If-None-Match": "",
        "X-Compatibility-Date": "2025-08-26",
        "X-Tenant": "",
        "Accept": "application/json"
    }

    res_zkill = requests.get(f"{settings.ZKILL_API_URL}/kills/killID/{zkill_id}/", headers_zkill)
    if res_zkill.status_code != 200:
        return -1
    
    data_zkill = res_zkill.json()
    zkill_hash = data_zkill[0]['zkb']['hash']
    if zkill_hash == "":
        return -2
    
    res_eve = requests.get(f"{settings.EVE_ESI_API_URL}/killmails/{zkill_id}/{zkill_hash}", headers_eve)
    if res_eve.status_code != 200:
        return -1
    
    data_eve = res_eve.json()

    res_insurance = requests.get(f"{settings.EVE_ESI_API_URL}/insurance/prices", headers_eve)
    if res_insurance.status_code != 200:
        return -1

    insurance_list = res_insurance.json()
    
    # Create data
    pilot_id = data_eve["victim"]["character_id"]
    ship_id = data_eve["victim"]["ship_type_id"]
    try:
        pilot = EveCharater.objects.get(characterId = pilot_id)
    except EveCharater.DoesNotExist:
        return -3
    
    ship_name = item_name(ship_id)
    zkill_value = data_zkill[0]['zkb']['totalValue']
    insurance_value = 0
    for insurance in insurance_list:
        if insurance["type_id"] == ship_id:
            for level in insurance["levels"]:
                if level["name"] == "Platinum":
                    insurance_value = level["payout"]
                    break

    roam = FleetType.objects.get(name = "Roam")
    if srp.fleet.fleetType == roam:
        srp_cost = (zkill_value - insurance_value)* 0.5
        if srp_cost > 200_000_000:
            srp_cost = 200_000_000
    else:
        srp_cost = zkill_value - insurance_value

    new_srp_ship = SRPShips.objects.create(
        pilot = pilot,
        zkill_id = zkill_id,
        ship_id = ship_id,
        ship_name = ship_name,
        srp = srp,
        zkill_value = zkill_value,
        srp_cost = srp_cost,
        status = 0
    )
    new_srp_ship.save()

    srp.srp_cost += srp_cost
    srp.save()
    return 0