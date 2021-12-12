#!/usr/bin/env python
"""Control shells."""

from discord.ext import commands
import discord

from utils import tools
from config.config import access, masters, cluster
from config import emoji
from urllib.parse import quote

import requests
import asyncio
import re


class Shell(commands.Cog):
    """Control shells"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def shell(self, ctx: commands.Context):
        """Run a command in a shell"""
        ctx.author.id
        await ctx.send(command)


def setup(bot):
    bot.add_cog(Shell(bot))
