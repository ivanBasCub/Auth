import discord
from discord.ext import commands
from dotenv import load_dotenv
import importlib
import logging
import os

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
COMMANDS_DIR = os.path.join(os.path.dirname(__file__), "commands")

handler = logging.FileHandler(filename="discord.log", encoding='utf-8', mode="w")
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='/', intents=intents)

# Command Loader
for filename in os.listdir(COMMANDS_DIR):
    if filename.endswith(".py"):
        filepath = os.path.join(COMMANDS_DIR, filename)
        spec = importlib.util.spec_from_file_location(filename[:-3], filepath)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if hasattr(module, "register"):
            module.register(bot)
    
@bot.event
async def on_ready():
    print(f"Hello World, {bot.user.name}")
    bot.zkill_init()
    
bot.run(TOKEN,log_handler=handler, log_level=logging.DEBUG)