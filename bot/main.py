import discord
from discord.ext import commands
import requests
from django.conf import settings
import json

TOKEN = settings.DISCORD_TOKEN

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)

# Bot commands

@bot.command(name='clear_messages')
async def clear_messages(ctx):
    await ctx.channel.purge()



def start_bot():
    bot.run(TOKEN)

