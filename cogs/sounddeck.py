from utils.date import months, days
from config.config import cluster, masters
from discord.ext import commands

import datetime
import discord
import time

class SoundDeck(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.sounds = cluster.sound_deck.sounds
        self.bot = bot

    @property
    def music(self):
        return self.bot.get_cog('Music')

    @commands.group(name="son", aliases=['sound', 'sn'])
    async def sound(self, ctx:commands.Context):
        """Groupe des commandes pour un son."""


    @commands.group(name="sons", aliases=['sounds', 'sns'])
    async def sounds(self, ctx:commands.Context):
        """Groupe des commandes pour des sons."""
        if not ctx.invoked_subcommand:
            await self.list_sounds(ctx)

    @sounds.command(name="voir", aliases=['v', 'show', 'see'])
    async def list_sounds(self, ctx:commands.Context):
        """Affiche tous les sons disponibles."""
        lines = []
        for s in self.sounds:
            author = self.bot.get_user(s.author)
            line = f"> {s._id} par {author.name} joue {s.url}."
            lines.append(line)
        msg = '\n'.join(lines)
        await ctx.send(msg)

    @sound.command(name="voir", aliases=['v', 'show', 'see'])
    async def show(self, ctx:commands.Context, *, name:str):
        """Affiche un son."""
        embed = self.embed_sound(name)
        await ctx.send(embed=embed)


    def embed_sound(self, name:str):
        """Embed a sound."""
        s = self.sounds[name]
        author = self.bot.get_user(s.author)
        f = lambda n: f'{days[n.weekday()]} {n.day} {months[n.month]} {n.year}'
        embed = discord.Embed(
            title=f"**{name}**",
            color=author.color,
            description=f"lien: {s.url}")
        d1 = datetime.datetime.fromtimestamp(s.creation_time)
        embed.add_field(name="crée le", value=f(d1))
        embed.add_field(name="joué", value=str(s.played))
        if s.last_used_time:
            d2 = datetime.datetime.fromtimestamp(s.last_used_time)
            embed.add_field(name="dernière utilisation", value=f(d2))
        return embed


    @sound.command(name='ajouter', aliases=['add', 'a'])
    async def add(self, ctx:commands.Context, url:str, *, name:str):
        """Ajoute un son."""
        if name in self.sounds and ctx.author.id not in masters:
            return await ctx.send(f"Le nom {name} est déjà pris.")
        self.sounds[name] = dict(
            author=ctx.author.id,
            url=url,
            creation_time=time.time(),
            last_used_time=None,
            played=0,
        )
        await ctx.send("Son ajoutée.")

    async def connect(self, ctx: commands.Context, music):
        """Connect to voice channel."""
        await music.cog_before_invoke(ctx)
        await music._join(ctx)

    @sound.command(name="jouer", aliases=['j', 'play', 'p'])
    async def play(self, ctx:commands.Context, *, name:str):
        """Joue un son."""
        music = self.music 
        sound = self.sounds[name]
        await self.connect(ctx, music)
        await music._play(ctx, search=sound.url)
        sound.played += 1
        sound.last_used_time = time.time()

def setup(bot):
    bot.add_cog(SoundDeck(bot))