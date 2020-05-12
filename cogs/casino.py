from config.config import access, status, delete_after_time, masters
from models.database import Database
from config import emoji
from utils import tools

from discord.ext import commands, tasks
import discord
import random
import time


class Casino(commands.Cog, Database):
    def __init__(self, bot, path, **kwargs):
        commands.Cog.__init__(self, **kwargs)
        Database.__init__(self, path)
        self.bot = bot
        self.max_chips = 5
        self.bank = self.bot.get_cog("Bank")


def setup(bot):
    from os.path import join, dirname, abspath
    path = join(dirname(dirname(abspath(__file__))), 'database/casino.db')

    bot.add_cog(Casino(bot, path=path))