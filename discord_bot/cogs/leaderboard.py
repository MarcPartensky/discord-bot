from discord.ext import commands
from utils.tools import not_invoked_command
from config.config import access, cluster
from models.user import User

import discord


class LeaderBoard(commands.Cog):
    """Board of users ranked by money."""

    def __init__(self, bot: commands.Bot):
        """Create the leaderboard cog using the bot."""
        self.bot = bot
        self.color = discord.Color.dark_gold()

    @commands.group()
    async def leaderboard(self, ctx: commands.Context):
        """Groupe de commande du leaderboard."""
        if not ctx.invoked_subcommand:
            not_invoked_command(ctx, "LeaderBoard")

    @leaderboard.command(name="afficher", aliases=["show", "a"])
    async def show(self, ctx: commands.Context):
        """Affiche le leaderboard."""
        embed = discord.Embed(title="LeaderBoard", color=self.color)
        leaderboard_list = []
        for member in ctx.guild.members:
            if id in cluster.bank.accounts:
                money = cluster.bank.accounts[member.id].money
            else:
                money = 0
            leaderboard_list.append((member.name, money))
        leaderboard_list.sort(key=lambda x: x[1], reverse=True)
        print(leaderboard_list)
        for name, money in leaderboard_list:
            embed.add_field(name=name, value=str(money))
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(LeaderBoard(bot))
