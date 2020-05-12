from config.config import access, masters
from models.database import Database
from config import emoji
from utils import tools

from discord.ext import commands, tasks
import discord
import time


class Bank(commands.Cog, Database):
    class NotEnoughMoney(Exception):
        def __init__(self, user):
            super().__init__(f"{user.name} n'a pas assez d'argent.")
    class NoAccount(Exception):
        def __init__(self, user):
            super().__init__(f"{user.name} n'a pas de compte en banque.")

    def __init__(self, bot, path, **kwargs):
        commands.Cog.__init__(self, **kwargs)
        Database.__init__(self, path)
        self.bot = bot
        self.money_fields = dict(customer="integer", money="integer", datetime="integer")
        self.booklet_a_fields = dict(customer="integer", datetime="integer")
        self.transactions_fields = dict(buyer="integer", receiver="integer", money="integer", datetime="integer") #auto increment key
        self.starter_money = 10
        self.load()

    def load(self):
        self.create_table_if_not_exists("money", self.money_fields)
        self.create_table_if_not_exists("booklet_a", self.booklet_a_fields)
        self.create_table_if_not_exists("transactions", self.transactions_fields)
        try:
            self.create_unique_index(table="money", id="id", field="customer") #unique customer key
            self.create_unique_index(table="booklet_a", id="id", field="customer") #unique customer key
            self.insert(table="money", row=[self.bot.id, "infinity", time.time()])
        except:
            pass


    @commands.command(name="ouvrir-compte")
    async def open_an_account(self, ctx, customer:discord.User=None):
        """Supprime un compte bancaire."""
        customer = customer or ctx.author
        if ctx.author!=customer and not ctx.author.id in masters:
            await ctx.send("Vous n'êtes pas autorisés à ouvrir le compte de cette personne.")
            return
        self.select(table="money", conditions={"customer":customer.id})
        result = self.fetchone()
        if result:
            if ctx.author == customer:
                await ctx.send("Vous avez déjà un compte.")
            else:
                await ctx.send(f"Le nom {customer.name} est déjà pris.")
        else:
            self.insert(table="money", row=[customer.id, self.starter_money, time.time()])
            self.insert(table="transactions", row=[self.bot.id, customer.id, self.starter_money, time.time()])
            if ctx.author.id == customer.id:
                await ctx.send("Votre compte est ouvert.")
                await ctx.send(f"Vous bénéficez d'un starter de {self.starter_money} {emoji.coin}.")
            else:
                await ctx.send(f"Un compte au nom de {customer.name} a été ouvert.")
                await ctx.send(f"{customer.name} bénéficie d'un starter de {self.starter_money} {emoji.coin}.")

    @commands.command(name="fermer-compte")
    async def close_an_account(self, ctx, customer:discord.User=None):
        """Crée un compte bancaire."""
        customer = customer or ctx.author
        if ctx.author!=customer and not ctx.author.id in masters:
            await ctx.send("Vous n'êtes pas autorisés à fermer le compte de cette personne.")
            return
        self.select(table="money", conditions={"customer":customer.id})
        result = self.fetchone()
        if result:
            self.delete(table="money", conditions={"customer":customer.id})
            await ctx.send(f"Le compte au nom de '{customer.name}' a été fermé.")
        else:
            await ctx.send(f"Ce compte au nom de '{customer.name}' n'existe pas.")

    @commands.command(name="choisir-argent", aliases=["argent="])
    @access.admin
    async def set_money(self, ctx, money:int, customer:discord.User=None):
        """Choisis l'argent d'un compte."""
        customer = customer or ctx.author
        buyer = self.bot.get_user(self.bot.id)
        self.update(table="money", values={"money":money}, conditions={"customer":customer.id})
        await ctx.send(f"{customer.name} a maintenant {money} {emoji.coin}.")

    @commands.command(name="gagner-argent", aliases=["argent+="])
    @access.admin
    async def win_money(self, ctx, money:int, customer:discord.User=None):
        """Ajoute de l'argent à un compte."""
        customer = customer or ctx.author
        buyer = self.bot.get_user(self.bot.id)
        try:
            self.win(customer, money)
            await ctx.send(f"{customer.name} reçoit {money} {emoji.coin} de {buyer.name}.")
        except Exception as e:
            await ctx.send(e)

    @commands.command(name="perdre-argent", aliases=["argent-="])
    @access.admin
    async def loose_money(self, ctx, money:int, customer:discord.User=None):
        """Retire de l'argent à compte bancaire."""
        customer = customer or ctx.author
        receiver = self.bot.get_user(self.bot.id)
        try:
            self.loose(customer, money)
            await ctx.send(f"{customer.name} donne {money} {emoji.coin} à {receiver.name}.")
        except Exception as e:
            await ctx.send(e)


    @commands.command(name="argent")
    async def money(self, ctx, customer:discord.User=None):
        """Affiche l'argent d'un compte bancaire."""
        customer = customer or ctx.author
        self.select(table="money", column="money", conditions={"customer":customer.id})
        result = self.fetchone()
        if result:
            money = result[0]
            if customer==ctx.author:
                await ctx.send(f"Vous avez {money} {emoji.coin}.")
            else:
                await ctx.send(f"{customer.name} a {money} {emoji.coin}.")          
        else:
            if customer==ctx.author:
                await ctx.send(f"Vous avez n'avez pas de compte.")
            else:
                await ctx.send(f"Le compte {customer.name} n'existe pas.")

    @commands.command(name="vider-banque")
    @access.admin
    async def reset(self, ctx):
        """Vide tous les comptes bancaires."""
        self.update(table="money", values={"money":0})
        self.select(table="money", column="customer")
        for name in self.fetchall():
            self.insert(table="transaction", row=(name, 0, time.time()))
        await ctx.send("Tout les comptes bancaires sont mis à zéros.")

    @commands.command(name="sup-banque", aliases=['supprimer-banque'])
    @access.admin
    async def delete(self, ctx):
        """Vide tous les comptes bancaires."""
        self.drop_table("money")
        self.drop_table("booklet_a")
        self.drop_table("transactions")
        await ctx.send("Toute la banque est supprimée.")

    @commands.command(name="charger_banque")
    @access.admin
    async def load_bank(self, ctx):
        """Charge la banque."""
        self.load()
        await ctx.send("La banque est chargée.")

    @commands.command(name="comptes")
    @access.admin
    async def accounts(self, ctx):
        """Affiche tous les comptes."""
        rows = self["money"]
        if not rows:
            await ctx.send("La banque est vide.")
        else:
            for [id, money, time] in rows:
                customer = self.bot.get_user(id)
                msg = f"{customer.name} has {money} {emoji.coin}."
                await ctx.send(msg)

    @commands.command(name="nb-comptes", aliases=["nombre_comptes", "taille_comptes"])
    async def accounts_number(self, ctx):
        """Affiche le nombre total de comptes."""
        rows = self["money"]
        if not rows:
            await ctx.send("La banque est vide.")
        else:
            msg = f"Il y a {len(rows)} comptes en banque enregistrés."
            await ctx.send(msg)


    @commands.command()
    @access.admin
    async def transactions(self, ctx, n=10):
        """Affiche toutes les transactions."""
        rows = self["transactions"]
        n = min(n, len(rows))
        if not rows:
            await ctx.send("Aucune transaction n'a été effectué.")
        else:
            for i,[buyer_id, receiver_id, money, time] in enumerate(reversed(rows)):
                if i==n:
                    break
                buyer = self.bot.get_user(buyer_id)
                receiver = self.bot.get_user(receiver_id)
                msg = f"{buyer.name} paie {receiver.name} {money} {emoji.coin}."
                await ctx.send(msg)

    @commands.command(name="nb-transactions", aliases=["nombre_transactions, taille_transactions"])
    async def transactions_number(self, ctx):
        """Affiche le nombre total de transactions."""
        rows = self["transactions"]
        if not rows:
            await ctx.send("Il n'y a aucune transaction enregistrée.")
        else:
            msg = f"Il y'a {len(rows)} transactions enregistrées."
            await ctx.send(msg)

    def pay(self, buyer, receiver, money:int):
        """Paie un client avec l'argent."""
        #Checking if the buyer has an account
        self.select(table="money", column="money", conditions={"customer":buyer.id})
        result = self.fetchone()
        if not result:
            raise Bank.NoAccount(buyer)
        #Accepting infinite amount of money for the buyer
        buyer_money = result[0]
        try:
            buyer_money = int(result[0])
        except:
            buyer_money = float(buyer_money)
        #Checking if the buyer has enough money
        if buyer_money-money<0:
            raise Bank.NotEnoughMoney(buyer)
        #Checking if the receiver has an account
        self.select(table="money", column="money", conditions={"customer":receiver.id})
        result = self.fetchone()
        if not result:
            raise Bank.NoAccount(receiver)
        #Now that we're sure everything is fine the buyer can pay
        self.update(table="money", values={"money":buyer_money-money}, conditions={"customer":buyer.id})
        self.select(table="money", column="money", conditions={"customer":receiver.id})
        result = self.fetchone()
        #Accepting infinite amount of money for the receiver
        receiver_money = result[0]
        try:
            receiver_money = int(result[0])
        except:
            receiver_money = float(receiver_money)
        #Then the receiver can receiver
        self.update(table="money", values={"money":receiver_money+money}, conditions={"customer":receiver.id})
        #The transactions are stored
        self.insert(table="transactions", row=[buyer.id, receiver.id, money, time.time()])

    def win(self, customer:discord.User, money:int):
        """Gagne de l'argent"""
        self.pay(self.bot, customer, money)
    
    def loose(self, customer:discord.User, money:int):
        """Perds de l'argent."""
        self.pay(customer, self.bot, money)

    @commands.command(name="payer", aliases=["pay"])
    async def pay_command(self, ctx, receiver:discord.User, money:int, buyer:discord.User=None):
        """Paie un utilisateur."""
        buyer = buyer or ctx.author
        if not ctx.author.id in masters:
            await ctx.send("Vous n'avez pas les droits.")
            return
        try:
            self.pay(buyer, receiver, money)
            await ctx.send(f"{receiver.name} a reçu {money} {emoji.coin} de {buyer.name}")
        except Exception as e:
            await ctx.send(e)
            
def setup(bot): #Production
    from os.path import join, dirname, abspath
    path = join(dirname(dirname(abspath(__file__))), 'database/bank.db')
    bot.add_cog(Bank(bot, path=path))
    
    

if __name__=="__main__": #Test
    b = Bank(None, ":memory:")
    b.register(None, "marc")
    b.register(None, "marc")
    print(b["money"])

