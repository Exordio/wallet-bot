from ctst.vls import __REASON_ADMIN_CHANGING, __COIN_ROUND_INT_VALUE
from core import discord, app_commands, client, getenv
from db import get_user_balance, append_user_balance, perm_change_balance, get_users_balance_top
from func.comm import wrapped_launch


# FINANCES SECTION

@client.tree.command()
async def my_balance(interaction: discord.Interaction):
    """Мой баланс на данном сервере."""

    user_balance = await wrapped_launch(interaction, get_user_balance,
                                        {'member': interaction.user},
                                        True)

    if user_balance is False:
        return

    user_balance = round(user_balance, __COIN_ROUND_INT_VALUE)

    await interaction.response.send_message(f"Твой баланс: **{user_balance} {getenv('COIN_NAME')}**")


@client.tree.command()
@app_commands.describe(
    user='Пользователь канала.'
)
async def see_balance(interaction: discord.Interaction, user: discord.Member):
    """Посмотреть баланс пользователя на сервере."""
    user_balance = await wrapped_launch(interaction, get_user_balance,
                                        {'member': user},
                                        True)

    if user_balance is False:
        return

    user_balance = round(user_balance, __COIN_ROUND_INT_VALUE)

    await interaction.response.send_message(
        f"Баланс пользователя <@{user.id}> : **{user_balance} {getenv('COIN_NAME')}**")


@client.tree.command()
@app_commands.rename(user='пользователь', value='значение')
@app_commands.describe(
    user='Пользователь канала.',
    value='Смена значения валюты.'
)
async def spell_bal(interaction: discord.Interaction, user: discord.Member, value: float):
    """Добавить или убавить валюту у пользователя."""

    state = await wrapped_launch(interaction, append_user_balance,
                                 {'member': user, 'value': value, 'reason': __REASON_ADMIN_CHANGING})

    if not state:
        return

    await interaction.response.send_message(
        f"Успешно выполнено. Пользователю <@{user.id}> начислено **{value} {getenv('COIN_NAME')}**")


@client.tree.command()
@app_commands.rename(user='пользователь', value='значение')
@app_commands.describe(
    user='Пользователь канала.',
    value='Новое значение валюты.'
)
async def perm_change_bal(interaction: discord.Interaction, user: discord.Member, value: float):
    """Изменить баланс у пользователя. Перманентно применяет новое значение."""

    state = await wrapped_launch(interaction, perm_change_balance,
                                 {'member': user, 'value': value, 'reason': __REASON_ADMIN_CHANGING})

    if not state:
        return

    await interaction.response.send_message(
        f"Успешно выполнено. Пользователю <@{user.id}> изменён баланс : **{value} {getenv('COIN_NAME')}**")


@client.tree.context_menu(name='Баланс пользователя')
async def watch_balance(interaction: discord.Interaction, member: discord.Member):
    user_balance = await wrapped_launch(interaction, get_user_balance,
                                        {'member': member},
                                        True)

    if user_balance is False:
        return

    user_balance = round(user_balance, __COIN_ROUND_INT_VALUE)

    await interaction.response.send_message(
        f"Баланс пользователя <@{member.id}> : **{user_balance} {getenv('COIN_NAME')}**")


@client.tree.command()
async def wallets_top(interaction: discord.Interaction):
    """Вывод самых топовых кошельков на сервере. :)"""
    balance_top = await wrapped_launch(interaction, get_users_balance_top, need_return=True)

    if balance_top is False:
        return

    if len(balance_top) == 0:
        await interaction.response.send_message(
            f"На данный момент не существует ни одного кошелька.")

    top = '**Вывод самых топовых кошельков на сервере: **\n'

    for wallet in balance_top:
        top += f"\n **{round(float(wallet['bal']), __COIN_ROUND_INT_VALUE)} {getenv('COIN_NAME')}** : <@{wallet['user_id']}>"

    await interaction.response.send_message(top)

# FINANCES SECTION END
