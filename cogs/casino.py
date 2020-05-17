from config.config import access, delete_after_time, masters
from models.mongocollection import MongoCollection
from config import emoji
from utils import tools

from discord.ext import commands, tasks
import discord
import random
import time

class Casino(commands.Cog, MongoCollection):
    def __init__(self, bot, **kwargs):
        # commands.Cog.__init__(self, **kwargs)
        # MongoCollection.__init__(self, type(self).__name__)
        self.bot = bot
        self.max_chips = 5
        # self.bank = self.bot.get_cog("Bank")

    @commands.command
    def find_the_number(self, ctx:commands.Context, n:int):
        """Jeu ou il faut deviner le nombre."""
        pass


def setup(bot):
    # bot.add_cog(Casino(bot))
    pass