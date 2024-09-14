#!/usr/bin/env python
import discord
from discord.ext import commands

from config.config import access, masters


class Debug(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.role = "Debug"
        self.color = discord.Color.greyple()

    @commands.group(aliases=["db"])
    @access.admin
    async def debug(self, ctx: commands.Context):
        """Main command group of docker.
        Only members with the docker role can run those commands."""
        if not self.role in [role.name for role in ctx.guild.roles]:
            role = await ctx.guild.create_role(name=self.role, colour=self.color)
            await ctx.send(f"> Created `{role}` role.")
            members = []
            for master in masters:
                if member := await ctx.guild.fetch_member(master):
                    print(member, member.id, master)
                    await member.add_roles(role)
                    members.append(member)
            if members:
                members = "\n".join(map(lambda m: f"+ {member}", members))
                await ctx.send(
                    '```diff\nAdded "' + self.role + '" role to:\n' + members + "```"
                )
                return

    @debug.command(aliases=["ctx"])
    async def context(self, ctx: commands.Context):
        """Supprime une ferme."""
        embed = discord.Embed(title="Contexte", color=self.color)
        for key, value in ctx.__dict__.items():
            embed.add_field(name=key, value=str(value))
        await ctx.send(embed=embed)

    @debug.command(aliases=["mess"])
    async def message(self, ctx: commands.Context):
        """Supprime une ferme."""
        embed = discord.Embed(title="Message", color=self.color)
        for key, value in ctx.message.__dict__.items():
            embed.add_field(name=key, value=str(value))
        await ctx.send(embed=embed)

    @debug.command(aliases=["mb"])
    async def member(self, ctx: commands.Context, member: discord.Member or None):
        """Debug in auteur de message"""
        member = member or ctx.author
        embed = discord.Embed(title=str(member), color=member.color)
        for key, value in member.__dict__.items():
            embed.add_field(name=key, value=str(value))
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Debug(bot))
