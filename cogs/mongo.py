import discord

from discord.ext import commands
from models.mongo import Post, MongoCollection, MongoDatabase

from config.config import cluster, access
from utils.tools import not_invoked_command, lazy_embed

# @for_all_cog_methods(access.cog_admin)


class Mongo(commands.Cog):
    def __init__(self, bot: commands.Bot):
        """Initialize the mongo cog using the bot."""
        self.bot = bot
        self.database: MongoDatabase = None
        self.collection: MongoCollection = None
        self.post_color = discord.Color.dark_green()

    @commands.group(aliases=['mg'])
    async def mongo(self, ctx: commands.Context):
        """Groupe de commandes pour gérer un cluster mongo."""
        if not ctx.invoked_subcommand:
            return await not_invoked_command(ctx, 'mongo')

    @mongo.command(name='collections', aliases=['cls'])
    async def list_collection_names(self, ctx: commands.Context):
        """Liste les noms des collections."""
        names: list = self.database.list_collection_names()
        if self.collection:
            names.remove(self.collection.name)
            names.insert(0, f"**{names.pop(self.collection.name)}**")
        text = '\n'.join(map(lambda s: f"> - {s}", names))
        await ctx.send(f"**Les collections sont**:\n{text}")

    @mongo.group(aliases=['cl'])
    async def collection(self, ctx: commands.Context):
        """Groupe de commandes des collections mongo."""
        if not ctx.invoked_subcommand:
            return await not_invoked_command(ctx, 'mongo collection')

    @collection.command(name='choisir', aliases=['='])
    @access.admin
    async def collection_set(self, ctx: commands.Context, *, name: str = None):
        """Choisi une collection."""
        if name:
            self.collection = self.database[name]
        await ctx.send(f"> La collection **{self.collection.name}** est sélectionnée.")

    @collection.command(name="supprimer", aliases=[''])
    @access.admin
    async def collection_delete(self, ctx: commands.Context, *, name: str = None):
        """Supprime une collection."""
        if name:
            collection = self.database[name]
        else:
            collection = self.collection
        name = collection.name
        del collection
        await ctx.send(f"> La collection **{name}** est supprimée.")

    @mongo.command(name='databases', aliases=['dbs'])
    @access.admin
    async def list_database_names(self, ctx: commands.Context):
        """Liste les bases de données."""
        names: list = cluster.list_database_names()
        if self.database:
            names.remove(self.database.name)
            names.insert(0, f"**{self.database.name}**")
        text = '\n'.join(map(lambda s: f"> - {s}", names))
        await ctx.send(f"> **Les base de données sont**:\n{text}")

    @mongo.group(aliases=['db'])
    async def database(self, ctx: commands.Context):
        """Groupe de commandes des bases de données mongo."""
        if not ctx.invoked_subcommand:
            await not_invoked_command(ctx, 'mongo database')

    @database.command(name='choisir', aliases=['='])
    @access.admin
    async def database_set(self, ctx: commands.Context, *, name: str = None):
        """Choisi une collection."""
        if name:
            self.database = cluster[name]
        await ctx.send(f"> La base de donnée **{self.database.name}** est sélectionnée.")

    @mongo.group(aliases=['p'])
    async def post(self, ctx: commands.Context):
        """Groupe de commandes des posts mongos."""
        if not ctx.invoked_subcommand:
            await not_invoked_command(ctx, 'mongo post')

    @post.command(name="insert-one")
    @access.admin
    async def insert_one(self, ctx: commands.Context, id: str, *, value: str):
        """Ajoute des posts dans mongo."""
        post = {id: value}
        self.collection.insert_one(post)
        await ctx.send(f"Le post {id}:{value} est inséré dans {self.collection.name}.")

    @post.command(name="update-one")
    @access.admin
    async def update_one(self, ctx: commands.Context, id: str, *, value: str):
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

    @post.command(name="delete-one")
    @access.admin
    async def delete_one(self, ctx: commands.Context, *, conditions: str):
        """Trouve un post dans mongo."""
        conditions = conditions.split(',')
        conditions = dict([string.strip() for string in condition.strip().split(
            '=')] for condition in conditions)
        self.collection.find_and_delete_one(conditions)
        await ctx.send("> Document supprimé.")

    @post.command(name="find-one")
    @access.admin
    async def find_one(self, ctx: commands.Context, *, conditions: str):
        """Trouve des posts dans mongo."""
        conditions = conditions.split(',')
        conditions = dict([string.strip() for string in condition.strip().split(
            '=')] for condition in conditions)
        post = self.collection.find_one(conditions)
        embed = lazy_embed(post._id, self.post_color, post)
        await ctx.send(embed=embed)

    @post.command(name="find")
    @access.admin
    async def find(self, ctx: commands.Context, *, conditions: str):
        """Trouve des posts dans mongo."""
        conditions = conditions.split(',')
        conditions = dict([string.strip() for string in condition.strip().split(
            '=')] for condition in conditions)
        for post in self.collection.find(conditions):
            post = Post(post)
            embed = lazy_embed(post._id, self.post_color, post)
            await ctx.send(embed=embed)

    @post.command(name="find-all")
    @access.admin
    async def find_all(self, ctx: commands.Context, n: int = 10):
        """Trouve des posts dans mongo."""
        for post in self.collection.find({}, limit=n):
            post = Post(post)
            embed = lazy_embed(post._id, self.post_color, post)
            await ctx.send(embed=embed)

    @mongo.command(name="back")
    @access.admin
    async def back(self, ctx: commands.Context):
        """Fait un retour en arrière."""
        if self.collection:
            self.collection = None
            return await ctx.send("La collection est désélectionnée.")
        if self.database:
            self.database = None
            return await ctx.send("La base de donnée est désélectionnée.")
        return await ctx.send("Rien n'est sélectionné pour l'instant.")


def setup(bot):
    mongo = Mongo(bot)
    bot.add_cog(mongo)
