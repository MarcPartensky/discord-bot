from models.mongocollection import MongoCollection
from config.config import cluster,access
from config import emoji

from discord.ext import commands, tasks
import discord

import time


class Users(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot
        self.users = cluster.users
        self.info = self.users.info
        self.accounts = self.users.accounts
        self.starter_wallet_size = 1000
        self.starter_wallet_money = 5

    @property
    def defaults(self):
        """Renvoie les champs des utilisateurs par défaults."""
        return dict(
            creation = time.time(),
            use = 0,
            last_use = time.time(),
            money = 0,
            xp = 0,
            messages = 0,
        )


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
        """Affiche les informations d'un membre."""
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
        user = member or ctx.author
        account = self.accounts[user.id]
        self.update(account)
        if ctx.author==user:
            msg = f"Vous avez **{account.money}** {emoji.euro} dans votre portefeuille."
        else:
            msg = f"{user.name} a **{account.money}** {emoji.money} dans son portefeuille."
        await ctx.send(msg)

    @commands.command(name='portefeuille=')
    @access.admin
    async def set_wallet(self, ctx:commands.Context, money:int, member:discord.Member=None):
        """Choisi l'argent d'un utilisateur."""
        user = member or ctx.author
        account = self.accounts[user.id]
        self.update(account)
        account.money = money
        if ctx.author==user:
            msg = f"Vous avez maintenant **{account.money}** {emoji.euro} dans votre portefeuille."
        else:
            msg = f"{user.name} a maintenant **{account.money}** {emoji.money} dans son portefeuille."
        await ctx.send(msg)

    @commands.command()
    async def xp(self, ctx:commands.Context, member:discord.Member=None):
        """Affiche l'expérience d'un utilisateur."""
        user = member or ctx.author
        account = self.accounts[user.id]
        self.update(account)
        if ctx.author==user:
            msg = f"Vous avez **{account.xp}** {emoji.xp}."
        else:
            msg = f"{user.name} a **{account.xp}** {emoji.xp}."
        await ctx.send(msg)

    @commands.command(name='xp=')
    @access.admin
    async def set_xp(self, ctx:commands.Context, xp:int, member:discord.Member=None):
        """Choisi l'xp d'un utilisateur."""
        user = member or ctx.author
        account = self.accounts[user.id]
        self.update(account)
        account.xp = xp
        if ctx.author==user:
            msg = f"Vous avez maintenant **{account.xp}** {emoji.xp}."
        else:
            msg = f"{user.name} a maintenant **{account.xp}** {emoji.xp}."
        await ctx.send(msg)


    @commands.command(name="dernier-message")
    async def last_message(self, ctx:commands.Context, member:discord.Member=None):
        """Affiche votre dernier message."""
        user = member or ctx.author
        account = self.accounts[user.id]
        id = account.last_message
        msg = "Dernier message introuvable."
        for channel in self.bot.get_all_channels():
            try:
                if isinstance(channel, discord.channel.TextChannel):
                    msg = await channel.fetch_message(id)
                    break
            except Exception as e:
                print(e)
        await ctx.send("> "+msg.content)

    @wallet.before_invoke
    @me.before_invoke
    async def connect(self, ctx:commands.Context, member:discord.Member=None):
        """Connecte un utilisateur à son compte."""
        user = member or ctx.author
        account = self.accounts[user.id]
        self.update(account)

    def update(self, account):
        """Met à jour un compte utilisateur."""
        account.setdefaults(self.defaults)
        account.use += 1
        account.last_use = time.time()

    @commands.Cog.listener()
    async def on_message(self, msg:discord.Message):
        """Détecte les messages des utilisateurs et incrémente l'xp."""
        if msg.author.bot: return
        account = self.accounts[msg.author.id]
        account.setdefaults(xp=0)
        account.xp += 1
        account.setdefaults(messages=0)
        account.messages += 1
        account.last_message = msg.id

    @commands.command(name="augmente-xp")
    async def increase_xp(self, user:discord.user):
        """Augmente l'expérience d'un utilisateur."""
        account.setdefaults(xp=0)
        account.xp += 1


def setup(bot):
    bot.add_cog(Users(bot))
