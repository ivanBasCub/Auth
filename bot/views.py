import discord
from discord.ext import commands

class FacilitiesView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.select(
        placeholder="Selecciona una estación",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(label="Estación 1", description="Descripción de la estación 1", value="station_1"),
            discord.SelectOption(label="Estación 2", description="Descripción de la estación 2", value="station_2"),
            discord.SelectOption(label="Estación 3", description="Descripción de la estación 3", value="station_3"),
        ]
    )
    async def select_callback(self, select, interaction):
        await interaction.response.send_message(f"Has seleccionado: {select.values[0]}", ephemeral=True)