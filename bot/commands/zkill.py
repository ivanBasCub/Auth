from bot.main import bot
import discord
from discord.ext import tasks
from django.conf import settings
from bot.utils.esi import get_type_name, get_system_name, get_character_name, get_corp_name,get_alliance_name
import aiohttp

zkill_loops = {}
# Commands
# Start Task
@bot.command()
async def zkill(ctx, eve_id: int, type: int):
    await ctx.message.delete()

    zkill_loops[eve_id] = {
        "channels": set(),
        "type": type,
        "last_kill": None
    }
    zkill_loops[eve_id]["channels"].add(ctx.channel.id)

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
async def stopzkill(ctx, eve_id: int):
    await ctx.message.delete()

    if eve_id in zkill_loops:
        zkill_loops[eve_id]["channels"].discard(ctx.channel.id)
        if not zkill_loops[eve_id]["channels"]:
            del zkill_loops[eve_id]
        if not zkill_loops and fetch_kills.is_running():
            fetch_kills.stop()
    else:
        await ctx.send("No hay seguimiento activo para ese ID")

# Task
@tasks.loop(minutes=1)
async def fetch_kills():
    async with aiohttp.ClientSession() as session:
        for eve_id, data in list(zkill_loops.items()):
            type_eve_id = data["type"]
            kills = []
            # Configuración de la URL
            if type_eve_id == 1:
                zkill_kill_url = f"{settings.ZKILL_API_URL}/kills/characterID/{eve_id}/"
                zkill_losses_url = f"{settings.ZKILL_API_URL}/losses/characterID/{eve_id}/"
            elif type_eve_id == 2:
                zkill_kill_url = f"{settings.ZKILL_API_URL}/kills/corporationID/{eve_id}/"
                zkill_losses_url = f"{settings.ZKILL_API_URL}/losses/corporationID/{eve_id}/"
            elif type_eve_id == 3:
                zkill_kill_url = f"{settings.ZKILL_API_URL}/kills/allianceID/{eve_id}/"
                zkill_losses_url = f"{settings.ZKILL_API_URL}/losses/allianceID/{eve_id}/"
            
            # Peticiones Https
            async with session.get(zkill_kill_url, headers={"Accept-Encoding": "gzip"}) as resp:
                if resp.status == 200:
                    data_url = await resp.json()
                    if isinstance(data_url, list):
                        kills = data_url

            async with session.get(zkill_losses_url, headers={"Accept-Encoding": "gzip"}) as resp:
                if resp.status == 200:
                    data_url = await resp.json()
                    if isinstance(data_url, list):
                        kills.extend(data_url)

            if not kills:
                continue

            kills_list = sorted(kills, key=lambda k: k["killmail_id"], reverse=True)
            # Filtrar nuevas kills
            new_kills = []
            for kill in kills_list:
                if data["last_kill"] is None or kill["killmail_id"] > data["last_kill"]:
                    new_kills.append(kill)
                else:
                    break

            if not new_kills:
                continue
                
            data["last_kill"] = new_kills[0]["killmail_id"]

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

                ship_name = await get_type_name(session, ship_type_id)
                system_name = await get_system_name(session, system_id)
                pilot_name = await get_character_name(session, character_id)
                corp_name = await get_corp_name(session, corp_id)
                alliance_name = await get_alliance_name(session, alliance_id)
                total_value = kill["zkb"].get("totalValue", 0)
                title_embed = f"**{pilot_name}** perdió una **{ship_name}** en `{system_name}`"

                if pilot_name == "":
                    title_embed = f"**{corp_name}** perdió una **{ship_name}** en `{system_name}`"

                embed = discord.Embed(
                    title=title_embed,
                    url= f"https://zkillboard.com/kill/{km_id}/",
                    color=discord.Color.red()
                )
                # /zkill 2120527651 1
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
                embed.set_thumbnail(url=f"https://images.evetech.net/types/{ship_type_id}/render?size=128")

                for channel_id in data["channels"]:
                    channel = bot.get_channel(channel_id)
                    if channel:
                        await channel.send(embed=embed)

@fetch_kills.before_loop
async def before_fetch():
    await bot.wait_until_ready()