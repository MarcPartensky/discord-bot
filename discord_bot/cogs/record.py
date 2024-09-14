"""
All sound effects you want in one command.
"""

import time
import datetime
import discord

from utils.date import months, days
from config.config import cluster, masters
from discord.ext import commands


class Record(commands.Cog):
    """Record voices."""

    def __init__(self, bot: commands.Bot):
        """Define the recorder"""
        # self.sounds = cluster.sound_deck.sounds
        self.bot = bot
        self.connections = {}

    # @property
    # def music(self):
    #     return self.bot.get_cog("Music")

    # @commands.group(name="son", aliases=["sound", "sn"])
    # async def sound(self, ctx: commands.Context):
    #     """Groupe des commandes pour un son."""
    #     if not ctx.invoked_subcommand:
    #         return await ctx.send(
    #             f"> Commande inexistante."
    #             f"\n> Écrivez `{ctx.bot.command_prefix}help son` pour voir les commandes disponibles."
    #             ""
    #         )

    # @sound.command(name="voir", aliases=["v", "show", "see"])
    # async def show(self, ctx: commands.Context, *, name: str):
    #     """Affiche un son."""
    #     embed = self.embed_sound(name)
    #     await ctx.send(embed=embed)


    @commands.command(name="record")
    async def record(self, ctx):  # If you're using commands.Bot, this will also work.
        """Enregistre une voix."""
        voice = ctx.author.voice

        if not voice:
            await ctx.respond("You aren't in a voice channel!")

        vc = await voice.channel.connect()  # Connect to the voice channel the author is in.
        self.connections.update({ctx.guild.id: vc})  # Updating the cache with the guild and channel.

        vc.start_recording(
            discord.sinks.WaveSink(),  # The sink type to use.
            self.once_done,  # What to do once done.
            ctx.channel  # The channel to disconnect from.
        )
        await ctx.respond("Started recording!")

    def once_done(self, *args):
        print("its done", args)

async def setup(bot):
    await bot.add_cog(Record(bot))
