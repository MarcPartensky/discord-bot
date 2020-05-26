from config.config import access, cluster
from models.mongo import MongoCollection, MongoDatabase, Post
from discord.ext import commands
import discord

class Item(Post):
    """Shop item."""

class Shop(commands.Cog):
    #in a soon future, everyone will be able to sell items
    #for now its only for admins
    #and it's only for commands
    def __init__(self, bot):
        self.bot = bot
        self.shops = {}
        self.shop:MongoDatabase = cluster.shop
        self.aisle:MongoCollection = None

    def getShops(self, id):
        """Renvoie les boutiques disponibles pour un utilisateur."""
        pass

    @commands.command("rayon")
    @access.admin
    async def aisle(self, ctx:commands.Context, *, aisle:str):
        """Choisi la collection d'items."""
        if aisle: self.aisle = self.shop[aisle]
        if self.aisle:
            msg = f"Vous êtes dans le rayon {self.aisle.name}."
        else:
            msg = f"Ce rayon n'existe pas en magasin."
        await ctx.send(msg)

    @commands.command("jeter")
    @access.admin
    async def delete(self, ctx:commands.Context, id):
        """Supprime un item."""
        try:
            self.aisle.find_one_and_delete(id)
            msg = "Item jeté avec succès."
        except:
            msg = "Item introuvable."
        await ctx.send(msg)

    @commands.command("vendre")
    @access.admin
    async def sell(self, ctx:commands.Context, id, price:int):
        """Vend un item."""
        item = self.aisle[id]
        if not item:
            item = self.createNewItem(id, price)
        self.aisle.post(item)
        msg = f"{id} se vend maintenant à {price}."
        await ctx.send(msg)

    @commands.command("items")
    @access.admin
    async def items(self, ctx:commands.Context):
        """Liste tous les items du rayon."""
        lines = []
        for post in self.aisle.find():
            line = str(post)
            lines.append(line)
        msg = '\n'.join(lines)
        await ctx.send(msg)


def setup(bot):
    bot.add_cog(Shop(bot))
