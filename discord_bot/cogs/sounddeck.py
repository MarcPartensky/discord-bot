"""
All sound effects you want in one command.
"""

import time
import datetime
import discord

from utils.date import months, days
from config.config import cluster, masters
from discord.ext import commands


class SoundDeck(commands.Cog):
    """Sound deck cog for the sound deck commands."""

    def __init__(self, bot: commands.Bot):
        """Define the sound deck using the bot."""
        self.sounds = cluster.sound_deck.sounds
        self.bot = bot

    @property
    def music(self):
        return self.bot.get_cog("Music")

    @commands.group(name="son", aliases=["sound", "sn"])
    async def sound(self, ctx: commands.Context):
        """Groupe des commandes pour un son."""
        if not ctx.invoked_subcommand:
            return await ctx.send(
                f"> Commande inexistante."
                f"\n> Écrivez `{ctx.bot.command_prefix}help son` pour voir les commandes disponibles."
                ""
            )

    @commands.group(name="sons", aliases=["sounds", "sns"])
    async def sounds(self, ctx: commands.Context):
        """Groupe des commandes pour des sons."""
        if not ctx.invoked_subcommand:
            await self.list_sounds(ctx)

    @sounds.command(name="voir", aliases=["v", "show", "see"])
    async def list_sounds(self, ctx: commands.Context):
        """Affiche tous les sons disponibles."""
        msg = ""
        for s in self.sounds:
            print(s)
            if len(s.keys()) == 1:
                del self.sounds[s._id]
            else:
                author = self.bot.get_user(s.author)
                if not hasattr(author, "name"):
                    line = f"> **{s._id}** ajouté par *inconnu*.\n"
                else:
                    line = f"> **{s._id}** ajouté par *{author.name}*.\n"
                if len(msg + line) > 2000:
                    await ctx.send(msg)
                    msg = ""
                else:
                    msg += line
        if len(msg):
            await ctx.send(msg)

    @sound.command(name="voir", aliases=["v", "show", "see"])
    async def show(self, ctx: commands.Context, *, name: str):
        """Affiche un son."""
        embed = self.embed_sound(name)
        await ctx.send(embed=embed)

    def embed_sound(self, name: str):
        """Embed a sound."""
        s = self.sounds[name]
        author = self.bot.get_user(s.author)
        f = lambda n: f"{days[n.weekday()]} {n.day} {months[n.month]} {n.year}"
        embed = discord.Embed(
            title=f"**{name}**", color=author.color, description=f"lien: {s.url}"
        )
        d1 = datetime.datetime.fromtimestamp(s.creation_time)
        embed.add_field(name="crée le", value=f(d1))
        embed.add_field(name="joué", value=str(s.played))
        if s.last_used_time:
            d2 = datetime.datetime.fromtimestamp(s.last_used_time)
            embed.add_field(name="dernière utilisation", value=f(d2))
        return embed

    @sound.command(name="ajouter", aliases=["add", "a"])
    async def add(self, ctx: commands.Context, url: str, *, name: str):
        """Ajoute un son."""
        if name in self.sounds and ctx.author.id not in masters:
            return await ctx.send(f"> Le nom **{name}** est déjà pris.")
        self.sounds[name] = dict(
            author=ctx.author.id,
            url=url,
            creation_time=time.time(),
            last_used_time=None,
            played=0,
        )
        await ctx.send(f"Le son {name} est ajouté.")

    @sound.command(name="supprimer", aliases=["sup", "delete", "d", "remove", "rm"])
    async def delete(self, ctx: commands.Context, *, name: str):
        """Supprime un son."""
        if name not in self.sounds:
            return await ctx.send(f"> Le son **{name}** n'existe pas.")
        if not ctx.author.id in masters:
            sound = self.sounds[name]
            if sound.author != ctx.author.id:
                author = self.get.get_user(sound.author)
                return await ctx.send(
                    f"> Le son **{name}** appartient à *{author.name}*."
                    "> Vous n'avez pas les droits."
                )
        del self.sounds[name]
        return await ctx.send(f"> Le son **{name}** est supprimé.")

    async def connect(self, ctx: commands.Context, music):
        """Connect to voice channel."""
        await music.cog_before_invoke(ctx)
        await music._join(ctx)

    @sound.command(name="jouer", aliases=["j", "play", "p"])
    async def play(self, ctx: commands.Context, *, name: str):
        """Joue un son."""
        music = self.music
        sound = self.sounds[name]
        await self.connect(ctx, music)
        await music._play(ctx, search=sound.url)
        sound.played += 1
        sound.last_used_time = time.time()


def setup(bot):
    bot.add_cog(SoundDeck(bot))
