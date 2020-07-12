import asyncio

import discord
import youtube_dl

from discord.ext import commands

# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''


ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('webpage_url')

    @classmethod
    async def from_url(cls, url, *, loop=None, download=False):
        print(url, loop, download)
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=download))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if not download else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

    @classmethod
    async def from_youtube(cls, data, *, loop=None, download=False):
        filename = data['webpage_url'] if not download else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


class Music2(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="mjoin")
    async def join(self, ctx, *, channel: discord.VoiceChannel):
        """Joins a voice channel"""

        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)

        await channel.connect()

    @commands.command(name="mplay_locally")
    async def play_locally(self, ctx, *, query):
        """Plays a file from the local filesystem"""

        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(query))
        ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)

        await ctx.send('Now playing: {}'.format(query))

    @commands.command(name="mplay")
    async def play(self, ctx, *, url, download=False):
        """Plays from a url (almost anything youtube_dl supports)"""
        print("at least i'm here")

        async with ctx.typing():
            print("i'm even here")
            data = await self.bot.loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=download))
            print("i might be even here")
            if 'entries' in data:
                print(len(data['entries']))
                print("if")
                for entry in data['entries']:
                    player = await YTDLSource.from_youtube(entry, loop=self.bot.loop, download=download)
                    ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
                    await ctx.send('Now playing: {}'.format(player.title))
            else:
                print("else")
                player = await YTDLSource.from_youtube(data, loop=self.bot.loop, download=download)
                ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
                await ctx.send('Now playing: {}'.format(player.title))

    @commands.command()
    async def stream(self, ctx, *, url):
        """Streams from a url (same as yt, but doesn't predownload)"""

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop, download=False)
            ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
        await ctx.send('Now playing: {}'.format(player.title))

    @commands.command("mvolume")
    async def volume(self, ctx, volume: int):
        """Changes the player's volume"""

        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")

        ctx.voice_client.source.volume = volume / 100
        await ctx.send("Changed volume to {}%".format(volume))

    @commands.command(name="mstop")
    async def stop(self, ctx):
        """Stops and disconnects the bot from voice"""
        await ctx.voice_client.disconnect()
        await ctx.send("Disconnected.")

    @commands.command(name="mpause")
    async def pause(self, ctx):
        """Fais pause."""
        ctx.voice_client.pause()

    @commands.command(name="mresume")
    async def resume(self, ctx):
        """Reprends la musique."""
        ctx.voice_client.resume()

    @play_locally.before_invoke
    @play.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()

    @commands.command()
    async def urls(self, ctx, url):
        await ctx.send("inside urls")
        opts = {'ignoreerrors': True}
        # ydl =  #'outtmpl': '%(id)s%(ext)s',

        with youtube_dl.YoutubeDL(opts) as ydl:
            await ctx.send("extracting urls")
            result = ydl.extract_info(url=url, download=False) #We just want to extract the info
            print(result.keys())
            if 'entries' in result:
                print('yes')
                print(result['entries'][0]['webpage_url'])
                urls = [entry['webpage_url'] for entry in result['entries'] if entry is not None]
                print(urls)
                await ctx.send('\n'.join(urls))
            else:
                print('no')
                await ctx.send(result['webpage_url'])
            print("this ends now")

def setup(bot):
    bot.add_cog(Music2(bot))
