from config.config import cluster

from discord.ext import commands
import discord

class Advertisement(commands.Cog):
    """Fais de la publicité moyennant rémunération."""
    def __init__(self, bot):
        self.bot = bot
        self.advertisement = cluster.advertisement
        self.accounts = self.advertisement.accounts
        self.prices = self.advertisement.prices
        self.users = cluster.users

    @commands.command(name="pub")
    async def advertise(self, ctx:commands.Context):
        """Fais de la pub moyennant paiement."""
        await ctx.send("En développement...")


def setup(bot):
    bot.add_cog(Advertisement(bot))