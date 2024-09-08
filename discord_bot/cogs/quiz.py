from models.quiz import Quiz, Question

from discord.ext import commands
import discord
import math


class Quiz(commands.Cog):
    """Representation of a quiz."""

    def __init__(self, bot: commands.Bot):
        """Create a quiz given the bot."""
        self.bot = bot
        # self.quiz = quiz.Quiz()

    @commands.group(aliases=["qz"])
    async def quiz(self, ctx: commands.Context):
        """Groupe de commandes des Quizs."""
        if not ctx.invoked_subcommand:
            await ctx.send(
                f"> Erreur: commande inexistante."
                f"\n> Tapez `{self.bot.command_prefix}help quiz` pour voir les commandes disponibles."
            )

    @quiz.command(name="ajouter", aliases=["add", "a"])
    async def add(self, ctx: commands.Context, *, question: str):
        """Ajoute une question au quiz sélectionné."""
        question = self.quiz.parse(question)
        self.quiz.add(question)
        await ctx.send(f"> Question *{question}* ajoutée par **{ctx.author.name}**.")

    @quiz.command(name="suivant", aliases=["next", "sv", "n"])
    async def next(self, ctx: commands.Context):
        """Passe à la question suivante."""
        await self.quiz.next(ctx).embed


def setup(bot):
    bot.add_cog(Quiz(bot))
