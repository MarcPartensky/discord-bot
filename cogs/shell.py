#!/usr/bin/env python
"""Control shells."""

import os

from discord.ext import commands
import discord
from discord.ext.commands.core import has_role

from utils.tools import create_role_if_missing


import pexpect

SHELL_ROLE = "Shell"


class Shell(commands.Cog):
    """Control shells"""

    def __init__(self, bot: commands.Bot):
        """Initialize the cog with the bot."""
        self.bot = bot
        self.color: discord.Color = discord.Color.darker_grey()
        # self.thumbnail: str = (
        #     "https://cdn0.iconfinder.com/data/icons/development-2/24/terminal-512.png"
        # )
        self.thumbnail: str = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/da/GNOME_Terminal_icon_2019.svg/1200px-GNOME_Terminal_icon_2019.svg.png"
        self.shells: list = []

    @has_role(SHELL_ROLE)
    @commands.command(aliases=["sh"])
    async def shell(self, ctx: commands.Context):
        """Run a command in a shell"""
        await create_role_if_missing(ctx, SHELL_ROLE, self.color)
        embed = discord.Embed(color=self.color)
        embed.set_thumbnail(url=self.thumbnail)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
        embed.description = os.environ.get("SHELL")

        if ctx.author.id in self.shells:
            self.shells.remove(ctx.author.id)
            embed.title = "Closed shell"
            await ctx.send(embed=embed)
        else:
            embed.title = "Opened shell"
            await ctx.send(embed=embed)
            self.shells.append(ctx.author.id)

    @commands.command(name="shells")
    async def list_shells(self, ctx: commands.Context):
        """List opened shells."""
        if len(self.shells) == 0:
            return await ctx.send("> No shell opened.")
        embed = discord.Embed(title="Shells :", color=self.color)
        embed.set_thumbnail(url=self.thumbnail)

        shell_users = []
        for shell_user in map(self.bot.fetch_user, self.shells):
            shell_users.append(f"- {await shell_user}")
        embed.description = "\n".join(shell_users)
        await ctx.send(embed=embed)

    @commands.Cog.listener(name="on_message")
    async def on_message(self, msg: discord.Message):
        """Read all messages"""
        if msg.author == self.bot.user:
            return
        if msg.content.startswith(self.bot.command_prefix):
            return
        if msg.author.id in self.shells:
            await msg.channel.send("> response")


def setup(bot):
    """Setup the Shell cog."""
    bot.add_cog(Shell(bot))
