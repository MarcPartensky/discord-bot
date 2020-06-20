from discord.ext import commands
import discord
import os

class TextToSpeech(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot

    @commands.command(name="dire")
    async def text_to_speech(self, ctx:commands.Context, *, msg:str):
        """Dit un message à l'oral dans une conversation."""
        from gtts import gTTS
        tts = gTTS(msg,lang="fr")
        file = f'tts/{msg}.mp3'
        tts.save(file)
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(file))
        if not ctx.voice_client:
            return await ctx.send("Je ne suis pas dans un salon vocal.")
        def after(e):
            for file in os.listdir("tts"):
                os.remove(os.path.join("tts", file))
            if e:
                print(f'Erreur de lecture du fichier audio {file}: %s' % e)
        ctx.voice_client.play(source, after=after)



# def tts(self, ctx, *, message: str):
#         """ Text to speech through the bot's mic """
#         func = functools.partial(self.create_tts, message)
#         response = await self.bot.loop.run_in_executor(None, func)
#         with open(path('tmp', 'tts.mp3'), 'wb') as out:
#             out.write(response.audio_content)
#         vc = ctx.guild.voice_client
#         if not vc:
#             vc = await ctx.author.voice.channel.connect()
#         vc.play(discord.FFmpegPCMAudio(source=path(
#             'tmp', 'tts.mp3'), options='-loglevel fatal'))
#         vc.source = discord.PCMVolumeTransformer(vc.source)
#         vc.source.volume = 1
#         while vc.is_playing():
#             await asyncio.sleep(1)
#         vc.stop() 

def setup(bot):
    bot.add_cog(TextToSpeech(bot))