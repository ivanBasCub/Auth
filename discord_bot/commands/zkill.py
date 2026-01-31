import os
from dotenv import load_dotenv
import discord
from discord.ext import tasks
import aiohttp
from utils import persistence
from utils.esi import (
    get_type_name,
    get_system_name,
    get_character_name,
    get_corp_name,
    get_alliance_name
)

load_dotenv()

def register(bot):
    # Ruta correcta al JSON
    STATIC_FILE = os.path.join(os.path.dirname(__file__), "..", "json", "zkill_data.json")
    STATIC_FILE = os.path.abspath(STATIC_FILE)

    # Cargar datos en el bot
    bot.zkill_data = persistence.load_data(STATIC_FILE)

    ZKILL_API = os.getenv("ZKILL_API_URL")

    def init(): 
        print("ZKILL_DATA cargado:", bot.zkill_data) 
        if bot.zkill_data and not fetch_kills.is_running(): 
            fetch_kills.start() 
            
    bot.zkill_init = init

    @bot.command()
    async def zkill(ctx, eve_id: int, type: int):
        await ctx.message.delete()

        data = bot.zkill_data

        if eve_id in data:
            data[eve_id]["channels"].add(ctx.channel.id)
        else:
            data[eve_id] = {
                "channels": {ctx.channel.id},
                "type": type,
                "last_kill": None
            }

        persistence.save_data(STATIC_FILE, data)

        if 1 <= type <= 3:
            if not fetch_kills.is_running():
                fetch_kills.start()
        else:
            error_embed = discord.Embed(
                title=f"**Error** No existe la opción {type}",
                description="Opciones válidas:\n1.- Personaje\n2.- Corporación\n3.- Alianza",
                color=discord.Color.red()
            )
            await ctx.send(embed=error_embed)

    @bot.command()
    async def stopzkill(ctx, eve_id: str):
        await ctx.message.delete()

        data = bot.zkill_data

        if eve_id in data:
            data[eve_id]["channels"].discard(ctx.channel.id)

            if not data[eve_id]["channels"]:
                del data[eve_id]

            if not data and fetch_kills.is_running():
                fetch_kills.stop()

            persistence.save_data(STATIC_FILE, data)
        else:
            await ctx.send("No hay seguimiento activo para ese ID")

    @tasks.loop(minutes=1)
    async def fetch_kills():
        async with aiohttp.ClientSession() as session:

            data = bot.zkill_data

            for eve_id, entry in list(data.items()):
                eve_id = int(eve_id)
                type_eve_id = entry["type"]
                kills = []

                # URLs según tipo
                if type_eve_id == 1:
                    url1 = f"{ZKILL_API}/kills/characterID/{eve_id}/"
                    url2 = f"{ZKILL_API}/losses/characterID/{eve_id}/"
                elif type_eve_id == 2:
                    url1 = f"{ZKILL_API}/kills/corporationID/{eve_id}/"
                    url2 = f"{ZKILL_API}/losses/corporationID/{eve_id}/"
                else:
                    url1 = f"{ZKILL_API}/kills/allianceID/{eve_id}/"
                    url2 = f"{ZKILL_API}/losses/allianceID/{eve_id}/"

                # Peticiones
                for url in (url1, url2):
                    async with session.get(url, headers={"Accept-Encoding": "gzip"}) as resp:
                        if resp.status == 200:
                            payload = await resp.json()
                            if isinstance(payload, list):
                                kills.extend(payload)

                if not kills:
                    continue

                kills_sorted = sorted(kills, key=lambda k: k["killmail_id"], reverse=True)

                new_kills = [
                    k for k in kills_sorted
                    if entry["last_kill"] is None or k["killmail_id"] > entry["last_kill"]
                ]

                if not new_kills:
                    continue

                # Enviar notificaciones
                if entry["last_kill"] is not None:
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

                        ship_name = await get_type_name(session, ship_type_id)
                        system_name = await get_system_name(session, system_id)
                        pilot_name = await get_character_name(session, character_id)
                        corp_name = await get_corp_name(session, corp_id)
                        alliance_name = await get_alliance_name(session, alliance_id)

                        total_value = kill["zkb"].get("totalValue", 0)
                        num_attackers = len(km_data["attackers"])

                        title = f"**{pilot_name}** perdió una **{ship_name}** en {system_name}"
                        if pilot_name == "":
                            title = f"**{corp_name}** perdió una **{ship_name}** en {system_name}"

                        embed = discord.Embed(
                            title=title,
                            url=f"https://zkillboard.com/kill/{km_id}/",
                            color=discord.Color.red()
                        )

                        # Color verde si no es el objetivo
                        if type_eve_id == 1 and character_id != eve_id:
                            embed.color = discord.Color.green()
                        elif type_eve_id == 2 and corp_id != eve_id:
                            embed.color = discord.Color.green()
                        elif type_eve_id == 3 and alliance_id != eve_id:
                            embed.color = discord.Color.green()

                        if corp_name:
                            embed.add_field(
                                name="Corporación",
                                value=f"[{corp_name}](https://zkillboard.com/corporation/{corp_id}/)",
                                inline=True
                            )
                        if alliance_name:
                            embed.add_field(
                                name="Alianza",
                                value=f"[{alliance_name}](https://zkillboard.com/alliance/{alliance_id}/)",
                                inline=True
                            )

                        embed.add_field(name="Valor ISK", value=f"{total_value:,.2f} ISK", inline=False)
                        embed.add_field(name="Participantes", value=f"{num_attackers}", inline=False)

                        embed.set_thumbnail(url=f"https://images.evetech.net/types/{ship_type_id}/render?size=128")

                        # Enviar a canales
                        for channel_id in entry["channels"]:
                            channel = bot.get_channel(channel_id)
                            if channel:
                                await channel.send(embed=embed)

                entry["last_kill"] = new_kills[0]["killmail_id"]
                persistence.save_data(STATIC_FILE, data)

    @fetch_kills.before_loop
    async def before_fetch():
        await bot.wait_until_ready()
