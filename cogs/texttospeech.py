from discord.ext import commands

import nightcore as nc

import discord
import os


class TextToSpeech(commands.Cog):
    def __init__(self, bot: commands.Bot, lang="fr"):
        self.bot = bot
        self.lang = lang

    async def cog_before_invoke(self, ctx: commands.Context):
        """Assure que l'opus est chargé."""
        music = self.bot.get_cog("Music")
        await music.cog_before_invoke(ctx)
        await music._join(ctx)
        # if os.environ.get('DEVELOPMENT'):
        #     if not discord.opus.is_loaded():
        #         discord.opus.load_opus('libopus.so')

    @commands.command(name="speech")
    async def speech(self, ctx: commands.Context, lang, *, msg: str):
        """Dit un message dans une langue en vocal."""
        await self.say(ctx, msg, lang)

    @commands.command(name="dire")
    async def french_say(self, ctx: commands.Context, *, msg: str):
        """Dit un message français en vocal."""
        await self.say(ctx, msg, "fr")

    @commands.command(name="say")
    async def english_say(self, ctx: commands.Context, *, msg: str):
        """Dit un message anglais en vocal."""
        await self.say(ctx, msg, "en")

    @commands.command(name="decir")
    async def spanish_say(self, ctx: commands.Context, *, msg: str):
        """Dit un message espagnol en vocal."""
        await self.say(ctx, msg, "es")

    @commands.command(name="thai")
    async def thai(self, ctx: commands.Context, *, msg: str):
        """Traduit et dit un message en thai."""
        from translate import Translator

        t = Translator(to_lang="th", from_lang=self.lang)
        msg = t.translate(msg)
        await ctx.send("> " + msg)
        await self.say(ctx, msg, "th")

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

    @commands.command(name="vite", aliases=["vt", "speed", "nightcore"])
    async def speed(self, ctx: commands.Context, msg: str, pitch=1, lang="fr"):
        """Dit un message plus ou moins rapidement."""
        # Text to speech stuff
        from gtts import gTTS

        tts = gTTS(msg, lang=lang)
        file = f"tts/{msg}.mp3"
        tts.save(file)
        # Here comes the nightcore stuff
        nc_audio = file @ nc.Tones(pitch)
        nc_audio.export(file)
        # Then discord stuff
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


def setup(bot):
    bot.add_cog(TextToSpeech(bot))
