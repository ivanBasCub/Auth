import discord

# Esta bien creado
class FacilitiesView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

        select = discord.ui.Select(
            placeholder="Selecciona una estación",
            min_values=1,
            max_values=1,
            options=[
                discord.SelectOption(label="Estación 1", description="Descripción de la estación 1", value="station_1"),
                discord.SelectOption(label="Estación 2", description="Descripción de la estación 2", value="station_2"),
                discord.SelectOption(label="Estación 3", description="Descripción de la estación 3", value="station_3"),
            ]
        )

        # Asignar el callback
        select.callback = self.select_callback

        # Añadir el select a la vista
        self.add_item(select)

    async def select_callback(self, interaction: discord.Interaction):
        # Obtiene el valor seleccionado
        selected_value = interaction.data["values"][0]
        await interaction.response.send_message(f"Has seleccionado: {selected_value}", ephemeral=True)
