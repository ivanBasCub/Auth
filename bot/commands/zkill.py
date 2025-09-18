from bot.main import bot
import discord
from discord.ext import tasks
from django.conf import settings
from bot.utils.esi import get_type_name, get_system_name, get_character_name, get_corp_name,get_alliance_name
import aiohttp
from bot.utils import persistence

STATIC_FILE = "bot/json/zkill_data.json"
ZKILL_DATA = {}

@bot.event
async def on_ready():
    global ZKILL_DATA 
    ZKILL_DATA = persistence.load_data(STATIC_FILE)
    if ZKILL_DATA != {}:
        fetch_kills.start()


@bot.command()
async def zkill(ctx, eve_id: int, type: int):
    global ZKILL_DATA 
    await ctx.message.delete()
    ZKILL_DATA = persistence.load_data(STATIC_FILE)

    if eve_id in ZKILL_DATA:
        ZKILL_DATA[eve_id]["channels"].add(ctx.channel.id)
    else:
        ZKILL_DATA[eve_id] = {
            "channels": set(),
            "type": type,
            "last_kill": None
        }
        ZKILL_DATA[eve_id]["channels"].add(ctx.channel.id)
    
    persistence.save_data(STATIC_FILE, ZKILL_DATA)
    if 1 <= type <= 3:
        if not fetch_kills.is_running():
            fetch_kills.start()
    else:
        error_embed = discord.Embed(
            title=f"**Error** No existe la opcion {type}",
            description= "Solo existe las siguientes opciones:\n1.- Personaje\n2.- Corporaciones\n3.- Alianza",
            color=discord.Color.red()
        )

        await ctx.send(embed=error_embed)
        
# Parar el loop
@bot.command()
async def stopzkill(ctx, eve_id: str):
    global ZKILL_DATA
    await ctx.message.delete()
    ZKILL_DATA = persistence.load_data(STATIC_FILE)

    if eve_id in ZKILL_DATA:
        ZKILL_DATA[eve_id]["channels"].discard(ctx.channel.id)
        if not ZKILL_DATA[eve_id]["channels"]:
            del ZKILL_DATA[eve_id]
        if not ZKILL_DATA and fetch_kills.is_running():
            fetch_kills.stop()
        persistence.save_data(STATIC_FILE, ZKILL_DATA)
    else:
        await ctx.send("No hay seguimiento activo para ese ID")

# Task
@tasks.loop(minutes=1)
async def fetch_kills():
    global ZKILL_DATA
    try:
        async with aiohttp.ClientSession() as session:

            ZKILL_DATA = persistence.load_data(STATIC_FILE)

            for eve_id, data in list(ZKILL_DATA.items()):
                eve_id = int(eve_id)
                type_eve_id = data["type"]
                kills = []
                # Configuración de la URL
                if type_eve_id == 1:
                    zkill_kill_url_1 = f"{settings.ZKILL_API_URL}/kills/characterID/{eve_id}/"
                    zkill_kill_url_2 = f"{settings.ZKILL_API_URL}/losses/characterID/{eve_id}/"
                elif type_eve_id == 2:
                    zkill_kill_url_1 = f"{settings.ZKILL_API_URL}/kills/corporationID/{eve_id}/"
                    zkill_kill_url_2 = f"{settings.ZKILL_API_URL}/losses/corporationID/{eve_id}/"
                elif type_eve_id == 3:
                    zkill_kill_url_1 = f"{settings.ZKILL_API_URL}/kills/allianceID/{eve_id}/"
                    zkill_kill_url_2 = f"{settings.ZKILL_API_URL}/losses/allianceID/{eve_id}/"
                
                # Peticiones Https
                async with session.get(zkill_kill_url_1, headers={"Accept-Encoding": "gzip"}) as resp:
                    if resp.status == 200:
                        data_url = await resp.json()
                        if isinstance(data_url, list):
                            kills = data_url

                async with session.get(zkill_kill_url_2, headers={"Accept-Encoding": "gzip"}) as resp:
                    if resp.status == 200:
                        data_url = await resp.json()
                        if isinstance(data_url, list):
                            kills.extend(data_url)

                if not kills:
                    continue

                kills_list = sorted(kills, key=lambda k: k["killmail_id"], reverse=True)
                new_kills = []
                for kill in kills_list:
                    if data["last_kill"] is None or kill["killmail_id"] > data["last_kill"]:
                        new_kills.append(kill)

                if not new_kills:
                    continue
                
                data["last_kill"] = new_kills[0]["killmail_id"]
                persistence.save_data(STATIC_FILE, ZKILL_DATA)

                # Preparación de datos y creación del embed
                for kill in reversed(new_kills):
                    km_id = kill["killmail_id"]
                    km_hash = kill["zkb"]["hash"]
                    esi_url = f"https://esi.evetech.net/latest/killmails/{km_id}/{km_hash}/"
                    async with session.get(esi_url) as esi_resp:
                        if esi_resp.status != 200:
                            continue
                        km_data = await esi_resp.json()

                    victim = km_data["victim"]
                    ship_type_id = victim["ship_type_id"]
                    system_id = km_data["solar_system_id"]
                    character_id = victim.get("character_id")
                    corp_id = victim.get("corporation_id")
                    alliance_id = victim.get("alliance_id")
                    top_damage_id = 0
                    final_blow_id = 0
                    num_attackers = len(km_data["attackers"])

                    aux = 0
                    for attacker in km_data["attackers"]:
                        final_id = attacker.get("character_id",0)
                        if aux < attacker["damage_done"]:
                            aux = attacker["damage_done"]
                            top_damage_id = final_id
                        if attacker["final_blow"]:
                            final_blow_id = final_id

                    ship_name = await get_type_name(session, ship_type_id)
                    system_name = await get_system_name(session, system_id)
                    pilot_name = await get_character_name(session, character_id)
                    corp_name = await get_corp_name(session, corp_id)
                    alliance_name = await get_alliance_name(session, alliance_id)
                    final_blow_name = ""
                    top_damage_name = ""
                    if top_damage_id != 0 and final_blow_id != 0:
                        final_blow_name = await get_character_name(session, final_blow_id)
                        top_damage_name = await get_character_name(session, top_damage_id)

                    total_value = kill["zkb"].get("totalValue", 0)

                    title_embed = f"**{pilot_name}** perdió una **{ship_name}** en {system_name}"

                    if pilot_name == "":
                        title_embed = f"**{corp_name}** perdió una **{ship_name}** en {system_name}"

                    embed = discord.Embed(
                        title=title_embed,
                        url= f"https://zkillboard.com/kill/{km_id}/",
                        color=discord.Color.red()
                    )
                    if type_eve_id == 1 and character_id != eve_id:
                        embed.color = discord.Color.green()
                    elif type_eve_id == 2 and corp_id != eve_id:
                        embed.color = discord.Color.green()
                    elif type_eve_id == 3 and alliance_id != eve_id:
                        embed.color = discord.Color.green()

                    if corp_name != "":
                        embed.add_field(name="Corporación", value=f"[{corp_name}](https://zkillboard.com/corporation/{corp_id}/)", inline=True)
                    if alliance_name != "":
                        embed.add_field(name="Alianza", value=f"[{alliance_name}](https://zkillboard.com/alliance/{alliance_id}/)", inline=True)

                    embed.add_field(name="Valor ISK", value=f"{total_value:,.2f} ISK", inline=False)
                    embed.add_field(name="Numero de Participantes", value=f"{num_attackers}", inline=False)

                    if top_damage_name != "":
                        embed.add_field(name="Top Damage",value=f"[{top_damage_name}](https://zkillboard.com/character/{top_damage_id})", inline=True)
                    if final_blow_name != "":
                        embed.add_field(name="Final Blow",value=f"[{final_blow_name}](https://zkillboard.com/character/{final_blow_id})", inline=True)

                    embed.set_thumbnail(url=f"https://images.evetech.net/types/{ship_type_id}/render?size=128")

                    for channel_id in data["channels"]:
                        channel = bot.get_channel(channel_id)
                        if channel:
                            await channel.send(embed=embed)
    except Exception as e:
        print(f"[fetch_kills] Error: {e}")

@fetch_kills.before_loop
async def before_fetch():
    await bot.wait_until_ready()