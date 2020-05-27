from models.mongocollection import MongoCollection
from config.config import cluster,access
from config import emoji

from discord.ext import commands, tasks
import discord

import time


class Users(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.users = cluster.users
        self.info = self.users.info
        self.accounts = self.users.accounts
        self.starter_wallet_size = 1000
        self.starter_wallet_money = 5

    @commands.command(name="moi", aliases=['me'])
    async def me(self, ctx:commands.Context):
        """Affiche mes informations."""
        account = self.accounts[ctx.author.id]
        title = f"Informations sur vous"
        embed = (discord.Embed(title=title, color=0x00ff00)
            .set_thumbnail(url=ctx.author.avatar_url))
        for k,v in account.items():
            embed.add_field(name=k, value=v)
        await ctx.send(embed=embed)

    @commands.command(name="lui", aliases=["elle"])
    async def him(self, ctx:commands.Context, member:discord.Member):
        """Affiche mes informations."""
        await self.connect(ctx, member)
        account = self.accounts[member.id]
        title = f"Informations sur {member.name}"
        embed = (discord.Embed(title=title, color=0x00ff00)
            .set_thumbnail(url=member.avatar_url))
        for k,v in account.items():
            embed.add_field(name=k, value=v)
        await ctx.send(embed=embed)

    @commands.command(name='portefeuille', aliases=['portemonnaie'])
    async def wallet(self, ctx:commands.Context, member:discord.Member=None):
        """Affiche l'argent d'un utilisateur."""
        user = ctx.author or member
        account = self.accounts[user.id]
        msg = f"Vous avez **{account.money}** {emoji.euro} dans votre portefeuille."
        await ctx.send(msg)

    @commands.command(name='portefeuille=')
    @access.admin
    async def set_wallet(self, ctx:commands.Context, money:int, member:discord.Member=None):
        """Affiche l'argent d'un utilisateur."""
        user = ctx.author or member
        account = self.accounts[user.id]
        account.money = money
        msg = f"Vous avez maintenant **{account.money}** {emoji.euro} dans votre portefeuille."
        await ctx.send(msg)

    @wallet.before_invoke
    @me.before_invoke
    async def connect(self, ctx:commands.Context, member:discord.Member=None):
        """Connecte un utilisateur à son compte."""
        user = member or ctx.author
        account = self.accounts[user.id]
        if not account:
            account = self.accounts[user.id]
        account.setdefault('creation', time.time())
        account.setdefault('use', 0)
        account.setdefault('money', 0)
        account.setdefault('xp', 0)
        account.use += 1
        account.last_use = time.time()
        

def setup(bot):
    bot.add_cog(Users(bot))
