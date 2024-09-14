#!/usr/bin/env python
"""Use groq"""

import typing
import discord
from discord.ext import commands
from discord.ext.commands.core import has_role

from utils.tools import create_role_if_missing, Capturing

import sys
import asyncio, os
from websockets.sync.client import connect

GROQ_ROLE = "Groq"


class Groq(commands.Cog):
    """Control Groq shells"""

    def __init__(self, bot: commands.Bot):
        """Initialize the cog with the bot."""
        self.host = "localhost"
        self.port = 8765
        self.bot = bot
        self.color: discord.Color = discord.Color.darker_grey()
        self.thumbnail: str = "https://wow.groq.com/wp-content/uploads/2021/04/groq-logo.svg"
        self.shells: typing.Dict[int, dict] = {}
    #     self.timeout = 3600

    # @commands.command(name="groq-shells")
    # async def groq_shells(self, ctx: commands.Context):
    #     """List opened shells."""
    #     if len(self.shells) == 0:
    #         return await ctx.send("> No shell opened.")
    #     embed = discord.Embed(title="Shells :", color=self.color)
    #     embed.set_thumbnail(url=self.thumbnail)

    #     shell_users = []
    #     for shell_user in map(self.bot.fetch_user, self.shells.keys()):
    #         shell_users.append(f"- {await shell_user}")
    #     embed.description = "\n".join(shell_users)
    #     await ctx.send(embed=embed)

    @commands.Cog.listener(name="on_message")
    async def on_message(self, msg: discord.Message):
        """Read all messages"""
        if msg.author == self.bot.user:
            return
        if msg.content.startswith(self.bot.command_prefix):
            return
        if self.hash(msg) in self.shells:
            answer = await self.ask(msg, msg.content)
            await msg.channel.send(answer)


    # async def cog_common_error(self, ctx, error):
    #     """Close all shell sessions."""
    #     for shell in self.shells.values():
    #         shell.close()

    @commands.command()
    async def groq(self, ctx: commands.Context):
        """Go in groq mode."""
        key = self.hash(ctx)
        # Create a role if in guild
        if ctx.guild:
            await create_role_if_missing(ctx, GROQ_ROLE, self.color)
        embed = discord.Embed(color=self.color)
        embed.set_thumbnail(url=self.thumbnail)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
        # embed.description = self.shell_path

        if ctx.author.id in self.shells:
            shell = self.shells[key]
            del self.shells[key]
            embed.title = "Closed shell"
            await ctx.send(embed=embed)
        else:
            embed.title = "Opened shell"
            await ctx.send(embed=embed)
            self.shells[key] = dict(messages=[])

    def hash(self, ctx):
        """Make a unique hash with channel id and author."""
        print(ctx.author.id, ctx.channel.id)
        print(self.shells)
        return hash((ctx.author.id, ctx.channel.id))

    def build_prompt(self, messages: list) -> str:
        """Build prompt."""
        prompt = ""
        for (me, bot) in messages:
            prompt += f"me: {me}\n"
            prompt += f"you: {bot}\n"
        return prompt

    async def ask(self, ctx, message: str) -> str:
        """Return groq answer"""
        key = self.hash(ctx)
        prompt = self.build_prompt(self.shells[key]["messages"])
        prompt += f"me: {message}\n"
        prompt += "answer my last message"
        with connect(f"ws://{self.host}:{self.port}") as websocket:
            websocket.send(prompt)
            answer = str(websocket.recv())
            print(f"{prompt} => {answer}")
        self.shells[key]["messages"].append((message, answer))
        return answer


async def setup(bot):
    """Setup the Shell cog."""
    await bot.add_cog(Groq(bot))
