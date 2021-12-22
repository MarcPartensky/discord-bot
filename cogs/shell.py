#!/usr/bin/env python
"""Control shells."""

import os

from discord.ext import commands
import discord
from discord.ext.commands.core import has_role

from utils import tools
from config.config import access, masters, cluster, SHELL_ROLE
from config import emoji
from urllib.parse import quote


import subprocess


class Shell(commands.Cog):
    """Control shells"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.color: discord.Color = discord.Color.darker_grey()
        # self.thumbnail: str = (
        #     "https://cdn0.iconfinder.com/data/icons/development-2/24/terminal-512.png"
        # )
        self.thumbnail: str = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/da/GNOME_Terminal_icon_2019.svg/1200px-GNOME_Terminal_icon_2019.svg.png"
        self.shells: list = []

    async def give_shell_role_to_masters(self, ctx: commands.Context):
        """Give shell tole to masters."""
        if not SHELL_ROLE in [role.name for role in ctx.guild.roles]:
            role = await ctx.guild.create_role(name=SHELL_ROLE, colour=self.color)
            await ctx.send(f"> Created `{SHELL_ROLE}` role.")
            members = []
            for master in masters:
                if member := await ctx.guild.fetch_member(master):
                    if SHELL_ROLE in [role.name for role in member.roles]:
                        print(member, member.id, master)
                        await member.add_roles(role)
                        members.append(member)
            if members:
                members = "\n".join(map(lambda m: f"+ {member}", members))
                await ctx.send(
                    '```diff\nAdded "' + SHELL_ROLE + '" role to:\n' + members + "```"
                )
                return

    # @commands.has_role(SHELL_ROLE)
    @commands.command(aliases=["sh"])
    async def shell(self, ctx: commands.Context):
        """Run a command in a shell"""
        await self.give_shell_role_to_masters(ctx)
        if SHELL_ROLE in [role.name for role in ctx.author.roles]:
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
        else:
            await ctx.send("Unauthorized")

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
