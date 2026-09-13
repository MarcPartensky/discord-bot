from config.config import access, cluster, prefix
from models.mongo import MongoCollection, MongoDatabase, Post
from config import emoji
from discord.ext import commands
import discord
import inspect


class Item(Post):
    """Shop item."""


def ensure_shop(func):
    async def decorated(self, ctx: commands.Context, *args, **kwargs):
        """Il faut être dans une boutique."""
        if ctx.author.id in self.shop_dict:
            return await func(self, ctx, *args, **kwargs)
        else:
            msg = (
                f"{emoji.warning}Vous devez d'abord vous rendre dans une boutique!"
                f"\nPour cela utiliser la commande: `{prefix}shopping [nom]`."
                f"\nPour voir la liste des boutiques: `{prefix}boutiques`."
            )
            return await ctx.send(msg)
        decorated.__doc__ = func.__doc__
        decorated.__name__ = func.__name__
        decorated.__signature__ = inspect.signature(func)

    return decorated


class Shop(commands.Cog):
    # in a soon future, everyone will be able to sell items
    # for now its only for admins
    # and it's only for commands
    def __init__(self, bot):
        self.bot = bot
        self.shop_dict = {}
        self.shops: MongoDatabase = cluster.shops
        self.item_color = discord.Color.dark_green()
        self.collection_color = discord.Color.dark_blue()
        self.database_color = discord.Color.dark_red()

    @commands.command(name="boutique", aliases=["shop"])
    async def shop(self, ctx: commands.Context, *, name: str = None):
        """Choisi la boutique pour le shopping."""
        if not name:
            await self.get_shop(ctx)
        else:
            await self.set_shop(ctx, name)

    async def get_shop(self, ctx: commands.Context):
        """Affiche la boutique courante."""
        if ctx.author.id not in self.shop_dict:
            msg = "Vous n'êtes dans aucune boutique."
        else:
            shop = self.shop_dict[ctx.author.id]
            msg = f"Vous êtes dans la boutique **{shop.name}**."
        return await ctx.send(msg)

    async def set_shop(self, ctx: commands.Context, name: str):
        """Choisi la boutique courante."""
        if not name in self.shops.collection_names():
            msg = "Cette boutique n'existe pas."
            return await ctx.send(msg)
        self.shop_dict[ctx.author.id] = self.shops[name]
        msg = f"Vous êtes dans la boutique **{name}**."
        return await ctx.send(msg)

    @commands.command(name="boutiques", aliases=["shops"])
    async def shops(self, ctx: commands.Context):
        """Affiche les boutiques disponibles."""
        names = self.shops.collection_names()
        msg = "\n".join(names)
        return await ctx.send(msg)

    @commands.command(name="créer-boutique")
    @access.admin
    async def create_shop(self, ctx: commands.Context, name: str):
        """Créer une boutique."""
        shop = self.shops[name]
        msg = f"Uen nouvelle boutique du nom de {shop.name} a été ouverte."
        return await ctx.send(msg)

    @commands.command("jeter")
    @access.admin
    async def delete(self, ctx: commands.Context, name: str):
        """Supprime un item."""
        shop = self.shop_dict[ctx.author.id]
        try:
            shop.find_one_and_delete(name)
            msg = "Item jeté avec succès."
        except:
            msg = "Item introuvable."
        await ctx.send(msg)

    @commands.command(name="vendre")
    @ensure_shop
    @access.admin
    async def sell(self, ctx: commands.Context, name: str, price: int):
        """Vend un item."""
        shop = self.shop_dict[ctx.author.id]
        item = shop[name]
        item.price = int(price)
        msg = f"{name} se vend maintenant à {price}."
        await ctx.send(msg)

    @commands.command(name="prix")
    @ensure_shop
    async def price(self, ctx: commands.Context, name: str):
        """Affiche le prix d'un item."""
        shop = self.shop_dict[ctx.author.id]
        item = shop[name]
        msg = f"{name} se vend à {item.price}."
        await ctx.send(msg)

    @commands.command(name="items")
    @ensure_shop
    async def items(self, ctx: commands.Context):
        """Liste tous les items du rayon."""
        shop = self.shop_dict[ctx.author.id]
        lines = []
        for post in shop.find({}):
            post = Post(post)
            line = f"> {post._id}:{post.price}{emoji.euro}"
            lines.append(line)
        msg = "\n".join(lines)
        print("les items")
        await ctx.send(msg)

    @commands.command(name="item")
    @ensure_shop
    async def item(self, ctx: commands.Context, name: str):
        """Affiche un item et ses informations."""
        shop = self.shop_dict[ctx.author.id]
        item = shop[name]
        embed = self.embed_item(item)
        await ctx.send(embed=embed)

    def embed_item(self, item):
        """Return an embed for an item."""
        embed = discord.Embed(title=item.name, color=self.item_color)
        for k, v in item.items():
            embed.add_field(name=k, value=v)
        return embed

    def embed_shop(self, shop):
        """Return an embed for a shop."""
        embed = discord.Embed(title=item.name, color=self.item_color)
        for k, v in item.items():
            embed.add_field(name=k, value=v)
        return embed

    def embed_shops(self, shops):
        """Return an embed for shops."""
        pass


def setup(bot):
    bot.add_cog(Shop(bot))
