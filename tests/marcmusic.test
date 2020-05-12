from async_timeout import timeout
import asyncio
import itertools
import youtube_dl
import discord
import itertools
import functools
import time

from discord.ext import commands

# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''

class VoiceConnectionError(commands.CommandError):
    """Custom Exception class for connection errors."""


class NotConnectedMember(VoiceConnectionError):
    """Exception for cases of not connected member."""

class InvalidVoiceChannel(VoiceConnectionError):
    """Exception for cases of invalid Voice Channels."""

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
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, audio, *, data, requester, volume=0.5):
        super().__init__(audio, volume)
        self.data = data
        self.requester = requester

    @property
    def title(self):
        return self.data.get('title')

    @property
    def url(self):
        return self.data.get('url')

    @classmethod
    async def from_url(cls, url, *, requester, loop, download):
        """Create a source from url either it's streamed or not."""
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=download))
        if 'entries' in data: #It should not happen because the source is pre-treated
            data = data['entries'][0]
        filename = data['url'] if not download else ytdl.prepare_filename(data)
        audio = discord.FFmpegPCMAudio(filename, **ffmpeg_options)
        return cls(audio, data=data, requester=requester)

    @classmethod
    async def from_data(cls, data, *, requester, download):
        """Create a source from data either it's streamed or not."""
        if 'entries' in data: #It should not happen because the source is pre-treated
            data = data['entries'][0]
        filename = data['url'] if not download else ytdl.prepare_filename(data)
        audio = discord.FFmpegPCMAudio(filename, **ffmpeg_options)
        return cls(audio, data=data, requester=requester)

    @classmethod
    async def regather_stream(cls, source, *, loop):
        """Used for preparing a stream, instead of downloading.
        Since Youtube Streaming links expire."""
        requester = source.requester
        to_run = functools.partial(ytdl.extract_info, url=source.data['webpage_url'], download=False)
        data = await loop.run_in_executor(None, to_run)
        audio = discord.FFmpegPCMAudio(data['url'])
        return cls(audio, data=data, requester=requester)


class Player:
    def __init__(self,
            ctx, #Easy way of getting references
            volume=5.0, #Volume not to loud
            download=False, #Stream is better than download
            time_before_timeout=5*60, #5 minutes
            time_before_expiration=30, #30 seconds
        ):
        #Necessary references to use in an asyncio queue
        self._bot = ctx.bot
        self._guild = ctx.guild
        self._channel = ctx.channel
        self._cog = ctx.cog
        #Download ou stream
        self.volume = volume
        self.download = download
        self.time_before_timeout = time_before_timeout
        self.time_before_expiration = time_before_expiration
        #Historics
        self.search_historic = []
        self.historic = []
        #Asyncio
        self.queue = asyncio.Queue()
        self.next = asyncio.Event()
        #Buffers
        self.current = None #Current music
        self.np = None #Now playing message, displayed as long as the current music is being played
        self.time = time.time() #Keep track of time for expirations

    def start(self):
        self._bot.loop.create_task(self.player_loop())

    async def put_url(self, ctx, *, url, loop, requester):
        """Put a url into the queue."""
        async with ctx.typing():
            source = await YTDLSource.from_url(url=url, requester=requester, loop=loop, download=self.download)
            await self.queue.put(source)

    async def player_loop(self):
        """Our main player loop."""
        await self._bot.wait_until_ready()

        while not self._bot.is_closed():
            self.next.clear()
            try:
                # Wait for the next song. If we timeout cancel the player and disconnect...
                async with timeout(self.time_before_timeout):  # 5 minutes...
                    source = await self.queue.get()
            except asyncio.TimeoutError:
                return self.destroy(self._guild)

            if not self.download:
                print("regathering")
                # We must regather to prevent stream expiration
                try:
                    source = await YTDLSource.regather_stream(source, loop=self._bot.loop)
                except Exception as e:
                    await self._channel.send(f'Une erreur s\'est produite, vérifier votre connexion.\n'
                                             f'```css\n[{e}]\n```')
                    continue

            source.volume = self.volume
            self.current = source

            self._guild.voice_client.play(source, after=lambda _: self._bot.loop.call_soon_threadsafe(self.next.set))
            np = await self._channel.send(f'**Now Playing:** `{source.title}` requested by '
                                               f'`{source.requester}`')
            await self.next.wait()

            # Make sure the FFmpeg process is cleaned up.
            source.cleanup()
            self.current = None
            try:
                # We are no longer playing this song...
                await self.np.delete()
            except discord.HTTPException:
                pass

    def destroy(self, guild):
        """Disconnect and cleanup the player."""
        return self.bot.loop.create_task(self._cog.cleanup(guild))

class marcMusic(commands.Cog):
    def __init__(self, bot, download=False):

        self.bot = bot
        self.players = {}
        self.download = download

    async def cleanup(self, guild):
        """Disconnect client and delete player."""
        try:
            await guild.voice_client.disconnect()
        except AttributeError:
            pass
        if guild.id in self[players]:
            del self.players[guild.id]

    def get_player(self, ctx):
        """Retrieve the guild player, or generate one."""
        if ctx.guild.id in self.players:
            player = self.players[ctx.guild.id]
        else:
            player = Player(ctx, download=self.download)
            player.start()
            self.players[ctx.guild.id] = player
        return player

    @commands.command(name='marcplay')
    async def play(self, ctx, *, search: str):
        """Ajoute une musique à la queue."""
        await ctx.trigger_typing()
        vc = ctx.voice_client
        player = self.get_player(ctx)
        urls = self.extract_urls(search)
        player.search_historic.append(search)
        player.historic += urls
        for url in urls:
            print("url:", url)
            await player.put_url(ctx, url=url,loop=self.bot.loop, requester=ctx.author)
        print("player is set")

    @commands.command(name='marcqueue')
    async def queue_info(self, ctx):
        """Donne la queue des prochaines musiques."""
        vc = ctx.voice_client
        if not vc or not vc.is_connected():
            return await ctx.send('Je ne suis pas connecté au salon vocal!', delete_after=20)
        player = self.get_player(ctx)
        if player.queue.empty():
            return await ctx.send('La queue est vide.')
        # Grab up to 5 entries from the queue...
        upcoming = list(itertools.islice(player.queue._queue, 0, 5))
        description = '\n'.join(f'**`{_["title"]}`**' for _ in upcoming)
        embed = discord.Embed(title=f'Musiques suivantes {len(upcoming)}', description=description)
        await ctx.send(embed=embed)

    @commands.command(name='marcencours')
    async def now_playing_(self, ctx):
        """Informe sur la musique en cours."""
        vc = ctx.voice_client
        if not vc or not vc.is_connected():
            return await ctx.send('Je ne suis pas connecté au salon vocal!', delete_after=20)
        player = self.get_player(ctx)
        if not player.current:
            return await ctx.send('Je ne joue rien pour l\'instant!')
        try:
            await player.np.delete()
        except discord.HTTPException:
            pass
        player.np = await ctx.send(f'**Je joue:** `{vc.source.title}` '
                                   f'demandé par `{vc.source.requester}`')

    def extract_urls(self, search):
        """Extrait les urls d'une recherche."""
        opts_info = {'ignoreerrors': True}
        ytdl_info = youtube_dl.YoutubeDL(opts_info)
        with ytdl_info:
            result = ytdl_info.extract_info(url=search, download=False) #We just want to extract the info
        if 'entries' in result:
            urls = [entry['webpage_url'] for entry in result['entries'] if entry is not None]
        else:
            urls = [result['webpage_url']]
        return urls

    @commands.command(name="marcurls")
    async def urls(self, ctx, search):
        """Affiche tous les urls d'une recherche."""
        urls = self.extract_urls(search=search)
        msg = '\n'.join(urls)
        await ctx.send(msg)

    @commands.command(name='marcjoin')
    async def join(self, ctx, *, channel:discord.VoiceChannel=None):
        """Se connecte à un salon vocal"""
        if not channel:
            if ctx.author.voice:
                channel = ctx.author.voice.channel
            else:
                raise InvalidVoiceChannel(
                            "Il n'y a pas de salon vocal à rejoindre."
                            "Vous devez soit spécifier le salon vocal, soit en rejoindre un."
                )
        vc = ctx.voice_client
        if vc:
            if vc.channel.id == channel.id:
                return
            try:
                await vc.move_to(channel)
            except asyncio.TimeoutError:
                raise VoiceConnectionError(f'Connection au salon vocal: <{channel}> expirée.')
        else:
            try:
                await channel.connect()
            except asyncio.TimeoutError:
                raise VoiceConnectionError(f'Connection au salon vocal: <{channel}> expirée.')
        await ctx.send(f'Connecté à: **{channel}**', delete_after=20)

    @commands.command(name='marcskip')
    async def skip(self, ctx):
        """Passe à la musique suivante."""
        vc = ctx.voice_client
        if not vc or not vc.is_connected():
            return await ctx.send('Je ne joue rien pour le moment.', delete_after=20)
        if vc.is_paused():
            pass
        elif not vc.is_playing():
            return
        vc.stop()
        await ctx.send(f'**`{ctx.author}`**: a skip la musique.')

    @commands.command(name="marcvolume")
    async def volume(self, ctx, volume: int):
        """Choisi le volume du player."""
        ctx.voice_client.source.volume = volume / 100
        await ctx.send(f"Volume: {volume}%", delete_after=20)

    @commands.command(name="marcpause")
    async def pause(self, ctx):
        """Fais pause."""
        ctx.voice_client.pause()
        await ctx.send(f"Pause", delete_after=20)


    @commands.command(name="marcresume")
    async def resume(self, ctx):
        """Reprends la musique."""
        ctx.voice_client.resume()
        await ctx.send(f"Reprise", delete_after=20)

    @commands.command(name="marcstop")
    async def stop(self, ctx):
        """Stops and disconnects the bot from voice"""
        await ctx.voice_client.disconnect()
        await ctx.send("Déconnecté.", delete_after=20)

    @volume.before_invoke
    @resume.before_invoke
    @stop.before_invoke
    @play.before_invoke
    async def ensure_voice_client(self, ctx):
        """Assure que le client est connecté."""
        if ctx.voice_client is None:
            await self.join(ctx)

def setup(bot):
    bot.add_cog(marcMusic(bot))