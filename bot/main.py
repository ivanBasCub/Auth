import os
import discord
import importlib    
from discord.ext import commands
from django.conf import settings
from .views.facilities import FacilitiesView

TOKEN = settings.DISCORD_TOKEN
COMMANDS_DIR = os.path.join(os.path.dirname(__file__), "commands")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)


for filename in os.listdir(COMMANDS_DIR):
    if filename.endswith(".py"):
        filepath = os.path.join(COMMANDS_DIR, filename)
        spec = importlib.util.spec_from_file_location(filename[:-3], filepath)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if hasattr(module, "register"):
            module.register(bot)

# Función para inicar el bot
def start_bot():
    bot.run(TOKEN)
