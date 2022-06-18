import discord

from discord import app_commands
from dotenv import load_dotenv
from os import getenv

load_dotenv()

MY_GUILD = discord.Object(id=getenv('MY_SHINY_GUILD'))


class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)


intents = discord.Intents.default()
client = MyClient(intents=intents)
