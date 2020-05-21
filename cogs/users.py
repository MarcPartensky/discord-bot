from models.mongocollection import MongoCollection

from discord.ext import commands, tasks
import discord

from config.config import cluster


class Users(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.users = cluster.users
        self.info = self.users.info
        self.accounts = self.users.accounts
        self.starter_wallet_size = 1000
        self.starter_wallet_money = 5

    # @commands.command()
    # def update_user(self, ctx:commansd)

    @commands.command(name='portefeuille')
    async def wallet(self, ctx:commands.Context, member:discord.Member=None):
        """Affiche l'argent d'un utilisateur."""
        user = ctx.author or member
        account = self.accounts[user.id]
        msg = f"Vous avez {account.money} pieces dans votre portefeuille."
        await ctx.send(msg)

    @wallet.before_invoke
    async def connect(self, ctx:commands.Context, member:discord.Member=None):
        """Connecte un utilisateur à son compte."""
        user = ctx.author or member
        account = self.accounts[user.id]
        if not account:
            post = Post
            self.accounts.insert_one(post)
        

def setup(bot):
    bot.add_cog(Users(bot))
