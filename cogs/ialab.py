"""
This cog is meant to interact with the ialab api provided on
marcpartensky.com/ialab.
"""

import requests
import discord

from discord.ext import commands, tasks
from config.config import ialab_bot_url, cluster
from rich import print


class IALab(commands.Cog):
    """Interact with ialab bot with the commands of this cog."""

    def __init__(self, bot: commands.Bot, **kwargs):
        """Initialize the ialab cog."""
        super().__init__(**kwargs)
        self.url = ialab_bot_url
        self.bot = bot

    @commands.command()
    async def ia(self, ctx: commands.Context, *, message: str):
        """Send a message to the ialab bot."""
        from bs4 import BeautifulSoup

        response = requests.post(self.url, data=dict(message=message))
        print(response)

        if response.status_code != 200:
            soup = BeautifulSoup(response.text, "html.parser")
            embed = discord.Embed(
                title=soup.title.string, description=soup.p.string, url=self.url
            )
            await ctx.send(embed=embed)

        else:
            d = response.json()
            await ctx.send(d["answer"])


def setup(bot):
    """Setup the ialab cog."""
    bot.add_cog(IALab(bot))
