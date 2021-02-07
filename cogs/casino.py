from config.config import access, delete_after_time, masters
from models.mongocollection import MongoCollection
from config import emoji
from utils import tools

from discord.ext import commands, tasks
from config.config import cluster
import discord
import random
import time
import datetime


class Casino(commands.Cog):
    @property
    def account_defaults(self):
        return dict(coins=self.coins_starter, creation=time.time(), time=time.time())

    def __init__(self, bot, **kwargs):
        self.bot = bot
        self.max_chips = 5
        self.casino = cluster.casino
        self.accounts = self.casino.accounts
        self.transactions = self.casino.transactions
        self.max_coins = 200
        self.coins_starter = 50
        self.refill_coins = 10
        self.refill_wait_time = 24 * 60 * 60  # 1 day

    @property
    def users(self):
        return cluster.users

    async def cog_before_invoke(self, ctx: commands.Context):
        await self.connect(ctx)

    @commands.group(name="casino", aliases=["csn"])
    async def casino(self, ctx: commands.Context):
        """Groupe de commandes du casino."""
        if not ctx.invoked_subcommand:
            await ctx.send(
                "> Commande invalide."
                f"\n> Tapez `{ctx.bot.command_prefix}help casino` pour voir les commandes disponibles."
            )

    @casino.command(name="claim")
    async def claim(self, ctx: commands.Context):
        """Claime les coins quotidiens."""
        account = self.accounts[ctx.author.id]
        if time.time() - account.time > self.refill_wait_time:
            self.refill(ctx)
            await self.coins(ctx)
        else:
            await ctx.send("> Vous devez attendre la recharge.")
            await self.time_before_refill(ctx)

    @casino.command(name="coins")
    async def coins(self, ctx: commands.Context, member: discord.Member = None):
        """Affiche son nombre de coins."""
        member = member or ctx.author
        account = self.accounts[member.id]
        if member == ctx.author:
            msg = f"> Vous avez **{account.coins}** coins au casino."
        else:
            msg = f"> **{member.name}** a **{account.coins}** au casino."
        await ctx.send(msg)

    @casino.command(name="temps")
    async def time_before_refill(
        self,
        ctx: commands.Context,
    ):
        """Affiche son nombre de coins."""
        account = self.accounts[ctx.author.id]
        seconds = int(self.refill_wait_time - (time.time() - account.time))
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)
        msg = f"> Encore "
        if days:
            msg += f"**{days}** jours, "
        if hours:
            msg += f"**{hours}** heures, "
        if minutes:
            msg += f"**{minutes}** minutes "
        if seconds:
            msg += f"et **{seconds}** secondes"
        msg += " avant la recharge."
        await ctx.send(msg)

    @casino.command(name="chiffre")
    async def find_the_digit(self, ctx: commands.Context, n: int, bet: int = 1):
        """Deviner un chiffre entre 0 et 9."""
        account = self.accounts[ctx.author.id]
        if account.coins < bet:
            await ctx.send(f"> Vous n'avez pas assez de coins pour miser **{bet}**.")
            return
        r = random.randint(0, 9)
        if n == r:
            account.coins += 10 * bet
            await ctx.send(f"> Vous gagnez **{10*bet}** coins.")
        else:
            account.coins -= bet
            await ctx.send(f"> Vous perdez **{bet}** coins.")

    @casino.command(name="compte", aliases=["account"])
    async def account(self, ctx: commands.Context, member: discord.Member = None):
        """Affiche un compte de casino."""
        member = member or ctx.author
        account = self.accounts[member.id]
        embed = discord.Embed(title=member.name, color=member.color)
        embed.set_thumbnail(url=member.avatar_url)
        for k, v in account.items():
            embed.add_field(name=k, value=v)
        await ctx.send(embed=embed)

    @casino.command(name="vendre", aliases=["sell"])
    async def sell(
        self, ctx: commands.Context, coins: int = None, member: discord.Member = None
    ):
        """Vend les coins pour de l'argent."""
        member = member or ctx.author
        if member != ctx.author and ctx.author.id not in masters:
            msg = f"> Vous ne pouvez pas vendre les coins de **{member.name}**."
            return await ctx.send(msg)
        user_account = self.users.accounts[member.id]
        casino_account = self.casino.accounts[member.id]
        if coins:
            if coins > casino_account.coins:
                msg = f"> **{member.name}** n'a pas assez de coins."
                return await ctx.send(msg)
        else:
            coins = casino_account.coins
        casino_account.coins -= coins
        user_account.money += coins
        await ctx.send(f"> Vente de **{coins}** coins effectuée.")

    @casino.command(name="coins=")
    @access.admin
    async def set_coins(
        self, ctx: commands.Context, coins: int, member: discord.Member = None
    ):
        """Choisi les coins d'un membre."""
        member = member or ctx.author
        self.casino.accounts[member.id].coins = coins
        await self.coins(ctx, member)

    @casino.command(name="coins+=")
    @access.admin
    async def add_coins(
        self, ctx: commands.Context, coins: int, member: discord.Member = None
    ):
        """Ajoute des coins à un membre."""
        member = member or ctx.author
        self.casino.accounts[member.id].coins += coins
        await self.coins(ctx, member)

    @casino.command(name="coins-=")
    @access.admin
    async def remove_coins(
        self, ctx: commands.Context, coins: int, member: discord.Member = None
    ):
        """Retire des coins à un membre."""
        member = member or ctx.author
        self.casino.accounts[member.id].coins -= coins
        await self.coins(ctx, member)

    async def connect(self, ctx):
        """Vérife compte et refill."""
        account = self.accounts[ctx.author.id]
        self.update(account)

    def update(self, account):
        account.setdefaults(**self.account_defaults)

    def refill(self, ctx: commands.Context):
        """Rajoute des coins régulièrement."""
        account = self.accounts[ctx.author.id]
        account.coins += self.refill_coins
        account.time = time.time()

    def get_account(self, user_id):
        """Renvoie un compte."""
        account = self.accounts[user_id]
        self.update(account)
        return account


def setup(bot):
    bot.add_cog(Casino(bot))
