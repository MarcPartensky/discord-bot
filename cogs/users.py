from models.mongocollection import MongoCollection

from discord.ext import commands, tasks
import discord


class Users(commands.Cog):
    def __init__(self, bot, collection):
        self.bot = bot
        self.collection = collection

    # @commands.command()
    # def update_user(self, ctx:commansd)


def setup(bot):
    collection = MongoCollection("Users")
    bot.add_cog(Users(bot, collection))
