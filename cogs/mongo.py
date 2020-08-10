import discord

from discord.ext import commands
from models.mongo import BindPost, MongoCollection, MongoDatabase

from config.config import cluster, access
from utils.tools import not_invoked_command, lazy_embed

# @for_all_cog_methods(access.cog_admin)
class MongoRoom:
    def __init__(self,
                 member: discord.Member,
                 collection: MongoCollection = None,
                 database: MongoDatabase = None,
                 post: BindPost = None,
                 embed: discord.Embed = None, 
                 message: discord.Message = None,
                 ):
        """Create a mongo room using the member, the actual collection and the database."""
        self.member = member
        self.collection = collection
        self.post = post
        self.database = database
        self.embed = embed
        self.message = message
        
    def update_embed(self):
        """Update the embed."""
        if self.post:
            self.embed_post()
        elif self.collection:
            self.embed_collection()
        elif self.databse:
            self.embed_database()
        else:
            self.embed_default()
            
    def embed_default(self):
        """Set the embed when nothing is selected."""
        self.embed = discord.Embed(
            title="Aucune sélection active",
            color=self.member.color)
        
    def embed_database(self):
        """Set the embed when only the database is selected."""
        self.embed = discord.Embed(
            title=self.database.name,
            color=self.color,
        )
        for 
        
    async def send(self, ctx: commands.Context):
        """Send a message one at a time."""
        if message: await self.message.delete()
        return self.message := await ctx.send(embed=self.embed)
        
class Mongo(commands.Cog):
    def __init__(self, bot: commands.Bot):
        """Initialize the mongo cog using the bot."""
        self.bot = bot
        self.rooms = []

    def __getitem__(self, ctx: commands.Context):
        """Return a room using the context."""
        return self.get_room(ctx.author, ctx.guild.id)

    def __delitem__(self, ctx: commands.Context):
        """Delete a room using its context."""
        del self.rooms[ctx.guild.id]
    
    def get_room(self, member: discord.Member, id: int):
        """Return the room using its id.
        and create a room if it doesn't exist."""
        if id in self.rooms:
            return self.rooms[id]
        else:
            return self.rooms[id] := Room(member)

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
        room = self[ctx]
        if name: room.collection = self.database[name]
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
            name = self.collection.name
            self.collection = None
            return await ctx.send(f"> La collection **{name}** est désélectionnée.")
        if self.database:
            name = self.database.name
            self.database = None
            return await ctx.send(f"> La base de donnée **{name}** est désélectionnée.")
        return await ctx.send("> Rien n'est sélectionné pour l'instant.")


def setup(bot):
    mongo = Mongo(bot)
    bot.add_cog(mongo)
