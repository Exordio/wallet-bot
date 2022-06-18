from os import getenv

from db import on_user_join, on_user_exit, on_user_move, on_user_mute, on_user_unmute, on_user_afk, on_user_unafk
from core import client


@client.event
async def on_voice_state_update(member, before, after):
    with EventStateController(member, before, after, client) as es_instance:
        await es_instance.state_definition()


# may be later change to Mono_state pattern
# and add translations
class EventStateController:
    __AFK_CHANNEL_ID = int(getenv('AFK_CHANNEL_ID'))
    __ADMIN_CHANNEL_ID = int(getenv('ADMIN_CHANNEL_ID'))

    def __init__(self, member, before, after, client):
        self.member = member
        self.before = before
        self.after = after
        self.client = client

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    async def __mute_deaf_check_operation(self):
        if self.after.self_mute or self.after.self_deaf:
            await self.__user_n_found(await on_user_mute(self.member, self.after))
        elif (self.before.self_mute or self.before.self_deaf) and \
                not self.after.self_mute and not self.after.self_deaf:
            await on_user_unmute(self.member, self.after)

    async def __user_n_found(self, state):
        if state == 'UNF':
            ad_ch_instance = self.client.get_channel(self.__ADMIN_CHANNEL_ID)
            await ad_ch_instance.send(
                f'Невозможно подсчитать валюту для юзера {self.member.name} | {self.member.id}'
                f' по причине отсутствия каких либо операций начала отсчёта.')

    async def state_definition(self):
        # Человек зашёл в канал. Признак: в self.before нет информации о канале. В self.after она есть.
        if self.before.channel is None and self.after.channel is not None:
            print(f'{self.member.name} зашёл в канал {self.after.channel}')
            await on_user_join(self.member, self.after)

            # пока хардкод, потом вынести в env, если юзер в афк канал перешёл
            if self.after.channel.id == self.__AFK_CHANNEL_ID:
                print(f'{self.member.name} зашёл в AFK канал')
                await self.__user_n_found(await on_user_afk(self.member, self.after))
                return

            # сюда можно встроить проверку, а не в муте ли чувак которые пришёл
            # Мут микры и абсолютный мут считаем одним и тем же
            await self.__mute_deaf_check_operation()
            return

        # если юзер перешёл из одного канала в другой. Или совершил какое то действие в канале.
        if self.before.channel is not None and self.after.channel is not None:
            if self.after.channel.id == self.__AFK_CHANNEL_ID:
                print(f'{self.member.name} перешел из {self.before.channel} в AFK канал')
                await self.__user_n_found(await on_user_afk(self.member, self.after))
                return
            # тут смысл в том совпадают ли каналы или нет.
            if self.before.channel.id == self.__AFK_CHANNEL_ID:
                print(f'{self.member.name} перешёл из AFK канала в {self.after.channel}')
                await on_user_unafk(self.member, self.after)
            if self.before.channel != self.after.channel:
                print(f'{self.member.name} перешел из канала {self.before.channel} в {self.after.channel}')
                await on_user_move(self.member, self.after)

            else:
                print(f'{self.member.name} совершил действие в канале {self.before.channel}')

            await self.__mute_deaf_check_operation()
            return

        # если чувак вышел
        if self.before.channel is not None and self.after.channel is None:
            print(f'{self.member.name} вышел из канала {self.before.channel}')
            await self.__user_n_found(await on_user_exit(self.member, self.before))
