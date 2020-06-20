from discord.ext import commands
import discord
import os

class TextToSpeech(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot

    @commands.command(name="dire")
    async def say(self, ctx:commands.Context, *, msg:str):
        """Dit un message à l'oral dans une conversation."""
        if not discord.opus.is_loaded():
            discord.opus.load_opus('libopus.so')
        from gtts import gTTS
        tts = gTTS(msg, lang="fr")
        file = f'tts/{msg}.mp3'
        tts.save(file)
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(file))
        if not ctx.voice_client:
            return await ctx.send("Je ne suis pas dans un salon vocal.")
        def after(e):
            for file in os.listdir("tts"):
                if file.endswith('mp3'):
                    os.remove(os.path.join("tts", file))
            if e:
                print(f'Erreur de lecture du fichier audio {file}: {e}')
        ctx.voice_client.play(source, after=after)


def setup(bot):
    bot.add_cog(TextToSpeech(bot))