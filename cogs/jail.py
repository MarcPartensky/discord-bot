"""
A place where you don't want to be.
"""

import discord
import time
import random
import asyncio
import datetime

from discord.ext import commands, tasks
from config.config import cluster


class Jail(commands.Cog):
    """
    The power to get rid of annoying people as you wish.
    Make them pay for their sins!
    """

    insults = [
        "You have been **confined**.",
        "Current status: **confined**.",
        "Es la **¡confinacìon!**",
    ]

    def __init__(self, bot: commands.Bot):
        """Initialize the jail commands."""
        self.bot = bot
        # cluster -> database -> collection -> document
        # self.jail = cluster.jail
        self.jail = cluster.jail
        self.term = 10  # in minute
        self.unit = "min"
        self.role_name = "Jail"
        self.check.start()

    # @access.admin
    # def add_guardian(self, member: discord.Member):
    #     """"""

    @tasks.loop(minutes=1)
    async def check(self):
        pass

    def convert_term(self, term, unit):
        """Converti un temps de sentence en seconde.
        La conversion prend en compte l'unité de temps initial."""
        if unit == "sec":
            pass
        elif unit == "min":
            term *= 60
        elif unit == "hour":
            term *= 3600
        elif unit == "day":
            term *= 24 * 3600
        elif unit == "month":
            term *= 30 * 24 * 3600
        elif unit == "year":
            term *= 355 * 30 * 24 * 3600
        elif unit == "decade":
            term *= 10 * 355 * 30 * 24 * 3600
        elif unit == "century":
            term *= 100 * 355 * 30 * 24 * 3600
        elif unit == "millenium":
            term *= 1000 * 355 * 30 * 24 * 3600
        else:  # seconds
            raise Exception(
                "This unit does not exist." "Advice: use millenium instead."
            )
        return term

    @commands.command(name="emprisonner", aliases=["tojail", "imprison"])
    async def imprison(
        self,
        ctx: commands.Context,
        member: discord.Member,
        term: int = None,
        unit: str = None,
    ):
        """Emprisonne un membre gratuitement."""
        term = term or self.term
        unit = unit or self.unit
        term = self.convert_term(term, unit)

        guild_info = self.jail.info[ctx.guild.id]

        text_jail = discord.utils.get(ctx.guild.channels, name="jail")
        if not text_jail:
            guild_info.text_jail_existed = False
            await ctx.guild.create_text_channel("jail")
        else:
            if not "text_jail_existed" in guild_info:
                guild_info.text_jail_existed = True

        voice_jail = discord.utils.get(ctx.guild.channels, name="Jail")
        if not voice_jail:
            guild_info.voice_jail_existed = False
            voice_jail = await ctx.guild.create_voice_channel("Jail")
        else:
            if not "text_jail_existed" in guild_info:
                guild_info.voice_jail_existed = True

        insult = random.choice(Jail.insults)
        message = (
            f"> 🔒 **{member}** 🔒\n"
            "> Tu va être dépouillé de **tout** ce que tu as:\n\n```diff\n"
            "Roles:"
        )

        roles = []
        undeleted_roles = []
        for role in member.roles[1:]:
            try:
                message += "\n- " + role.name
                print(f"{member} perd {role}")
                await member.remove_roles(role)
                roles.append(role)
            except discord.Forbidden:
                undeleted_roles.append(role)
                print(
                    f"Impossible de supprimer {role} \
                      pour {member} par {ctx.author}."
                )

        jail_role = discord.utils.get(ctx.guild.roles, name=self.role_name)
        await member.add_roles(jail_role)
        message += "\n+ Jail"
        for role in undeleted_roles:
            message += "\n+ " + role.name
        message += "\n```"
        message += "\n> " + insult

        self.jail.prisonners[member.id] = dict(
            police_officer=ctx.author.id,
            timestamp=time.time(),
            release=time.time() + term,
            term=term,
            removed_roles=[role.name for role in roles],
        )

        await ctx.send(message)

        # await asyncio.sleep(term)
        if not self.check.is_running():
            self.check.start()

    @commands.command(name="prison", aliases=["jail"])
    async def jail(self, ctx: commands.Context):
        """Affiche les prisonners."""
        embed = discord.Embed(
            title="Prison", color=0x555555, description="Les prisonniers sont :"
        )
        for prisonner in self.jail.prisonners:
            print(type(prisonner._id))
            member = self.bot.get_user(int(prisonner._id))
            # discord.utils.get(prisonner.police_officer, name=)
            police_officer = self.bot.get_user(prisonner.police_officer)
            timestamp = datetime.datetime.fromtimestamp(prisonner.timestamp)
            release = datetime.datetime.fromtimestamp(prisonner.release)
            embed.add_field(
                name=member.name,
                value=f"- emprisonné le {timestamp}\n"
                f"- par {police_officer}\n"
                f"- libéré le {release}",
            )
        await ctx.send(embed=embed)

    @commands.command(name="libérer", aliases=["unjail", "release", "free"])
    async def unjail(self, ctx: commands.Context, member: discord.Member):
        """Libère un membre par pur bonté."""
        print(self.jail.prisonners)
        print(member.id)
        if not member.id in self.jail.prisonners:
            await ctx.send(f"> **{member}** n'est pas en prison")
            await asyncio.sleep(1)
            await ctx.send(f"> enfin ...", delete_after=10)
            await asyncio.sleep(1)
            await ctx.send(f"> pour le moment ...", delete_after=9)
            return

        del self.jail.prisonners[member.id]

        text_jail = discord.utils.get(ctx.guild.channels, name="jail")
        if not text_jail:
            await ctx.guild.create_text_channel("jail")
        voice_jail = discord.utils.get(ctx.guild.channels, "jail")
        if not voice_jail:
            voice_jail = await ctx.guild.create_voice_channel("Jail")

        message = (
            f"> 🔓 **{member} !** 🔓\n"
            "> Vous êtes placé en libération conditionnelle.\n"
            "> Au moindre faux pas vous retournerez en prison.\n"
            "> Tâcher de ne pas recommencer!\n"
            "> Ou les conséquences seront **terribles!**"
        )
        # await self.free(ctx, member)
        await ctx.send(message)

    @commands.command()
    async def torture(self, ctx: commands.Context):
        """Torture quelqu'un."""
        pass

    def cog_unload(self):
        """Retire les tâches de fonds."""
        self.check.cancel()

    @check.before_loop
    async def before_printer(self):
        """Wait until the bot is ready."""
        await self.bot.wait_until_ready()

    # @commands.


def setup(bot):
    bot.add_cog(Jail(bot))
