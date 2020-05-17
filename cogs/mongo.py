from config.credentials import mongo_url

from discord.ext import commands, tasks
import discord

from config.config import cluster

db = cluster['esclave']
collection = db['memory']

class Mongo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(name="insert-mongo")
    async def insert_mongo(self, ctx:commands.Context, key:str, *, value:str):
        """Ajoute des valeurs dans mongo."""
        post = {key: value}
        await ctx.send(post)
        collection.insert_one(post)
        await ctx.send(f"{key}:{value} enregistré sur mongo")

    @commands.command(name="update-mongo")
    async def update_mongo(self, ctx:commands.Context, key:str, *, value:str):
        """Modifie des valeurs dans mongo."""
        post = {key: value}
        await ctx.send(post)
        collection.update_one(post)
        await ctx.send(f"{key}:{value} modifié sur mongo")

def setup(bot):
    bot.add_cog(Mongo(bot))