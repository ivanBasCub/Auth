import os
import discord
from discord.ext import commands
import importlib 
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
COMMANDS_DIR = os.path.join(os.path.dirname(__file__), "commands")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event 
async def on_ready(): 
    print(f"Bot conectado como {bot.user.name}")
    
    
# Command List
for filename in os.listdir(COMMANDS_DIR):
    if filename.endswith(".py"):
        filepath = os.path.join(COMMANDS_DIR, filename)
        spec = importlib.util.spec_from_file_location(filename[:-3], filepath)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if hasattr(module, "register"):
            module.register(bot)

if __name__ == "__main__": 
    if TOKEN is None: 
        raise ValueError("DISCORD_TOKEN no está definido en el entorno") 
    bot.run(TOKEN)