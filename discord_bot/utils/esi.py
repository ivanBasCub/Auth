import os
from dotenv import load_dotenv
load_dotenv()

API_URL = os.getenv("EVE_ESI_API_URL")

# Funciones para sacar nombres
async def get_type_name(session, type_id):
    url = f"{API_URL}/latest/universe/types/{type_id}/"
    async with session.get(url) as resp:
        if resp.status != 200:
            return str(type_id)
        data = await resp.json()
        return data.get("name", str(type_id))

async def get_system_name(session, system_id):
    url = f"{API_URL}/latest/universe/systems/{system_id}/"
    async with session.get(url) as resp:
        if resp.status != 200:
            return str(system_id)
        data = await resp.json()
        return data.get("name", str(system_id))

async def get_character_name(session, char_id):
    if not char_id:
        return "Desconocido"
    url = f"{API_URL}/latest/characters/{char_id}/"
    async with session.get(url) as resp:
        if resp.status != 200:
            return "Desconocido"
        data = await resp.json()
        return data.get("name", "")

async def get_corp_name(session, corp_id):
    if not corp_id:
        return "Desconocida"
    url = f"{API_URL}/latest/corporations/{corp_id}/"
    async with session.get(url) as resp:
        if resp.status != 200:
            return "Desconocida"
        data = await resp.json()
        return data.get("name", "")

async def get_alliance_name(session, alliance_id):
    if not alliance_id:
        return "Desconocida"
    url = f"{API_URL}/latest/alliances/{alliance_id}/"
    async with session.get(url) as resp:
        if resp.status != 200:
            return "Desconocida"
        data = await resp.json()
        return data.get("name", "")