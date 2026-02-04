import logging
from django.shortcuts import render
from django.conf import settings
from sso.models import EveCharater
from doctrines.models import FitShip
from skillplans.models import Skillplan, Skillplan_CheckList
from ban.models import SuspiciousNotification
from utils.views import update_pages, handler, esi_call
from datetime import datetime
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

    response_char = requests.get(f'{settings.EVE_ESI_API_URL}/characters/{character.characterId}', headers=headers)
    if response_char.status_code != 200:
        return character
    
    data = response_char.json()
    print(data)
    if "corporation_id" in data:
        response_corp = requests.get(f'{settings.EVE_ESI_API_URL}/corporations/{data["corporation_id"]}', headers=headers)
        data_corp = response_corp.json()
        character.corpId = data["corporation_id"]
        character.corpName = data_corp["name"]
    else:
        character.corpId = 0
        character.corpName = ""
        
    if "alliance_id" in data:
        response_alliance = requests.get(f'{settings.EVE_ESI_API_URL}/alliances/{data["alliance_id"]}', headers=headers)
        data_alliance = response_alliance.json()
        character.allianceId = data["alliance_id"]
        character.allianceName = data_alliance["name"]
    else:
        character.allianceId = 0
        character.allianceName = ""

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
    if response.status_code != 200:
        return character
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
    if response.status_code != 200:
        return character
    data = response.json()

    character.wallet_trans = data
    
    return character

# Funcion para conseguir la cantidad de skillpoints de la cuenta y las skills
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
    if response.status_code != 200:
        return character
    data = response.json()
    character.totalSkillPoints = data["total_sp"]

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

def update_character_skills(character):
    headers = {
        "Accept-Language": "",
        "If-None-Match": "",
        "X-Compatibility-Date": "2020-01-01",
        "X-Tenant": "",
        "Accept": "application/json",
        "Authorization": f"Bearer {character.accessToken}"
    }

    response = requests.get(f'{settings.EVE_ESI_API_URL}/characters/{character.characterId}/skills', headers=headers)
    if response.status_code != 200:
        return character
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

def transfers(character):
    headers = {
        "Accept-Language": "",
        "If-None-Match": "",
        "X-Compatibility-Date": "2025-08-26",
        "X-Tenant": "",
        "Accept": "application/json",
        "Authorization": f"Bearer {character.accessToken}"
    }

    params = {
        "page" : "1"
    }

    response = requests.get(
        f"{settings.EVE_ESI_API_URL}/characters/{character.characterId}/wallet/journal",
        headers= headers,
        params= params
    )

    data_transfer = response.json()

    type_transfers = [
        "corporation_id",
        "alliance_id",
        "character_id",
        "contract_id",
        ""
    ]
    
    character_list = set(EveCharater.objects.all().values_list('characterId',flat=True))
    corp_list = set(EveCharater.objects.all().filter(corpId__gt = 3000000).values_list('corpId', flat=True))
    autorice_list = character_list | corp_list
    autorice_list.add(1000132)
    autorice_list.add(1639878825)

    for transfer in data_transfer:
        if not isinstance(transfer, dict):
            logging.warning(f"Elemento {transfer} no es dict: {type(transfer)} - {transfer}")
            continue
        
        id_check_1 = transfer.get("first_party_id",0)
        id_check_2 = transfer.get("second_party_id",0)
        transfer_type = transfer.get("context_id_type", "")

        if transfer_type in type_transfers:
            if transfer["ref_type"] != "daily_goal_payouts":
                if id_check_1 not in autorice_list:
                    create_transfer_notification(character, transfer["first_party_id"], transfer["date"], transfer["amount"])
                elif id_check_2 not in autorice_list:
                    create_transfer_notification(character, transfer["second_party_id"], transfer["date"], transfer["amount"])

def create_transfer_notification(character, suspicious_id, date_str, amount):
    dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
    date = dt.date()
    
    headers = {
        "Accept-Language": "",
        "If-None-Match": "",
        "X-Compatibility-Date": "2025-08-26",
        "X-Tenant": "",
        "Accept": "application/json"
    }

    response = requests.get(f"{settings.EVE_ESI_API_URL}/characters/{suspicious_id}", headers= headers)
    name = ""
    if response.status_code != 200:
        response = requests.get(f"{settings.EVE_ESI_API_URL}/corporations/{suspicious_id}", headers= headers)
        if response.status_code != 200:
            response = requests.get(f"{settings.EVE_ESI_API_URL}/alliances/{suspicious_id}", headers= headers)

    if response.status_code != 200:
        logging.warning(f"El id {suspicious_id} no es de ninguna corporacion, alianza o jugador")
        
    name =response.json()["name"]
   
    if amount < 0:
        amount *= -1

    exists = SuspiciousNotification.objects.filter(
        date = date,
        character = character,
        target = name
    ).exists()

    if not exists:
        SuspiciousNotification.objects.create(
            character = character,
            target = name,
            date = date,
            amount = amount
        )
    
def suspicious_name(id, susp_type):
    headers = {
        "Accept-Language": "",
        "If-None-Match": "",
        "X-Compatibility-Date": "2025-08-26",
        "X-Tenant": "",
        "Accept": "application/json"
    }

    if susp_type == 1:
        response = requests.get(f"{settings.EVE_ESI_API_URL}/characters/{id}", headers= headers)
    elif susp_type == 2:
        response = requests.get(f"{settings.EVE_ESI_API_URL}/corporations/{id}", headers= headers)
    else:
        response = requests.get(f"{settings.EVE_ESI_API_URL}/alliances/{id}", headers= headers)

    data = response.json()

    return data["name"]

def character_assets(char):
    headers = {
        "Accept-Language": "",
        "If-None-Match": "",
        "X-Compatibility-Date": "2025-12-16",
        "X-Tenant": "",
        "If-Modified-Since": "",
        "Accept": "application/json",
        "Authorization": f"Bearer {char.accessToken}"
    }

    url = f"{settings.EVE_ESI_API_URL}/characters/{char.characterId}/assets"

    try:
        assets = update_pages(
            max_retries=3,
            handler=handler,
            url=url,
            headers=headers
        )
        return assets

    except requests.HTTPError as e:
        return f"Error HTTP: {e.response.status_code}"
    except Exception as e:
        return f"Error inesperado: {str(e)}"


def character_wallet_journal(char):
    headers = {
        "Accept-Language": "",
        "If-None-Match": "",
        "X-Compatibility-Date": "2025-12-16",
        "X-Tenant": "",
        "If-Modified-Since": "",
        "Accept": "application/json",
        "Authorization": f"Bearer {char.accessToken}"
    }
    
    url = f"{settings.EVE_ESI_API_URL}/characters/{char.characterId}/wallet/journal/"
    try:

        wallet = update_pages(
            max_retries=3,
            handler=handler,
            url=url,
            headers=headers
        )
        return wallet

    except requests.HTTPError as e:
        return f"Error HTTP: {e.response.status_code}"
    except Exception as e:
        return f"Error inesperado: {str(e)}"

def info_transfer_target_name(id):
    headers = {
        "Accept": "application/json",
        "X-Compatibility-Date": "2025-08-26",
    }

    url = f"{settings.EVE_ESI_API_URL}/universe/names/"
    response = requests.post(url, json=[id], headers=headers)

    if response.status_code != 200:
        logging.warning(f"No se pudo resolver el ID {id}")
        return f"Unknown ({id})"

    data = response.json()

    if not data:
        return f"Unknown ({id})"

    return data[0].get("name", f"Unknown ({id})")

# Function obtain structures data
def structure_data(character, structure_id):
  
    headers = {
        "Accept-Language": "",
        "If-None-Match": "",
        "X-Compatibility-Date": "2025-12-16",
        "X-Tenant": "",
        "Accept": "application/json",
        "Authorization": f"Bearer {character.accessToken}"
    }
    
    headers_station = {
        "Accept-Language": "",
        "If-None-Match": "",
        "X-Compatibility-Date": "2025-12-16",
        "X-Tenant": "",
        "If-Modified-Since": "",
        "Accept": "application/json"
    }
    
    response = requests.get(
        f"{settings.EVE_ESI_API_URL}/universe/structures/{structure_id}",
        headers=headers
    )
    response = esi_call(response)
    if response.status_code != 200:
        response = requests.get(
            f"{settings.EVE_ESI_API_URL}/universe/stations/{structure_id}",
            headers=headers_station
        )
        response = esi_call(response)

    return response.json()

def group_data(group_id):
    headers = {
        "Accept-Language": "",
        "If-None-Match": "",
        "X-Compatibility-Date": "2025-12-16",
        "X-Tenant": "",
        "If-Modified-Since": "",
        "Accept": "application/json"
    }
    
    url = f"{settings.EVE_ESI_API_URL}/universe/groups/{group_id}"
    response = requests.get(url=url, headers=headers)
    response = esi_call(response)
    
    return response.json()
    