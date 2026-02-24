import logging
from django.conf import settings
from sso.models import Eve_Character
from doctrines.models import Fit
from skillplans.models import Skillplan, Skillplan_CheckList
from utils.views import update_pages, handler, esi_call
import requests

def check_skill(pj_skill, skillplan):
        for skill, nivel in skillplan.items():
            if skill not in pj_skill or pj_skill[skill] < nivel:
                return False
        return True

# Funcion para conseguir informaciónde la corp y la alianza
def character_corp_alliance_info(character):

    headers = {
    "Accept-Language": "",
    "If-None-Match": "",
    "X-Compatibility-Date": "2020-01-01",
    "X-Tenant": "",
    "Accept": "application/json"
    }

    response_char = requests.get(f'{settings.EVE_ESI_API_URL}/characters/{character.character_id}', headers=headers)
    if response_char.status_code != 200:
        return character
    
    data = response_char.json()
    if "corporation_id" in data:
        response_corp = requests.get(f'{settings.EVE_ESI_API_URL}/corporations/{data["corporation_id"]}', headers=headers)
        data_corp = response_corp.json()
        character.corp_id = data["corporation_id"]
        character.corp_name = data_corp["name"]
    else:
        character.corp_id = 0
        character.corp_name = ""
        
    if "alliance_id" in data:
        response_alliance = requests.get(f'{settings.EVE_ESI_API_URL}/alliances/{data["alliance_id"]}', headers=headers)
        data_alliance = response_alliance.json()
        character.alliance_id = data["alliance_id"]
        character.alliance_name = data_alliance["name"]
    else:
        character.alliance_id = 0
        character.alliance_name = ""

    return character

# Funcion para saber cuanto dinero tiene en la cartera
def character_wallet_money(character):

    headers = {
        "Accept-Language": "",
        "If-None-Match": "",
        "X-Compatibility-Date": "2020-01-01",
        "X-Tenant": "",
        "Accept": "application/json",
        "Authorization": f"Bearer {character.access_token}"
    }

    response = requests.get(f'{settings.EVE_ESI_API_URL}/characters/{character.character_id}/wallet', headers= headers)
    if response.status_code != 200:
        return character
    data = response.json()

    character.money = data

    return character

# Funcion para conseguir la cantidad de skillpoints de la cuenta y las skills
def character_skill_points(character):
    headers = {
        "Accept-Language": "",
        "If-None-Match": "",
        "X-Compatibility-Date": "2020-01-01",
        "X-Tenant": "",
        "Accept": "application/json",
        "Authorization": f"Bearer {character.access_token}"
    }

    response = requests.get(f'{settings.EVE_ESI_API_URL}/characters/{character.character_id}/skills', headers=headers)
    if response.status_code != 200:
        return character
    data = response.json()
    character.skill_points = data["total_sp"]

    list_skills = {}
    
    if character.skills == {}:
        for skill in data["skills"]:
            name = item_name(skill["skill_id"])
            list_skills[name] = skill["trained_skill_level"]
        character.skills = list_skills
    
        skillplan_list = Skillplan.objects.all()
    
        for sp in skillplan_list:
            pj_skill = character.skills
            sp_skills = sp.skills
            status = check_skill(pj_skill, sp_skills)
            
            checklist_obj = Skillplan_CheckList.objects.filter(
                skillPlan = sp,
                character = character
            ).first()
            
            if checklist_obj:
                checklist_obj.status = status
            else:
                checklist_obj = Skillplan_CheckList.objects.create(status=status)
                checklist_obj.skillPlan.add(sp)
                checklist_obj.character.add(character)

            checklist_obj.save()
            
    return character

# Function to update the skills of a character
def update_character_skills(character):
    headers = {
        "Accept-Language": "",
        "If-None-Match": "",
        "X-Compatibility-Date": "2020-01-01",
        "X-Tenant": "",
        "Accept": "application/json",
        "Authorization": f"Bearer {character.access_token}"
    }

    response = requests.get(f'{settings.EVE_ESI_API_URL}/characters/{character.character_id}/skills', headers=headers)
    if response.status_code != 200:
        return character
    data = response.json()
    character.skill_points = data["total_sp"]

    list_skills = {}
    
    
    for skill in data["skills"]:
        name = item_name(skill["skill_id"])
        list_skills[name] = skill["trained_skill_level"]
    
    character.skills = list_skills
    
    return character


def fit_list():
    character = Eve_Character.objects.filter(character_id = settings.EVE_BOT_CHAR_ID).first()

    headers = {
        "Accept-Language": "",
        "If-None-Match": "",
        "X-Compatibility-Date": "2020-01-01",
        "X-Tenant": "",
        "Accept": "application/json",
        "Authorization": f"Bearer {character.access_token}"
    }
    
    response = requests.get(
        f'{settings.EVE_ESI_API_URL}/characters/{character.character_id}/fittings',
        headers = headers
    )

    if response.status_code != 200:
        return 1
    
    data = response.json()

    for fit_data in data:
        check = Fit.objects.filter(fitId = fit_data["fitting_id"])
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
            fit = Fit.objects.get(fitId = fit_data["fitting_id"])
            fit.items = item_list
            fit.min_skills = all_skills
            fit.save()
        else:
            fit = Fit.objects.create(
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
    headers = {
        "Accept-Language": "",
        "If-None-Match": "",
        "X-Compatibility-Date": "2020-01-01",
        "X-Tenant": "",
        "Accept": "application/json"
    }

    response = requests.get(f"{settings.EVE_ESI_API_URL}/universe/types/{item_id}", headers = headers)
    response = esi_call(response)
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
