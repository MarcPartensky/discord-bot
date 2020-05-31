from config.config import access, cluster, prefix
from models.mongo import MongoCollection, MongoDatabase, Post
from discord.ext import commands
import discord
from config import emoji

class Item(Post):
    """Shop item."""

def ensure_shop(func):
    async def decorated(self, ctx:commands.Context, *args, **kwargs):
        """Il faut être dans une boutique."""
        if ctx.author.id in self.shop_dict:
            print("yes")
            return await func(self, ctx, *args, **kwargs)
        else:
            msg = (f"{emoji.warning}Vous devez d'abord vous rendre dans une boutique!"
                f"\nPour cela utiliser la commande: `{prefix}shopping [nom]`."
                f"\nPour voir la liste des boutiques: `{prefix}boutiques`."
            )
            return await ctx.send(msg)
    return decorated


class Shop(commands.Cog):
    #in a soon future, everyone will be able to sell items
    #for now its only for admins
    #and it's only for commands
    def __init__(self, bot):
        self.bot = bot
        self.shop_dict = {}
        self.shops:MongoDatabase = cluster.shops
        self.item_color = discord.Color.dark_green()
        self.collection_color = discord.Color.dark_blue()
        self.database_color = discord.Color.dark_red()


    @commands.command(name="boutique", aliases=['shop'])
    async def shop(self, ctx:commands.Context, *, name:str=None):
        """Choisi la boutique pour le shopping."""
        if not name:
            await get_shop(ctx)
        else:
            await set_shop(ctx, name)

    async def get_shop(self, ctx:commands.Context):
        """Affiche la boutique courante."""
        shop = self.get_shop(ctx)
            if not shop:
                msg = "Vous n'êtes dans aucune boutique."
                return await ctx.send(msg)

    async def set_shop(self, ctx:commands.Context, name:str):
        """Choisi la boutique courante."""
        if not name in self.shops.collection_names():
            msg = "Cette boutique n'existe pas."
            return await ctx.send(msg)
        self.shop_dict[ctx.author.id] = self.shops[name]
        msg = f"Vous êtes dans la boutique **{name}**."
        return await ctx.send(msg)

    @commands.command(name="boutiques")
    async def shops(self, ctx:commands.Context):
        """Affiche les boutiques disponibles."""
        names = self.shops.collection_names()
        msg = '\n'.join(names)
        return await ctx.send(msg)

    def get_shop(self, ctx:commands.Context):
        """Renvoie sa boutique courante."""
        id = ctx.author.id
        return self.shop_dict[id]

    @commands.command("jeter")
    @access.admin
    async def delete(self, ctx:commands.Context, name:str):
        """Supprime un item."""
        shop = self.get_shop(ctx)
        try:
            shop.find_one_and_delete(name)
            msg = "Item jeté avec succès."
        except:
            msg = "Item introuvable."
        await ctx.send(msg)

    @commands.command(name="vendre")
    @ensure_shop
    @access.admin
    async def sell(self, ctx:commands.Context, name:str, price:int):
        """Vend un item."""
        shop = self.get_shop(ctx)
        item = shop[name]
        item.price = price
        msg = f"{name} se vend maintenant à {price}."
        await ctx.send(msg)

    @commands.command(name="prix")
    @ensure_shop
    async def price(self, ctx:commands.Context, name:str):
        """Affiche le prix d'un item."""
        shop = self.get_shop(ctx)
        item = shop[name]
        msg = f"{name} se vend à {item.price}."
        await ctx.send(msg)

    @commands.command(name="items")
    @ensure_shop
    async def items(self, ctx:commands.Context):
        """Liste tous les items du rayon."""
        shop = self.get_shop(ctx)
        lines = []
        for post in shop.find({}):
            post = Post(post)
            line = post._id
            lines.append(str(line))
        msg = '\n'.join(lines)
        print('les items')
        await ctx.send(msg)

    @commands.command(name="item")
    @ensure_shop
    async def item(self, ctx:commands.Context, name:str):
        """Affiche un item et ses informations."""
        shop = self.get_shop(ctx)
        item = shop[name]
        embed = self.embed_item(item)
        await ctx.send(embed=embed)

    def embed_item(self, item):
        """Return an embed for an item."""
        embed = discord.Embed(title=item.name, color=self.item_color)
        for k,v in item.items():
            embed.add_field(name=k, value=v)
        return embed

    def embed_shop(self, shop):
        """Return an embed for a shop."""
        embed = discord.Embed(title=item.name, color=self.item_color)
        for k,v in item.items():
            embed.add_field(name=k, value=v)
        return embed

    def embed_shops(self, shops):
        """Return an embed for shops."""
        pass





def setup(bot):
    bot.add_cog(Shop(bot))
