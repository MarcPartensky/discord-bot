import discord

from discord.ext import commands


class MongoRoom:
    def __init__(self,
                 member: discord.Member,
                 collection: MongoCollection = None,
                 database: MongoDatabase = None,
                 post: BindPost = None,
                 message: discord.Message = None,
                 ):
        """Create a mongo room using the member, the actual collection and the database."""
        self.member = member
        self.collection = collection
        self.post = post
        self.database = database
        self.message = message
        
    @property
    def path(self):
        """Return the path selected in the mongo cluster."""
        path_list = []
        if self.database:
            path_list.append(self.database.name)
        if self.collection:
            path_list.append(self.collection.name)
        if self.post:
            path_list.append(self.post.id)
        return '/'.join(path_list)
        
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
            return self.embed_default()
            
    def embed_default(self):
        """Set the embed when nothing is selected."""
        return discord.Embed(
            title="Aucune sélection active",
            description=self.path,
            color=self.member.color)
                
    def embed_database(self):
        """Set the embed only when the database is selected."""
        embed = discord.Embed(
            title=self.database.name,
            description=self.path,
            color=self.color,
        )
        for k,v in self.database.items():
            embed.add_field(name=k, value=v)
        return embed
            
    def embed_collection(self):
        """Set the embed when the collection and the database
        are selected."""
        embed = discord.Embed(
            title=self.collection.title,
            description=self.path,
            color=self.color,
        )
        for k,v in self.collection.items():
            embed.add_field(name=k, value=v)
        return embed
    
    def embed_post(self):
        """Set the embed when the post, the collection and the
        database are selected."""
        embed = discord.Embed(
            title=self.post.id,
            description=self.path,
            color=self.color
        )
        for k,v in self.post.items():
            embed.add_field(name=k, value=v)
        return embed
        
    async def send(self, ctx: commands.Context):
        """Send a message one at a time."""
        if self.message: await self.message.delete()
        self.message = await ctx.send(embed=self.embed)
        return self.message
        # return (self.message := await ctx.send(embed=self.embed))


class Mongo(commands.Cog):
    """Catégorie qui permet de naviguer au sein d'un cluster de mongo db."""
    
    def __init__(self, rooms:dict={}):
        """Initialise la catégorie mongo avec le dictionnaire des salons."""
        self.rooms = rooms
        
    def __getitem__(self, ctx: commands.Context):
        """Return a room using the context."""
        self.get_room(ctx.guild.id, ctx.author)
        
    def __delitem__(self, ctx: commands.Context):
        """Delete a room using the context."""
        del self.rooms[ctx.guild.id]
        
    def get_room(self, id: int, member: discord.Member):
        """Return a room using the id and the discord member."""
        self.rooms[id] = Room(member)
        return self.rooms[id]
        
    @commands.group(aliases=['mg'])
    def mongo(self, ctx: commands.Context):
       """Groupe de commandes mongo."""
       room = self[ctx]
       await room.send(ctx)


def setup(bot):
    """Setup the cog."""
    bot.add_cog(Mongo(bot))