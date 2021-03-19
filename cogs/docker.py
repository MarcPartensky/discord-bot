"""
Control over my docker cluster.
"""

import requests
import discord

from discord.ext import commands, tasks


class Docker(commands.Cog):
    """Manage my docker containers."""

    def __init__(self, bot: commands.Bot, **kwargs):
        """Initialize the ialab cog."""
        super().__init__(**kwargs)
        self.bot = bot


def setup(bot):
    """Setup the ialab cog."""
    bot.add_cog(Docker(bot))
