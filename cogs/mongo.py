import discord
import asyncio

from discord.ext import commands
from config.config import access, cluster
from models.mongo import MongoDatabase, MongoCollection, BindPost
from config import emoji


class MongoRoom:
    def __init__(self,
                 member: discord.Member,
                 selection: int = 0,
                 collection: MongoCollection = None,
                 database: MongoDatabase = None,
                 post: BindPost = None,
                 message: discord.Message = None,
                 timeout = 5*60, # in seconds
                 ):
        """Create a mongo room using the member, the actual collection and the database."""
        self.member = member
        self.selection  = selection
        self.collection = collection
        self.post = post
        self.database = database
        self.message = message
        self.timeout = timeout
        
    @property
    def path(self):
        """Return the path selected in the mongo cluster."""
        path_list = []
        if self.database:
            path_list.append(self.database.name)
        if self.collection:
            path_list.append(self.collection.name)
        if self.post:
            path_list.append(self.post._id)
        return path_list
        
    @path.setter
    def path(self, path_list: list):
        """Set the path of the room."""
        if len(path_list) >= 1:
            self.database = cluster[path_list[0]]
        else:
            self.database = None
        if len(path_list) >= 2:
            self.collection = self.database[path_list[1]]
        else:
            self.collection = None
        if len(path_list) >= 3:
            self.post = self.collection[path_list[2]]
        else:
            self.post = None
            
    @path.deleter
    def path(self):
        """Tricky way to set the path to empty."""
        self.database = None
        self.collection = None
        self.post = None
        
    @property
    def embed(self):
        """Update the embed."""
        if self.post:
            return self.embed_post()
        elif self.collection:
            return self.embed_collection()
        elif self.database:
            return self.embed_database()
        else:
            return self.embed_cluster()
            
    def embed_cluster(self):
        """Set the embed when nothing is selected."""
        embed = discord.Embed(
            title='cluster',
            description='/'.join(self.path),
            color=self.member.color)
        for i, k in enumerate(cluster.list_database_names()):
            v = cluster[k]
            if i == self.selection:
                k = f"> __{k}__"
            embed.add_field(name=k, value=f"{len(v)} collections")
        return embed
                
    def embed_database(self):
        """Set the embed only when the database is selected."""
        embed = discord.Embed(
            title=self.database.name,
            description='/'.join(self.path),
            color=self.member.color,
        )
        for i, (k,v) in enumerate(self.database.items()):
            if i == self.selection:
                k = f"> __{k}__"
            embed.add_field(name=k, value=f"{len(v)} posts")
        return embed
            
    def embed_collection(self):
        """Set the embed when the collection and the database
        are selected."""
        embed = discord.Embed(
            title=self.collection.name,
            description='/'.join(self.path),
            color=self.member.color,
        )
        for i, (k,v) in enumerate(self.collection.items()):
            if i == self.selection:
                k = f"> __{k}__"
            embed.add_field(name=k, value=f"{len(v)} items")
        return embed
    
    def embed_post(self):
        """Set the embed when the post, the collection and the
        database are selected."""
        embed = discord.Embed(
            title=str(self.post._id),
            description='/'.join(map(str, self.path)),
            color=self.member.color
        )
        # print('items', self.post.items())
        for i, (k,v) in enumerate(self.post.items()):
            if i == self.selection:
                k = f"> __{k}__"
            embed.add_field(name=k, value=str(v))
        return embed
        
    async def show(self, ctx: commands.Context):
        """Send a message one at a time."""
        if self.message: await self.message.delete()
        self.message = await ctx.send(embed=self.embed)
        return await self.add_reactions(ctx)
            
    async def add_reactions(self, ctx):
        """Add the reactions. Bad design."""
        await self.message.add_reaction(emoji.previous)
        await self.message.add_reaction(emoji.play)
        await self.message.add_reaction(emoji.next)
        await self.message.add_reaction(emoji.back)
        await self.message.add_reaction(emoji.scissors)
        await self.message.add_reaction(emoji.trash)
        reactions = [emoji.previous, emoji.play, emoji.next, emoji.back, emoji.trash]
        while True:
            try:
                reaction, user = await ctx.bot.wait_for(
                    'reaction_add', timeout=self.timeout, check=lambda r,u:not u.bot)
                if user != ctx.author:
                    await ctx.send(
                        "Vous n'êtes pas autorisés à effectuer cette action.")
                await reaction.remove(user)
                if reaction.emoji == emoji.back:
                    self.path = self.path[:-1]
                    return True
                elif reaction.emoji == emoji.play:
                    self.select()
                    return True
                elif reaction.emoji == emoji.previous:
                    self.selection = (self.selection + len(self) - 1) % len(self)
                    await self.message.edit(embed=self.embed)
                elif reaction.emoji == emoji.next:
                    self.selection = (self.selection + 1) % len(self)
                    await self.message.edit(embed=self.embed)
                elif reaction.emoji == emoji.scissors:
                    self.delete_selection()
                    return True
                elif reaction.emoji == emoji.trash:
                    return False
            except asyncio.exceptions.TimeoutError:
                return False
            
    async def delete(self):
        """Delete the messages when the room is deleted."""
        await self.message.delete()
        
    def __len__(self):
        """Return the length of the selected object in the room."""
        if self.post:
            return len(self.post)
        elif self.collection:
            return len(self.collection)
        elif self.database:
            return len(self.database)
        else:
            return len(cluster.list_database_names())
        
    def select(self):
        """Select the object selected in the room."""
        if self.post:
            pass
        elif self.collection:
            self.post = self.collection[self.collection.find()[self.selection]['_id']]
        elif self.database:
            self.collection = self.database[self.database.list_collection_names()[self.selection]]
        else:
            self.database = cluster[cluster.list_database_names()[self.selection]]
        self.selection = 0
        
    def delete_selection(self):
        """Delete the object selected in the room."""
        if self.post:
            keys = list(self.post.keys())
            del self.post[keys[self.selection]]
        elif self.collection:
            del self.collection[self.collection.find()[self.selection]['_id']]
        elif self.database:
            del self.database[self.database.list_collection_names()[self.selection]]
        else:
            del cluster[cluster.list_database_names()[self.selection]]
        self.selection = 0
        

class Mongo(commands.Cog):
    """Catégorie qui permet de naviguer au sein d'un cluster de mongo db."""
    
    def __init__(self, bot: commands.Bot, rooms:dict={}):
        """Initialise la catégorie mongo avec le dictionnaire des salons."""
        self.bot = bot
        self.rooms = rooms

    def __getitem__(self, ctx: commands.Context) -> MongoRoom:
        """Return a room using the context."""
        return self.get_room(ctx.guild.id, ctx.author)
        
    def __delitem__(self, ctx: commands.Context):
        """Delete a room using the context."""
        del self.rooms[ctx.guild.id]
        
    def get_room(self, id: int, member: discord.Member):
        """Return a room using the id and the discord member."""
        if id not in self.rooms:
            self.rooms[id] = MongoRoom(member)
        return self.rooms[id]
        
    @commands.group(aliases=['mg'])
    async def mongo(self, ctx: commands.Context):
       """Groupe de commandes mongo."""
       if not ctx.invoked_subcommand:
        await self.show(ctx)

    @mongo.command(name='afficher', aliases=['a', 'show'])
    @access.admin
    async def show(self, ctx: commands.Context):
        """Affiche un salon mongo."""
        room = self[ctx]
        keeping = True
        while keeping:
            keeping = await room.show(ctx)
            if not keeping:
                await room.delete()
                del self[ctx]

    @mongo.command(name='sélectionner', aliases=['=', 'select'])
    async def select(self, ctx: commands.Context, *path: str):
        """Sélectionne un chemin mongo."""
        room = self[ctx]
        room.path = path
        room.selection = 0
        await self.show(ctx)
        
    @mongo.command(name="chemin", alises=['path'])
    async def path(self, ctx: commands.Context):
        """Affiche le chemin dans le cluster mongo."""
        room = self[ctx]
        text_path = '/'.join(room.path)
        await ctx.send(f"> {text_path}")


def setup(bot):
    """Setup the cog."""
    bot.add_cog(Mongo(bot))
