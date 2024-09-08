import discord
from discord.ext import commands
from config.config import cluster, access

"""Module for dealing with quests."""


class Quest(commands.Cog, name="Quête"):
    def __init__(self, bot: commands.Bot):
        """Créer la catégorie des quêtes pour convertir l'énergie en argent."""
        self.bot = bot

    @commands.command(name="quêtes", aliases=["quests"])
    async def quests(self, ctx: commands.Context):
        """Affiche les quêtes disponibles."""

    @commands.group(name="quête", aliases=["quest"])
    async def quest(self, ctx: commands.Context):
        """Groupe de commande des quêtes."""
        if not ctx.invoked_subcommand:
            pass

    @quest.command(aliases=["i"])
    async def info(self, ctx: commands.Context):
        """Affiche des informations sur une quête."""
        pass

    @quest.command(name="accepter", aliases=["accept", "do"])
    async def accept(self, ctx: commands.Context):
        """Accepte une quête."""
        pass

    @quest.command(name="ajouter", aliases=["add", "a", "+"])
    @access.admin
    async def add(self, ctx: commands.Context):
        """Ajoute un quête."""
        pass

    @quest.command(name="retirer", aliases=["remove", "delete", "d", "-"])
    @access.admin
    async def remove(self, ctx: commands.Context):
        """Retire une quête."""


def setup(bot: commands.Bot):
    bot.add_cog(Quest(bot))
