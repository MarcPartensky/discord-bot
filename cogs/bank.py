from config.config import access, cluster, check, masters
from models.mongo import Post

from discord.ext import commands
import discord

import datetime
import time

class Bank(commands.Cog):
    class NotEnoughMoney(Exception):
        def __init__(self, user):
            super().__init__(f"{user.name} n'a pas assez d'argent.")
    class NoAccount(Exception):
        def __init__(self, user):
            super().__init__(f"{user.name} n'a pas de compte en banque.")

    def __init__(self, bot):
        self.bot = bot
        self.bank = cluster.bank
        self.accounts = self.bank.accounts
        self.starter_money = 10
        self.never = "jamais"
        self.troll_message = "Vous y avez vraiment cru? mdr"

    async def has_bank_account(self, ctx:commands.Context, member:discord.Member):
        """Assure l'existence d'un compte."""
        account = self.accounts[member.id]
        return await self.is_bank_account(ctx, account, member)

    async def is_bank_account(self, ctx:commands.Context, account, member:discord.Member):
        """Détermine si un compte bancaire est valide."""
        if not account:
            if ctx.author==member:
                msg = "Vous n'avez pas ouvert de compte bancaire."
            else:
                msg = f"{member.name} n'a pas ouvert de compte bancaire."
            await ctx.send(msg)
            return False
        return True
        
    async def has_enough_money(self, ctx:commands.Context, account, pay:int):
        """Assure la capacité de payer."""
        if account.money < pay:
            if ctx.author==user:
                msg = "Vous n'avez pas assez d'argent."
            else:
                msg = f"{user.name} n'a pas assez d'argent."
            await ctx.send(msg)
            return False
        return True

    @commands.command(name="choisir-argent", aliases=["argent="])
    async def set_money(self, ctx:commands.Context, member:discord.Member):
        """Choisi l'argent d'un compte bancaire."""
        member = member or ctx.author
        if await self.has_bank_account(ctx, member):
            pass


    @commands.command(name="migrer-banque")
    @access.admin
    async def migrate(self, ctx:commands.Context):
        """Migre banque de sqlite vers mongodb."""
        await ctx.send("En attente")

    @commands.command(name="code-bancaire")
    async def bank_code(self, ctx:commands.Context, member:discord.Member):
        """Donne le code bancaire d'un membre."""
        msg = f"Le code bancaire de {member.name} est ||{self.troll_message}||"
        await ctx.send(msg)

    @commands.command(name="comptes-bancaires")
    @access.admin
    async def bank_accounts(self, ctx:commands.Context):
        """Informe sur un compte bancaire."""
        cursor = list(self.accounts.find())
        if len(cursor)==0:
            msg = "Personne n'a ouvert de compte en banque."
            return await ctx.send(msg)
        for post in cursor:
            account = Post(post)
            msg = self.describe_account(account)
            await ctx.send(msg)

    @commands.command(name="compte-bancaire")
    async def bank_account(self, ctx:commands.Context, member:discord.Member=None):
        """Informe sur un compte bancaire."""
        member = member or ctx.author
        account = self.accounts[member.id]
        if await self.is_bank_account(ctx, account, member):
            msg = self.describe_account(account, member)
            await ctx.send(msg)

    def describe_account(self, account, user:discord.Member=None):
        """Décrit un compte bancaire."""
        user = user or self.bot.get_user(account._id)
        creation = datetime.datetime.fromtimestamp(int(account.creation))
        if account.withdrawed:
            withdrawed_time = datetime.datetime.fromtimestamp(int(account.withdrawed_time))
        else:
            withdrawed_time = self.never
        if account.saved:
            saved_time = datetime.datetime.fromtimestamp(int(account.saved_time))
        else:
            saved_time = self.never
        lines = [
            f"Informations bancaire de **{user.name}**:",
            f"compte de `{user.name}`",
            f"crée le `{creation}`",
            f"a retiré de l'argent `{account.withdrawed}` fois",
            f"dont la dernière fois le `{withdrawed_time}`",
            f"a placé de l'argent `{account.saved}` fois",
            f"dont la dernière fois le `{saved_time}`"
        ]
        msg = "\n  - ".join(lines)
        return msg

    @commands.command(name="compte-bancaire-brute", hidden=True)
    async def raw_bank_account(self, ctx:commands.Context, user:discord.Member=None):
        """Informe sur un compte bancaire."""
        user = ctx.author or user
        account = self.accounts[user.id]
        if await self.has_bank_account(ctx, user):
            lines = [f"Informations bancaire de {user.name}:"]
            lines += [f"{k} : {v}"  for k,v in account.items()]
            msg = "\n  - ".join(lines)
            await ctx.send(msg)

    @commands.command(name="ouvrir-compte")
    async def open_account(self, ctx:commands.Context, member:discord.Member=None):
        """Ouvre un compte en banque."""
        member = member or ctx.author
        if ctx.author!=member and not ctx.author.id in masters:
            return await ctx.send("Vous n'êtes pas autorisés à ouvrir le compte de cette personne.")
        account = self.accounts[member.id]
        if post:
            if ctx.author==member:
                msg = "Vous avez déjà un compte en banque."
            else:
                msg = f"{member.name} a déjà un compte en banque."
            return await ctx.send(msg)
        post = Post(
            _id = ctx.author.id,
            money = self.starter_money,
            creation = time.time(),
            withdrawed = 0,
            withdrawed_time = None,
            saved = 0,
            saved_time = None,
        )
        self.accounts.post(post)
        if ctx.author==member:
            await ctx.send("Votre compte est ouvert.")
        else:
            await ctx.send(f"Un compte au nom de {member.name} a été ouvert.")

    @commands.command(name="fermer-compte", aliases=['supprimer-compte'])
    async def close_account(self, ctx:commands.Context, member:discord.Member=None):
        """Ferme un compte en banque."""
        member = member or ctx.author
        if ctx.author!=member and not ctx.author.id in masters:
            await ctx.send(f"Vous n'êtes pas autorisés à fermer le compte de {member.name}.")
            return
        post = self.accounts.find_one({'_id':member.id})
        if not post:
            if member==ctx.author:
                await ctx.send("Vous n'avez pas de compte.")
            else:
                await ctx.send(f"{member.name} n'as pas de compte.")
            return
        if member==ctx.author:
            await ctx.send("Votre compte a été trouvé. "
                "Êtes-vous sur de vouloir le supprimer?")
        else:
            await ctx.send(f"Le compte de {member.name} a été trouvé. "
                "Êtes-vous sur de vouloir le supprimer?")
        success = await check.wait_for_check(ctx)
        if not success:
            return
        self.accounts.delete_one({'_id':member.id})
        if member==ctx.author:
            await ctx.send("Votre compte a été supprimé.")
        else:
            await ctx.send(f"{member.name} a été supprimé.")

    @commands.command(name="argent")
    async def money(self, ctx:commands.Context, member:discord.User=None):
        """Affiche l'argent d'un compte bancaire."""
        member = member or ctx.author
        account = self.accounts[member.id]
        if not account:
            if member==ctx.author:
                msg = "Vous n'avez pas ouvert de compte."
            else:
                msg = f"{member.name} n'a pas ouvert de compte."
        else:
            if member==ctx.author:
                msg = f"Vous avez {account.money} d'argent en banque."
            else:
                msg = f"{member.name} a {account.money} d'argent en banque."
        return await ctx.send(msg)

def setup(bot):
    bot.add_cog(Bank(bot))