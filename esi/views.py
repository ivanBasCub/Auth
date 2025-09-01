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

    list_skills = {}

    for skill in data["skills"]:
        name = item_name(skill["skill_id"])
        list_skills[name] = skill["trained_skill_level"]

    character.skills = list_skills
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
        all_skills = {}
        item_list = fit_data["items"]
        set_items_id = {fit_data["ship_type_id"]}

        for item in item_list:
            item["itemName"] = item_name(item["type_id"])
            set_items_id.add(item["type_id"])

        for item_id in set_items_id:
            skills = get_required_skills(item_id)
            for name, level in skills.items():
                all_skills[name] = max(all_skills.get(name, 0), level)

        if check.exists():
            fit = FitShip.objects.get(fitId = fit_data["fitting_id"])
            fit.items = item_list
            fit.min_skills = all_skills
            fit.save()
        else:
            fit = FitShip.objects.create(
                fitId = fit_data["fitting_id"],
                shipId = fit_data["ship_type_id"],
                shipName = item_name(fit_data["ship_type_id"]),
                nameFit = fit_data["name"],
                desc = fit_data["description"],
                items = item_list,
                min_skills = all_skills
            )

            fit.save()

    return 0

def item_data(item_id):
    headers_2 = {
        "Accept-Language": "",
        "If-None-Match": "",
        "X-Compatibility-Date": "2020-01-01",
        "X-Tenant": "",
        "Accept": "application/json"
    }

    response = requests.get(f"{settings.EVE_ESI_API_URL}/universe/types/{item_id}", headers = headers_2)
    return response.json()

def get_required_skills(type_id, visited=None):
    SKILL_ATTRS = [
        (182, 277),   # Skill 1
        (183, 278),   # Skill 2
        (184, 279),   # Skill 3
        (1285, 1286), # Skill 4
        (1289, 1287), # Skill 5
        (1290, 1288), # Skill 6
    ]

    """
    Devuelve un diccionario {skill_name: nivel} con todas las skills mínimas
    necesarias para un type_id, incluyendo prerequisitos recursivos.
    """
    if visited is None:
        visited = set()

    if type_id in visited:
        return {}
    visited.add(type_id)

    data = item_data(type_id)
    attrs = {a['attribute_id']: a['value'] for a in data.get('dogma_attributes', [])}

    skills = {}

    for skill_attr, level_attr in SKILL_ATTRS:
        if skill_attr in attrs:
            skill_id = int(attrs[skill_attr])
            level = int(attrs.get(level_attr, 0))

            skill_data = item_data(skill_id)
            skill_name = skill_data['name']

            # Guardar el nivel más alto si ya existe
            if skill_name in skills:
                skills[skill_name] = max(skills[skill_name], level)
            else:
                skills[skill_name] = level

            # Recursivamente obtener prerequisitos de esa skill
            sub_skills = get_required_skills(skill_id, visited)
            for sub_name, sub_level in sub_skills.items():
                if sub_name in skills:
                    skills[sub_name] = max(skills[sub_name], sub_level)
                else:
                    skills[sub_name] = sub_level

    return skills
                
def item_name(item_ID):
    data = item_data(item_ID)

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