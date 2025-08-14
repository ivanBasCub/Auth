import discord
from discord.ext import commands
from django.conf import settings

TOKEN = settings.DISCORD_TOKEN

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)

def start_bot():
    bot.run(TOKEN)


# Bot commands
secret_role = "DeathWatch"

@bot.command(name='clear_messages')
async def clear_messages(ctx):
    await ctx.channel.purge()

# Asignar de manera manual un rol
@bot.command()
async def assign_role(ctx):
    role = discord.utils.get(ctx.guild.roles, name=secret_role)
    if role:
        await ctx.author.add_roles(role)
        await ctx.send(f"{ctx.author.mention} ha subido a {secret_role}")
    else:
        await ctx.send("Role doesn't exists")


@bot.command()
async def remove_role(ctx):
    role = discord.utils.get(ctx.guild.roles, name=secret_role)
    if role:
        await ctx.author.remove_roles(role)
        await ctx.send(f"{ctx.author.mention} / {secret_role}")
    else:
        await ctx.send("Role doesn't exists")

@bot.command()
async def dm(ctx, *, msg):
    await ctx.author.send(f"Hola {msg}")
    await ctx.reply("Hola")



