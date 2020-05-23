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
    def __init__(self, bot, **kwargs):
        # commands.Cog.__init__(self, **kwargs)
        # MongoCollection.__init__(self, type(self).__name__)
        self.bot = bot
        self.max_chips = 5
        self.casino = cluster.casino
        self.accounts = self.casino.accounts
        self.transactions = self.casino.transactions
        self.bank = cluster.bank
        # self.bank = self.bot.get_cog("Bank")
        self.coins_starter = 50
        self.refill_coins = 10
        self.refill_wait_time = 24*60*60 #1 day


    @commands.command(name='vendre-coins')
    async def sell_coins(self, ctx:commands.Context):
        """Vends les coins pour de l'argent."""
        await ctx.send("Vos coins ont été échangés.")

    @commands.command(name='coins')
    async def coins(self, ctx:commands.Context,):
        """Affiche son nombre de coins."""
        account = self.accounts[ctx.author.id]
        msg = f"Vous avez {account.coins} coins au casino."
        await ctx.send(msg)

    @commands.command(name='temps-refill')
    async def time_before_refill(self, ctx:commands.Context,):
        """Affiche son nombre de coins."""
        account = self.accounts[ctx.author.id]
        seconds = int(self.refill_wait_time - (time.time() - account.time))
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)
        msg = f"Encore "
        if days:
            msg += f"{days} jours, "
        if hours:
            msg += f"{hours} heures, "
        if minutes:
            msg += f"{minutes} minutes "
        if seconds:
            msg += f"et {seconds} secondes"
        msg += " avant le refill."
        await ctx.send(msg)

    @commands.command(name='trouve-chiffre')
    async def find_the_digit(self, ctx:commands.Context, bet:int):
        """Deviner un chiffre entre 0 et 9."""
        account = self.accounts[ctx.author.id]
        coins = account.coins
        if coins<bet:
            await ctx.send(f"Vous n'avez pas assez de coins pour miser {bet}.")
            return
        n = random.randint(0, 9)
        if n==bet:
            account.coins += 10*bet
            await ctx.send(f"Vous gagnez {10*bet} coins.")
        else:
            account.coins -= bet
            await ctx.send(f"Vous perdez {bet} coins.")
        self.accounts.post(ctx.author.id, account)

    @commands.command(name='compte-casino')
    async def account(self, ctx:commands.Context,):
        """Affiche son compte de casino."""
        account = self.accounts[ctx.author.id]
        msg = '\n'.join([f"{k}:{v}" for k,v in account.items()])
        await ctx.send(msg)

    @time_before_refill.before_invoke
    @find_the_digit.before_invoke
    async def connect(self, ctx):
        """Vérife compte et refill."""
        account = self.accounts[ctx.author.id]
        if not account:
            self.accounts[ctx.author.id] = {'coins': self.coins_starter, 'creation':time.time(), 'time':time.time()}
        else:
            if time.time()-account.time>self.refill_wait_time:
                self.refill(ctx)

    def refill(self, ctx):
        """Rajoute des coins régulièrement."""
        self.accounts.update_one({'_id':ctx.author.id}, {'$inc': {'coins':self.refill_coins}})


def setup(bot):
    bot.add_cog(Casino(bot))
