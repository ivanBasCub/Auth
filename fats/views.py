from django.shortcuts import render
from django.conf import settings
from sso.models import EveCharater
from esi.views import item_name, solar_system_name
from doctrines.models import Doctrine
from .models import Fats, FleetType
import requests

# Create your views here.
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

