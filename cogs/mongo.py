# from config.credentials import mongo_url

from discord.ext import commands, tasks
import discord

from config.config import db, access
from utils.tools import for_all_cog_methods

# print('mongo_url:', mongo_url)


# db = cluster['esclave']
# collection = db['memory']

# @for_all_cog_methods(access.cog_admin)
class Mongo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = db
        self.collection = None

    @commands.command(name='mg-collections')
    @access.admin
    async def list_collection_names(self, ctx:commands.Context):
        """Liste les noms des collections."""
        names = ', '.join(self.db.list_collection_names())
        await ctx.send(f"Les collections sont: {names}.")

    @commands.command(name='mg-setcollection')
    @access.admin
    async def set_collection(self, ctx:commands.Context, *, name:str):
        """Choisi une collection."""
        self.collection = self.db[name]
        await ctx.send(f"La collection {self.collection.name} est sélectionnée.")

    @commands.command(name="mg-insert-one")
    @access.admin
    async def insert_one(self, ctx:commands.Context, id:str, *, value:str):
        """Ajoute des posts dans mongo."""
        post = {id: value}
        self.collection.insert_one(post)
        await ctx.send(f"Le post {id}:{value} est inséré dans {self.collection.name}.")

    @commands.command(name="mg-update-one")
    @access.admin
    async def update_one(self, ctx:commands.Context, id:str, *, value:str):
        """Mets à jour des posts dans mongo."""
        post = {id: value}
        self.collection.update_one(post)
        await ctx.send(f"{id}:{value} mis à jour dans {self.collection.name}.")

    @commands.command(name="mg-find-one")
    @access.admin
    async def find_one(self, ctx:commands.Context, *, conditions:str):
        """Trouve un post dans mongo."""
        conditions = conditions.split(',')
        conditions = dict([string.strip() for string in condition.strip().split('=')] for condition in conditions)
        post = self.collection.find_one(conditions)
        await ctx.send(f"Trouvé: {post}.")

    @commands.command(name="mg-find")
    @access.admin
    async def find(self, ctx:commands.Context, *, conditions:str):
        """Trouve des posts dans mongo."""
        conditions = conditions.split(',')
        conditions = dict([string.strip() for string in condition.strip().split('=')] for condition in conditions)
        posts = list(self.collection.find(conditions))
        await ctx.send(f"Trouvé: {posts}.")    

    # @on_command_error
    # async def cog_command_error(self, ctx, error):
    #     """Renvoie une réponse en cas d'erreur."""
        # await ctx.send(error)

    

def setup(bot):
    mongo = Mongo(bot)
    # print(mongo.find.help)
    print('mro in setup:', Mongo.__mro__)
    print('mro in setup:', type(mongo).__mro__)
    bot.add_cog(mongo)