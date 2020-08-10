import discord

from discord.ext import commands, tasks
from models.mongo import Post, MongoCollection, MongoDatabase

from config.config import cluster, access
from utils.tools import for_all_cog_methods, not_invoked_command

# @for_all_cog_methods(access.cog_admin)
class Mongo(commands.Cog):
    def __init__(self, bot: commands.Bot):
        """Initialize the mongo cog using the bot."""
        self.bot = bot
        self.database:MongoDatabase = None
        self.collection:MongoCollection = None
        self.post_color = discord.Color.dark_green()
        
    @commands.group(aliases=['mg'])
    async def mongo(self, ctx: commands.Context):
        """Groupe de commandes pour gérer un cluster mongo."""
        if not ctx.invoked_subcommand:
            return await not_invoked_command(ctx, 'mongo')
            
        # await ctx

    @commands.command(name='mg-collections')
    @access.admin
    async def list_collection_names(self, ctx:commands.Context):
        """Liste les noms des collections."""
        names = ', '.join(self.database.list_collection_names())
        await ctx.send(f"Les collections sont: {names}.")

    @commands.command(name='mg-setcollection')
    @access.admin
    async def set_collection(self, ctx:commands.Context, *, name:str=None):
        """Choisi une collection."""
        if name:
            self.collection = self.database[name]
        else:
            self.collection = None
        await ctx.send(f"La collection {self.collection.name} est sélectionnée.")

    @commands.command(name='mg-databases')
    @access.admin
    async def list_database_names(self, ctx:commands.Context):
        """Liste les bases de données."""
        names = ', '.join(cluster.list_database_names())
        await ctx.send(f"Les base de données sont: {names}.")

    @commands.command(name='mg-setdatabase')
    @access.admin
    async def set_database(self, ctx:commands.Context, *, name:str=None):
        """Choisi une collection."""
        if name:
            self.database = cluster[name]
        else:
            self.database = None
        await ctx.send(f"La base de donnée {self.database.name} est sélectionnée.")

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

    # @commands.command(name="mg-find-one")
    # @access.admin
    # async def find_one(self, ctx:commands.Context, *, conditions:str):
    #     """Trouve un post dans mongo."""
    #     conditions = conditions.split(',')
    #     conditions = dict([string.strip() for string in condition.strip().split('=')] for condition in conditions)
    #     post = self.collection.find_one(conditions)
    #     title = f"Trouvé: {post._id}."
    #     embed = self.lazy_embed(title, self.post_color, post)
    #     await ctx.send(embed=embed)

    @commands.command(name="mg-delete-one")
    @access.admin
    async def delete_one(self, ctx:commands.Context, *, conditions:str):
        """Trouve un post dans mongo."""
        conditions = conditions.split(',')
        conditions = dict([string.strip() for string in condition.strip().split('=')] for condition in conditions)
        # try:
        print(conditions)
        self.collection.find_and_delete_one(conditions)
        msg = f"Document supprimé."
        # except Exception as e:
        #     print(e)
        #     msg = f"Document introuvable."
        await ctx.send(msg)

    def lazy_embed(self, title, color, d):
        """Lazy embed a dictionary."""
        embed = discord.Embed(title=title, color=color)
        for k,v in d.items():
            embed.add_field(name=k, value=v)
        return embed

    @commands.command(name="mg-find-one")
    @access.admin
    async def find_one(self, ctx:commands.Context, *, conditions:str):
        """Trouve des posts dans mongo."""
        conditions = conditions.split(',')
        conditions = dict([string.strip() for string in condition.strip().split('=')] for condition in conditions)
        post = self.collection.find_one(conditions)
        embed = self.lazy_embed(post._id, self.post_color, post)
        await ctx.send(embed=embed)

    @commands.command(name="mg-find")
    @access.admin
    async def find(self, ctx:commands.Context, *, conditions:str):
        """Trouve des posts dans mongo."""
        conditions = conditions.split(',')
        conditions = dict([string.strip() for string in condition.strip().split('=')] for condition in conditions)
        for post in self.collection.find(conditions):
            post = Post(post)
            embed = self.lazy_embed(post._id, self.post_color, post)
            await ctx.send(embed=embed)

    @commands.command(name="mg-find-all")
    @access.admin
    async def find_all(self, ctx:commands.Context, n:int=10):
        """Trouve des posts dans mongo."""
        for post in self.collection.find({}, limit=n):
            post = Post(post)
            embed = self.lazy_embed(post._id, self.post_color, post)
            await ctx.send(embed=embed)

    @commands.command(name="mg-back")
    @access.admin
    async def back(self, ctx:commands.Context):
        """Fait un retour en arrière."""
        if self.collection:
            self.collection = None
            return await ctx.send("La collection est désélectionnée.")
        if self.database:
            self.database = None
            return await ctx.send("La base de donnée est désélectionnée.")
        return await ctx.send("Rien n'est sélectionné pour l'instant.")

    # @on_command_error
    # async def cog_command_error(self, ctx, error):
    #     """Renvoie une réponse en cas d'erreur."""
        # await ctx.send(error)
    

def setup(bot):
    mongo = Mongo(bot)
    bot.add_cog(mongo)