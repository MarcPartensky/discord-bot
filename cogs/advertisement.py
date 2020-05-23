from config.config import cluster, access, check
from models.mongo import Post
from utils.check import Check
from utils import tools

from discord.ext import commands
import discord

import time

class Advertisement(commands.Cog):
    """Fais de la publicité moyennant rémunération."""
    def __init__(self, bot):
        self.bot = bot
        self.advertisement = cluster.advertisement
        self.accounts = self.advertisement.accounts
        self.prices = self.advertisement.prices
        self.users = cluster.users
        # await self.create_prices()

    @commands.command(name="prix-pub")
    async def prices(self, ctx:commands.Context):
        """Affiche les prix des pubs."""
        posts = self.prices.find()
        lines = []
        for post in posts:
            post = Post(post)
            line = f"L'offre {post._id} coûte {post.price}."
            lines.append(line)
        txt = '\n'.join(lines)
        await ctx.send(txt)

    @commands.command(name="pub")
    async def pub(self, ctx:commands.Context):
        """Fais de la pub moyennant paiement."""
        post = self.prices['pub']
        if not post:
            return await ctx.send("Cette offre est indisponible pour le moment.")
        msg = f"En effectuant cette action vous consentez à payer {post.price}."
        success = await check.wait_for_check(ctx)
        if not success: return
        await ctx.send(msg)

    # @commands.command('cr')
    # await def create_prices(self):
    #     """Crée les prix pour les publicités."""
    #     pass

    @commands.command(name="choisir-prix")
    @access.admin
    async def set_price(self, ctx:commands.Context, name:str, price:int):
        """Choisi le prix pour une pub."""
        post = self.prices.find_one({'_id':name})
        if not post:
            post = Post(
                    _id=name,
                    price=price,
                    author=ctx.author.id,
                    creation=time.time(),
                    time=time.time()
                )
            self.prices.insert_one(post)
        else:
            post.price = price
            post.time = time.time()
            self.prices.replace_one({'_id':name}, post)
        await ctx.send(f"Le prix de {name} est maintenant à {price}.")








def setup(bot):
    bot.add_cog(Advertisement(bot))