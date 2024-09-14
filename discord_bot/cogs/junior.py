"""
Junior ISEP related commands.
"""

import os
import requests
import discord

from discord.ext import commands, tasks
from config.config import ialab_bot_url, cluster
from rich import print


class Junior(commands.Cog):
    """Interact with ialab bot with the commands of this cog."""

    def __init__(self, bot: commands.Bot, **kwargs):
        """Initialize the ialab cog."""
        super().__init__(**kwargs)
        self.bot = bot


async def setup(bot):
    """Setup the ialab cog."""
    await bot.add_cog(Junior(bot))
