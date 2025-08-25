from django.shortcuts import render
from django.conf import settings
from sso.models import EveCharater
from doctrines.models import FitShip, Categories, Doctrine
import requests

# Funcion para conseguir informaciónde la corp y la alianza
def character_corp_alliance_info(character):

    headers = {
    "Accept-Language": "",
    "If-None-Match": "",
    "X-Compatibility-Date": "2020-01-01",
    "X-Tenant": "",
    "Accept": "application/json"
    }

    response_char = requests.get(f'{settings.EVE_ESI_API_URL}/characters/{character.characterId}', headers=headers)
    data = response_char.json()

    if "corporation_id" in data:
        response_corp = requests.get(f'{settings.EVE_ESI_API_URL}/corporations/{data["corporation_id"]}', headers=headers)
        data_corp = response_corp.json()
        character.corpId = data["corporation_id"]
        character.corpName = data_corp["name"]

    if "alliance_id" in data:
        response_alliance = requests.get(f'{settings.EVE_ESI_API_URL}/alliances/{data["alliance_id"]}', headers=headers)
        data_alliance = response_alliance.json()
        character.allianceId = data["alliance_id"]
        character.allianceName = data_alliance["name"]


    return character

# Funcion para saber cuanto dinero tiene en la cartera
def character_wallet_money(character):

    headers = {
        "Accept-Language": "",
        "If-None-Match": "",
        "X-Compatibility-Date": "2020-01-01",
        "X-Tenant": "",
        "Accept": "application/json",
        "Authorization": f"Bearer {character.accessToken}"
    }

    response = requests.get(f'{settings.EVE_ESI_API_URL}/characters/{character.characterId}/wallet', headers= headers)
    data = response.json()

    character.walletMoney = data

    return character

# Funcion para el registro de las tranferencias de la cuenta
def character_wallet_transactions(character):

    headers = {
        "Accept-Language": "",
        "If-None-Match": "",
        "X-Compatibility-Date": "2020-01-01",
        "X-Tenant": "",
        "Accept": "application/json",
        "Authorization": f"Bearer {character.accessToken}"
    }

    response = requests.get(f'{settings.EVE_ESI_API_URL}/characters/{character.characterId}/wallet/transactions', headers=headers)
    data = response.json()

    character.wallet_trans = data
    
    return character

# Funcion para conseguir la cantidad de skillpoints de la cuenta
def character_skill_points(character):
    headers = {
        "Accept-Language": "",
        "If-None-Match": "",
        "X-Compatibility-Date": "2020-01-01",
        "X-Tenant": "",
        "Accept": "application/json",
        "Authorization": f"Bearer {character.accessToken}"
    }

    response = requests.get(f'{settings.EVE_ESI_API_URL}/characters/{character.characterId}/skills', headers=headers)
    data = response.json()
    character.totalSkillPoints = data["total_sp"]

    return character


def fit_list():
    character = EveCharater.objects.filter(characterId = settings.EVE_BOT_CHAR_ID).first()

    headers = {
        "Accept-Language": "",
        "If-None-Match": "",
        "X-Compatibility-Date": "2020-01-01",
        "X-Tenant": "",
        "Accept": "application/json",
        "Authorization": f"Bearer {character.accessToken}"
    }
    
    response = requests.get(
        f'{settings.EVE_ESI_API_URL}/characters/{character.characterId}/fittings',
        headers = headers
    )

    if response.status_code != 200:
        return 1
    
    data = response.json()

    for fit_data in data:
        check = FitShip.objects.filter(fitId = fit_data["fitting_id"])

        item_list = fit_data["items"]

        for item in item_list:
            item["itemName"] = item_name(item["type_id"])

        if check.exists():
            fit = FitShip.objects.get(fitId = fit_data["fitting_id"])
            fit.items = item_list
            fit.save()
        else:
            fit = FitShip.objects.create(
                fitId = fit_data["fitting_id"],
                shipId = fit_data["ship_type_id"],
                shipName = item_name(fit_data["ship_type_id"]),
                nameFit = fit_data["name"],
                desc = fit_data["description"],
                items = item_list,
            )

            fit.save()

    return 0

def item_name(item_ID):

    headers_2 = {
        "Accept-Language": "",
        "If-None-Match": "",
        "X-Compatibility-Date": "2020-01-01",
        "X-Tenant": "",
        "Accept": "application/json"
    }

    response = requests.get(f"{settings.EVE_ESI_API_URL}/universe/types/{item_ID}", headers = headers_2)
    data = response.json()

    return data["name"]

def solar_system_name(solar_system_ID):

    headers_2 = {
        "Accept-Language": "",
        "If-None-Match": "",
        "X-Compatibility-Date": "2020-01-01",
        "X-Tenant": "",
        "Accept": "application/json"
    }

    response = requests.get(f"{settings.EVE_ESI_API_URL}/universe/systems/{solar_system_ID}", headers = headers_2)
    data = response.json()

    return data["name"]