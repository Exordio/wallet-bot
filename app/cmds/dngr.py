from db import truncate_wallets as tw, truncate_activity as ta, truncate_all as tall
from core import discord, app_commands, client
from func.comm import wrapped_launch

# DANGER SECTION

danger_group = app_commands.Group(name='danger', description='hell')


@danger_group.command()
async def truncate_wallets(interaction: discord.Interaction):
    """Очистка кошельков."""

    state = await wrapped_launch(interaction, tw)

    if not state:
        return

    await interaction.response.send_message(f'Очистка кошельков успешно выполнена!')


@danger_group.command()
async def truncate_activity(interaction: discord.Interaction):
    """Очистка активностей."""
    state = await wrapped_launch(interaction, ta)

    if not state:
        return

    await interaction.response.send_message(f'Очистка активности успешно выполнена!')


@danger_group.command()
async def truncate_all(interaction: discord.Interaction):
    """Очистка всего."""
    state = await wrapped_launch(interaction, tall)

    if not state:
        return

    await interaction.response.send_message(f'Полная очистка успешно выполнена!')


client.tree.add_command(danger_group)

# DANGER SECTION END
