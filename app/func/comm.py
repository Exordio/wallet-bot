from core import discord, getenv


async def wrapped_launch(interaction: discord.Interaction, func: any, params: dict = None, need_return: bool = False):
    try:
        if need_return:
            return await func() if params is None else await func(**params)

        await func() if params is None else await func(**params)
        return True
    except Exception as err:
        print('We have error in command module: ')
        print(err)
        await interaction.response.send_message(
            f"Произошла ошибка! Не расстраивайся. :) Зови <@{getenv('OPERATOR_ID')}> смотреть логи.")
        return False
