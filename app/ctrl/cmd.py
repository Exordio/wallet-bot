from typing import Optional

from core import client, discord, app_commands, getenv

# from cmds.dngr import *
from cmds.fins import *


@client.tree.command()
@app_commands.describe(
    member='Пользователь на которого вы хотите посмотреть.')
async def joined(interaction: discord.Interaction, member: Optional[discord.Member] = None):
    """Сообщает когда пользователь присоединился в канал. Можно выбрать другого пользователя."""
    member = member or interaction.user

    await interaction.response.send_message(f'<@{member.id}> присоединился {discord.utils.format_dt(member.joined_at)}')
