#!/usr/bin/env python
"""Control ssh sessions."""

import os
import typing
import discord
from pexpect import pxssh
from discord.ext import commands
from discord.ext.commands.core import has_role

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
    async def ssh(self, ctx: commands.Context, hostname: str, port: int=0):
        """Run a command in a shell"""
        username=""
        await create_role_if_missing(ctx, SSH_ROLE, self.color)
        embed = discord.Embed(color=self.color)
        embed.set_thumbnail(url=self.thumbnail)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
        embed.description = self.shell_path
        embed.title = "Opened shell"
        await ctx.send(embed=embed)
        shell = pxssh.pxssh()
        shell.login(hostname, username, password)
        self.shells[ctx.author.id] = shell

    @commands.command(name="shells")
    async def list_shells(self, ctx: commands.Context):
        """List ."""
        if len(self.shells) == 0:
            return await ctx.send("> No active ssh connexion.")
        embed = discord.Embed(title="Active ssh connexions:", color=self.color)
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
            shell.sendline(msg.content)
            shell.prompt()
            output = shell.before.decode("utf-8")
            print(output)
            await msg.channel.send(output)

    # async def cog_common_error(self, ctx, error):
    #     """Close all shell sessions."""
    #     for shell in self.shells.values():
    #         shell.close()


def setup(bot):
    """Setup the Shell cog."""
    bot.add_cog(Shell(bot))
