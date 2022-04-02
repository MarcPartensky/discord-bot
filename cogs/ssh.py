#!/usr/bin/env python
"""Control ssh sessions."""

import os
import sys
import typing
import discord
import pxssh
from discord.ext import commands
from discord.ext.commands.core import has_role

from utils.tools import create_role_if_missing, Capturing


import pexpect

SSH_ROLE = "Ssh"


class Shell(commands.Cog):
    """Control shells"""

    def __init__(self, bot: commands.Bot):
        """Initialize the cog with the bot."""
        self.bot = bot
        self.color: discord.Color = discord.Color.light_purple()
        self.thumbnail: str = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/da/GNOME_Terminal_icon_2019.svg/1200px-GNOME_Terminal_icon_2019.svg.png"
        self.timeout = 3600
        self.shell_path = os.environ.get("SHELL")
        self.shells: typing.Dict[int, pexpect.pty_spawn.spawn] = {}

    @has_role(SHELL_ROLE)
    @commands.command()
    async def ssh(self, ctx: commands.Context):
        """Run a command in a shell"""
        await create_role_if_missing(ctx, SSH_ROLE, self.color)
        embed = discord.Embed(color=self.color)
        embed.set_thumbnail(url=self.thumbnail)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
        embed.description = self.shell_path

        if ctx.author.id in self.shells:
            shell = self.shells[ctx.author.id]
            shell.close()
            del self.shells[ctx.author.id]
            embed.title = "Closed shell"
            await ctx.send(embed=embed)
        else:
            embed.title = "Opened shell"
            await ctx.send(embed=embed)
            shell = pexpect.spawn(command=self.shell_path, encoding="utf-8")
            self.shells[ctx.author.id] = shell

    @commands.command(name="shells")
    async def list_shells(self, ctx: commands.Context):
        """List opened shells."""
        if len(self.shells) == 0:
            return await ctx.send("> No shell opened.")
        embed = discord.Embed(title="Shells :", color=self.color)
        embed.set_thumbnail(url=self.thumbnail)

        shell_users = []
        for shell_user in map(self.bot.fetch_user, self.shells.keys()):
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
            shell = self.shells[msg.author.id]
            print(shell.sendline(msg.content))
            # output = shell.read()
            # output = shell.before
            # print(output)
            shell.expect(pexpect.EOF)
            # shell.expect(".*\$ ")
            output = shell.before
            # output = "\n".join(output_list)
            print(output)
            # await msg.channel.send(output)
            await msg.channel.send("test")

    # async def cog_common_error(self, ctx, error):
    #     """Close all shell sessions."""
    #     for shell in self.shells.values():
    #         shell.close()


def setup(bot):
    """Setup the Shell cog."""
    bot.add_cog(Shell(bot))
