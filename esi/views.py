from django.shortcuts import render
from django.conf import settings
from sso.models import EveCharater
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