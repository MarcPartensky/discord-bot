"""
This cog is meant to interact with the ialab api provided on
marcpartensky.com/ialab.
"""

import os
import requests
import discord

from discord.ext import commands, tasks
from config.config import cluster
from rich import print


class IALab(commands.Cog):
    """Interact with ialab bot with the commands of this cog."""

    def __init__(self, bot: commands.Bot, **kwargs):
        """Initialize the ialab cog."""
        super().__init__(**kwargs)
        self.url = os.environ["IALAB_URL"]
        self.bot = bot

    @commands.command()
    async def ia(self, ctx: commands.Context, *, message: str):
        """Send a message to the ialab bot."""
        response = requests.post(self.url, data=dict(message=message))
        print(response)

        if response.status_code != 200:
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(response.text, "html.parser")
            embed = discord.Embed(
                title=soup.title.string, description=soup.p.string, url=self.url
            )
            await ctx.send(embed=embed)

        else:
            d = response.json()
            await ctx.send(d["answer"])

    async def say(self, ctx: commands.Context, msg, lang):
        """Dit un message."""
        from gtts import gTTS

        tts = gTTS(msg, lang=lang)
        file = f"tts/{msg}.mp3"
        tts.save(file)
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(file))
        if not ctx.voice_client:
            return await ctx.send("Je ne suis pas dans un salon vocal.")

        def after(e):
            for file in os.listdir("tts"):
                if file.endswith("mp3"):
                    os.remove(os.path.join("tts", file))
            if e:
                print(f"Erreur de lecture du fichier audio {file}: {e}")

        ctx.voice_client.play(source, after=after)

    @commands.command()
    async def tell(self, ctx: commands.Context, *, message: str):
        """Send a message to the ialab bot."""

        response = requests.post(self.url, data=dict(message=message))
        print(response)

        if response.status_code != 200:
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(response.text, "html.parser")
            embed = discord.Embed(
                title=soup.title.string, description=soup.p.string, url=self.url
            )
            await ctx.send(embed=embed)

        else:
            d = response.json()
            await self.say(ctx, d["answer"], "en")


def setup(bot):
    """Setup the ialab cog."""
    bot.add_cog(IALab(bot))
