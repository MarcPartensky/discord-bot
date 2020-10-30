from config.config import access, cluster, check, masters
from config.errors import *
from models.mongo import Post

from config import emoji
from discord.ext import commands
import discord
import pymongo

import datetime
import time

from models.database import Database
from os.path import join, dirname, abspath
path = join(dirname(dirname(abspath(__file__))), 'database/bank.db')
sqldb = Database(path=path)


class Bank(commands.Cog):
    class Account(Post):
        """Compte bancaire."""
    class Transaction(Post):
        """Transaction bancaire."""

    class Error(Exception):
        def __init__(self, user:discord.User, author:discord.User=None):
            self.user = user
            self.author = author
            self.message = self.tell()
        def tell(self) -> str:
            raise NotImplemented
        def __str__(self):
            return self.message

    class NotEnoughMoney(Error):
        def tell(self):
            if self.author==self.user:
                return "Vous n'avez pas assez d'argent."
            else:
                return f"{self.user.name} n'a pas assez d'argent."
    class NoAccount(Error):
        def tell(self):
            if self.author==self.user:
                return "Vous n'avez pas de compte bancaire."
            else:
                return f"{self.user.name} n'a pas de compte en banque."
    class SelfPayment(Error):
        def tell(self):
            if self.author==self.user:
                return "Vous ne pouvez pas vous payer vous-même."
            else:
                return f"{self.user.name} ne peut pas se payer soi-même."

    def __init__(self, bot:commands.Bot):
        self.bot = bot
        self.bank = cluster.bank
        self.users = cluster.users
        self.accounts = self.bank.accounts
        self.transactions = self.bank.transactions
        self.starter_money = 10
        self.limit = 10
        self.max_limit = 20
        self.never = "jamais"
        self.troll_message = "Vous y avez vraiment cru? mdr"
        # self.gold_color = 0xecce8b #useless with discord.color system
        self.gold_color = discord.Color.gold()

    @property
    def account_defaults(self):
        return dict(
            money = float('inf'),
            creation = time.time(),
            withdrawed = 0,
            withdrawed_time = None,
            saved = 0,
            saved_time = None,
        )

    @commands.command(name="nettoie-compte")
    async def clean_account(self, ctx:commands.Context, member:discord.Member=None):
        """Nettoie les champs inutiles d'un compte.
        Les champs inutiles dans mongo sont supprimés."""
        member = member or ctx.author
        keys = list(self.account_defaults.keys())+['_id']
        account = self.accounts[member.id]
        if 'creation' not in account:
            if ctx.author==member:
                msg = "Vous n'avez pas de compte bancaire."
            else:
                msg = f"{member.name} n'a pas de compte bancaire."
            return await ctx.send(msg)
        for key in account.keys():
            if key not in keys:
                del account[key]
        await ctx.send("Compte bancaire nettoyé.")
    
    @commands.command(name="rendre-riche")
    @access.admin
    async def make_rich(self, ctx:commands.Context, member:discord.Member):
        """Rend un membre infiniment riche."""
        account = self.accounts[member.id]
        account.setdefaults(self.account_defaults)
        account.money = float('inf')
        if ctx.author==member:
            msg = "Vous êtes maintenant infiniment riche."
        else:
            msg = f"{member.name} est maintenant infiniment riche."
        return await ctx.send(msg)

    async def has_bank_account(self, ctx:commands.Context, member:discord.Member):
        """Assure l'existence d'un compte."""
        account = self.accounts[member.id]
        return self.is_bank_account(ctx, account, member)

    def is_bank_account(self, ctx:commands.Context, account, member:discord.Member):
        """Détermine si un compte bancaire est valide."""
        if not account:
            raise Bank.NoAccount(member, ctx.author)
        elif len(account)==1:
            raise Bank.NoAccount(member, ctx.author)
        
    def has_enough_money(self, ctx:commands.Context, account, member:discord.Member, money:int):
        """Assure la capacité de payer."""
        account.setdefaults(money=0)
        if account.money < money:
            raise Bank.NotEnoughMoney(member, ctx.author)

    @commands.command(name="argent")
    async def money(self, ctx:commands.Context, member:discord.User=None):
        """Affiche l'argent d'un compte bancaire."""
        member = member or ctx.author
        account = self.accounts[member.id]
        try:
            self.is_bank_account(ctx, account, member)
            self.has_enough_money(ctx, account, member, account.money)
            if member==ctx.author:
                msg = f"Vous avez"
            else:
                msg = f"{member.name} a"
            msg += f" **{account.money}**{emoji.money_bag} en banque."
        except Bank.Error as e:
            msg = str(e)
        return await ctx.send(msg)

    @commands.command(name="choisir-argent", aliases=["argent="])
    @access.admin
    async def set_money(self, ctx:commands.Context, money:int, member:discord.Member=None):
        """Choisi l'argent d'un compte bancaire."""
        member = member or ctx.author
        account = self.accounts[member.id]
        try:
            self.is_bank_account(ctx, account, member)
            account.money = money
            self.accounts.post(account)
            if member==ctx.author:
                msg = f"Vous avez maintenant **{money}**{emoji.money_bag}"
            else:
                msg = f"{member.name} a maintenant **{money}**{emoji.money_bag}"
        except Bank.Error as e:
            msg = str(e)
        return await ctx.send(msg)

    @commands.command(name="gagner-argent", aliases=["argent+="])
    @access.admin
    async def win_money(self, ctx:commands.Context, money:int, receiver:discord.Member=None):
        """Ajoute de l'argent à un compte."""
        receiver = receiver or ctx.author
        buyer = self.bot.user
        await self.pay(ctx, receiver, money, buyer)

    @commands.command(name="perdre-argent", aliases=["argent-="])
    async def loose_money(self, ctx:commands.Context, money:int, buyer:discord.Member=None):
        """Retire de l'argent d'un compte."""
        buyer = buyer or ctx.author
        receiver = self.bot.user
        await self.pay(ctx, receiver, money, buyer)

    def can_pay(
            self,
            author,
            receiver:discord.Member,
            receiver_account,
            buyer:discord.Member,
            buyer_account,
            money:int,
        ):
        """Détermine si un paiement est possible."""
        if buyer!=author and not author.id in masters:
            return False
        if buyer==receiver:
            return False
        if not receiver_account:
            return False
        if not buyer_account:
            return False
        if buyer_account.money < money:
            return False
        return True

    def ensure_payment(
            self,
            author,
            receiver:discord.Member,
            receiver_account,
            buyer:discord.Member,
            buyer_account,
            money:int,
        ):
        """Assure la possiblité d'un paiement."""
        if buyer!=author and not author.id in masters:
            raise NotAuthorized(buyer, author)
        if buyer==receiver:
            raise Bank.SelfPayment(buyer, author)
        if not receiver_account:
            raise Bank.NoAccount(receiver, author)
        if not buyer_account:
            raise Bank.NoAccount(buyer, author)
        if buyer_account.money < money:
            raise Bank.NotEnoughMoney(buyer, author)

    @commands.command(name="payer")
    async def pay(
            self,
            ctx:commands.Context,
            receiver:discord.Member,
            money:int,
            buyer:discord.Member=None
        ):
        """Paie un membre."""
        buyer = buyer or ctx.author
        # if buyer!=ctx.author and not ctx.author.id in masters:
        #     msg = f"Vous n'avez pas les droits."
        #     return await ctx.send(msg)
        # if buyer==receiver:
        #     msg = f"Aucun paiement nécessaire."
        #     return await ctx.send(msg)
        # receiver_account = self.accounts[receiver.id]
        # if not receiver_account:
        #     msg = f"{receiver.name} n'a pas de compte bancaire."
        #     return await ctx.send(msg)
        # buyer_account = self.accounts[buyer.id]
        # if not buyer_account:
        #     msg = f"{buyer.name} n'a pas de compte bancaire."
        #     return await ctx.send(msg)
        # if buyer_account.money < money:
        #     msg = f"{buyer.name} n'a pas assez d'argent en banque."
        #     return await ctx.send(msg)
        receiver_account = self.accounts[receiver.id]
        buyer_account = self.accounts[buyer.id]        
        try:
            self.ensure_payment(
                ctx.author,
                receiver,
                receiver_account,
                buyer,
                buyer_account,
                money)
        except Bank.Error as e:
            return await ctx.send(e)
        buyer_account.money -= money
        receiver_account.money += money
        self.accounts.post(buyer_account)
        self.accounts.post(receiver_account)
        transaction = Bank.Transaction(
            buyer=buyer.id,
            receiver=receiver.id,
            money=money,
            time=time.time()
        )
        self.transactions.post(transaction)
        msg = f"La transaction a été effectuée."
        return await ctx.send(msg)

    @commands.command(name="migrer-banque")
    @access.admin
    @check.warn("migrer de sqlite3 vers mongodb.")
    async def migrate(self, ctx:commands.Context):
        """Migre banque de sqlite vers mongodb."""
        sqldb.select('money')
        for (id, money, datetime) in sqldb.fetchall():
            account = Bank.Account(self.account_defaults)
            self.accounts.post(account)
        sqldb.select('transactions')
        for (buyer, receiver, money, datetime) in sqldb.fetchall():
            transaction = Bank.Transaction(
                buyer = buyer,
                receiver = receiver,
                money = money,
                time = datetime,
            )
            self.transactions.post(transaction)
        return await ctx.send("migration effectuée")

    @commands.command(name="code-bancaire")
    async def bank_code(self, ctx:commands.Context, member:discord.Member):
        """Donne le code bancaire d'un membre."""
        msg = f"Le code bancaire de {member.name} est ||{self.troll_message}||"
        return await ctx.send(msg)

    @commands.command(name="comptes-bancaires")
    @access.admin
    async def bank_accounts(self, ctx:commands.Context):
        """Informe sur un compte bancaire."""
        accounts = list(self.accounts.find())
        if len(accounts)==0:
            msg = "Personne n'a ouvert de compte en banque."
            return await ctx.send(msg)
        for account in accounts:
            account = Bank.Account(account)
            embed = self.describe_account(account)
            return await ctx.send(embed=embed)

    @commands.command(name="compte-bancaire")
    async def bank_account(self, ctx:commands.Context, member:discord.Member=None):
        """Informe sur un compte bancaire."""
        member = member or ctx.author
        account = self.accounts[member.id]
        try:
            self.is_bank_account(ctx, account, member)
            embed = self.describe_account(account, member)
            return await ctx.send(embed=embed)
        except Bank.Error as e:
            return await ctx.send(e)

    def describe_account(self, account, user:discord.Member=None):
        """Décrit un compte bancaire."""
        user = user or self.bot.get_user(account._id)
        creation = datetime.datetime.fromtimestamp(int(account.creation))
        if account.withdrawed_time:
            withdrawed_time = datetime.datetime.fromtimestamp(int(account.withdrawed_time))
        else:
            print(account.withdrawed_time)
            withdrawed_time = self.never
        if account.saved_time:
            saved_time = datetime.datetime.fromtimestamp(int(account.saved_time))
        else:
            saved_time = self.never
        embed = (discord.Embed(title=f"Compte bancaire de **{user.name}**", color=self.gold_color)
            .set_thumbnail(url=user.avatar_url)
            .add_field(name="argent", value=str(account.money)+emoji.money_bag)
            .add_field(name="creation", value=creation)
            .add_field(name="nombre de retirements", value=account.withdrawed)
            .add_field(name="dernier retirement", value=withdrawed_time)
            .add_field(name="nombre de placements", value=account.saved)
            .add_field(name="dernier placement", value=saved_time))
        return embed

    @commands.command()
    async def transactions(self, ctx:commands.Context, limit:int=None, reverse=True):
        """Liste les transactions bancaires."""
        if reverse:
            order = pymongo.DESCENDING
            strorder = "dernières"
        else:
            order = pymongo.ASCENDING
            strorder = "premières"
        limit = limit or self.limit
        limit = min(limit, self.max_limit)
        cursor = self.transactions.find({}, limit=limit, sort=[('time', order)])
        title = f"Liste des {limit} {strorder} transactions."
        lines = []
        for transaction in cursor:
            transaction = Bank.Transaction(transaction)
            buyer = self.bot.get_user(transaction.buyer)
            receiver = self.bot.get_user(transaction.receiver)
            t = datetime.datetime.fromtimestamp(int(transaction.time))
            line = f"{buyer.name} paie {receiver.name} **{transaction.money}**{emoji.money_bag} le {t}."
            lines.append(line)
        description = '\n'.join(lines)
        embed = discord.Embed(title=title, description=description, color=self.gold_color)
        return await ctx.send(embed=embed)

    @commands.command(name="ouvrir-compte")
    async def open_account(self, ctx:commands.Context, member:discord.Member=None):
        """Ouvre un compte en banque."""
        member = member or ctx.author
        if ctx.author!=member and not ctx.author.id in masters:
            return await ctx.send("Vous n'êtes pas autorisés à ouvrir le compte de cette personne.")
        account = self.accounts[member.id]
        if len(account)>1:
            if ctx.author==member:
                msg = "Vous avez déjà un compte en banque."
            else:
                msg = f"{member.name} a déjà un compte en banque."
            return await ctx.send(msg)
        account = Bank.Account(
            _id = member.id,
            money = self.starter_money,
            creation = time.time(),
            withdrawed = 0,
            withdrawed_time = None,
            saved = 0,
            saved_time = None,
        )
        self.accounts.post(account)
        if ctx.author==member:
            return await ctx.send("Votre compte est ouvert.")
        else:
            return await ctx.send(f"Un compte au nom de {member.name} a été ouvert.")

    @commands.command(name="fermer-compte", aliases=['supprimer-compte'])
    @check.warn("supprimer votre compte bancaire définitivement.")
    async def close_account(self, ctx:commands.Context, member:discord.Member=None):
        """Ferme un compte en banque."""
        member = member or ctx.author
        
        if ctx.author!=member and not ctx.author.id in masters:
            return await ctx.send(f"Vous n'êtes pas autorisés à fermer le compte de {member.name}.")
        self.accounts.find_one_and_delete(dict(_id=member.id))
        if member==ctx.author:
            return await ctx.send("Votre compte a été supprimé.")
        else:
            return await ctx.send(f"Le compte de {member.name} a été supprimé.")

    @commands.command(name="retirer")
    async def withdraw(self, ctx:commands.Context, money:int, member:discord.Member=None):
        """Retire l'argent vers le portefeuille."""
        member = member or ctx.author
        if member!=ctx.author and ctx.author.id not in masters:
            return await ctx.send("Vous n'avez pas les droits.")
        try:
            bank_account = self.bank.accounts[member.id]
            user_account = self.users.accounts[member.id]
            self.is_bank_account(ctx, bank_account, member)
            self.has_enough_money(ctx, bank_account, member, money)
        except Bank.Error as e:
            return await ctx.send(e)
        bank_account.money -= money
        user_account.money += money
        bank_account.withdrawed += 1
        bank_account.withdrawed_time = time.time()
        if ctx.author==member:
            msg = f"Vous avez retiré {money} {emoji.euro}."
        else:
            msg = f"{member.name} a retiré {money} {emoji.euro}."
        return await ctx.send(msg)

    @commands.command(name="placer")
    async def put(self, ctx:commands.Context, money:int, member:discord.Member=None):
        """Retire l'argent vers le portefeuille."""
        member = member or ctx.author
        if member!=ctx.author and ctx.author.id not in masters:
            return await ctx.send("Vous n'avez pas les droits.")
        try:
            users = self.bot.get_cog('Users')
            await users.connect(ctx, member)
            user_account = self.users.accounts[member.id]
            bank_account = self.bank.accounts[member.id]
            self.is_bank_account(ctx, bank_account, member)
            if user_account.money < money:
                raise Bank.Error("Vous n'avez pas assez d'argent dans votre portefeuille.")
        except Bank.Error as e:
            return await ctx.send(e)
        user_account.money -= money
        bank_account.money += money
        bank_account.saved += 1
        bank_account.saved_time = time.time()
        if ctx.author==member:
            msg = f"Vous avez placé {money} {emoji.euro}."
        else:
            msg = f"{member.name} a placé {money} {emoji.euro}."
        return await ctx.send(msg)

    @commands.command(name="sup-banque")
    @access.admin
    async def delete_bank(self, ctx:commands.Context):
        """Supprime transactions et comptes."""
        await self.delete_transactions(ctx)
        await self.delete_accounts(ctx)

    @commands.command(name="sup-transactions")
    @access.admin
    @check.warn("supprimer toutes les transactions bancaires.")
    async def delete_transactions(self, ctx:commands.Context):
        """Supprime toutes les transactions."""
        self.transactions.delete_many({})
        msg = "Toutes les transactions bancaires sont supprimées."
        await ctx.send(msg)

    @commands.command(name="sup-comptes")
    @access.admin
    @check.warn("supprimer tous les comptes bancaires.")
    async def delete_accounts(self, ctx:commands.Context):
        """Supprime tous les comptes bancaires."""
        self.accounts.delete_many({})
        msg = "Tous les comptes bancaires sont supprimés."
        await ctx.send(msg)
            
    @commands.command(name="vider-comptes")
    @access.admin
    @check.warn("mettre à zéro tous les comptes bancaires.")
    async def empty_accounts(self, ctx:commands.Context):
        """Vide tous les comptes bancaires."""
        self.accounts.update_many({}, {"$set":{"money":0}})
        msg = "Tous les comptes bancaires sont à zéro."
        await ctx.send(msg)

    @commands.command(name="drop-comptes")
    @access.admin
    @check.warn("supprimer la collection de comptes bancaires")
    async def drop_accounts(self, ctx:commands.Context):
        """Drop la collection des comptes."""
        self.accounts.drop()
        msg = "La collection des comptes bancaires est supprimée."
        await ctx.send(msg)

    @commands.command(name="drop-transactions")
    @access.admin
    @check.warn("supprimer la collection de transactions bancaires")
    async def drop_transactions(self, ctx:commands.Context):
        """Drop la collection des transactions."""
        self.transactions.drop()
        msg = "La collection des transactions bancaires est supprimée."
        await ctx.send(msg)

def setup(bot):
    bot.add_cog(Bank(bot))
