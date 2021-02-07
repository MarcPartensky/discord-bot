# -*- coding: utf-8 -*-

"""
Copyright (c) 2019 Valentin B.
A simple music bot written in discord.py using youtube-dl.
Though it's a simple example, music bots are complex and require much time and knowledge until they work perfectly.
Use this as an example or a base for your own bot and extend it as you want. If there are any bugs, please let me know.
Requirements:
Python 3.5+
pip install -U discord.py pynacl youtube-dl
You also need FFmpeg in your PATH environment variable or the FFmpeg.exe binary in your bot's directory on Windows.
"""

import asyncio
import functools
import itertools
import math
import random

import discord
import youtube_dl
from async_timeout import timeout
from discord.ext import commands

# Silence useless bug reports messages
youtube_dl.utils.bug_reports_message = lambda: ""


class VoiceError(Exception):
    pass


class YTDLError(Exception):
    pass


class YTDLSource(discord.PCMVolumeTransformer):
    YTDL_OPTIONS = {
        "format": "bestaudio/best",
        "extractaudio": True,
        "audioformat": "mp3",
        "outtmpl": "%(extractor)s-%(id)s-%(title)s.%(ext)s",
        "restrictfilenames": True,
        "noplaylist": True,
        "nocheckcertificate": True,
        "ignoreerrors": False,
        "logtostderr": False,
        "quiet": True,
        "no_warnings": True,
        "default_search": "auto",
        "source_address": "0.0.0.0",
    }

    FFMPEG_OPTIONS = {
        "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
        "options": "-vn",
    }

    ytdl = youtube_dl.YoutubeDL(YTDL_OPTIONS)

    def __init__(
        self,
        ctx: commands.Context,
        source: discord.FFmpegPCMAudio,
        *,
        data: dict,
        volume: float = 0.5,
    ):
        super().__init__(source, volume)

        self.requester = ctx.author
        self.channel = ctx.channel
        self.data = data

        self.uploader = data.get("uploader")
        self.uploader_url = data.get("uploader_url")
        date = data.get("upload_date")
        self.upload_date = date[6:8] + "." + date[4:6] + "." + date[0:4]
        self.title = data.get("title")
        self.thumbnail = data.get("thumbnail")
        self.description = data.get("description")
        self.duration = self.parse_duration(int(data.get("duration")))
        self.tags = data.get("tags")
        self.url = data.get("webpage_url")
        self.views = data.get("view_count")
        self.likes = data.get("like_count")
        self.dislikes = data.get("dislike_count")
        self.stream_url = data.get("url")

    def __str__(self):
        return "**{0.title}** by **{0.uploader}**".format(self)

    @classmethod
    async def create_source(
        cls, ctx: commands.Context, search: str, *, loop: asyncio.BaseEventLoop = None
    ):
        loop = loop or asyncio.get_event_loop()

        partial = functools.partial(
            cls.ytdl.extract_info, search, download=False, process=False
        )
        data = await loop.run_in_executor(None, partial)

        if data is None:
            raise YTDLError("Aucune résultat ne correspond à `{}`".format(search))

        if "entries" not in data:
            process_info = data
        else:
            process_info = None
            for entry in data["entries"]:
                if entry:
                    process_info = entry
                    break

            if process_info is None:
                raise YTDLError("Aucun résultat ne correspond à `{}`".format(search))

        webpage_url = process_info["webpage_url"]
        partial = functools.partial(cls.ytdl.extract_info, webpage_url, download=False)
        processed_info = await loop.run_in_executor(None, partial)

        if processed_info is None:
            raise YTDLError("Impossible de récupérer `{}`".format(webpage_url))

        if "entries" not in processed_info:
            info = processed_info
        else:
            info = None
            while info is None:
                try:
                    info = processed_info["entries"].pop(0)
                except IndexError:
                    raise YTDLError(
                        "Impossible de récupérer de résultat pour `{}`".format(
                            webpage_url
                        )
                    )

        return cls(
            ctx, discord.FFmpegPCMAudio(info["url"], **cls.FFMPEG_OPTIONS), data=info
        )

    @classmethod
    async def create_sources(
        cls, ctx: commands.Context, search: str, *, loop: asyncio.BaseEventLoop = None
    ):
        loop = loop or asyncio.get_event_loop()

        partial = functools.partial(
            cls.ytdl.extract_info, search, download=False, process=False
        )
        data = await loop.run_in_executor(None, partial)

        if data is None:
            raise YTDLError("Aucun résultat ne correspond à `{}`".format(search))

        if "entries" not in data:
            process_info_list = [data]
        else:
            process_info_list = list(data["entries"])
            for process_info in process_info_list:
                process_info["webpage_url"] = (
                    "https://www.youtube.com/watch?v=" + process_info["url"]
                )

            if process_info_list is None:
                raise YTDLError("Aucun résultat ne correspond à `{}`".format(search))

        sources = []
        for process_info in process_info_list:
            try:
                webpage_url = process_info["webpage_url"]
                partial = functools.partial(
                    cls.ytdl.extract_info, webpage_url, download=False
                )
                processed_info = await loop.run_in_executor(None, partial)

                if processed_info is None:
                    raise YTDLError("Impossible de récupérer `{}`".format(webpage_url))

                if "entries" not in processed_info:
                    info = processed_info
                else:
                    info = None
                    while info is None:
                        try:
                            info = processed_info["entries"].pop(0)
                        except IndexError:
                            raise YTDLError(
                                "Impossible de récupérer de résultat pour `{}`".format(
                                    webpage_url
                                )
                            )
                source = cls(
                    ctx,
                    discord.FFmpegPCMAudio(info["url"], **cls.FFMPEG_OPTIONS),
                    data=info,
                )
                sources.append(source)
            except:
                print(f"{webpage_url} n'est pas disponible")
        return sources

    @staticmethod
    def parse_duration(duration: int):
        minutes, seconds = divmod(duration, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)

        duration = []
        if days > 0:
            duration.append("{} jours".format(days))
        if hours > 0:
            duration.append("{} heures".format(hours))
        if minutes > 0:
            duration.append("{} minutes".format(minutes))
        if seconds > 0:
            duration.append("{} secondes".format(seconds))

        return ", ".join(duration)


class Song:
    __slots__ = ("source", "requester")

    def __init__(self, source: YTDLSource):
        self.source = source
        self.requester = source.requester

    def create_embed(self):
        embed = (
            discord.Embed(
                title="En cours:",
                description="```ini\n[{0.source.title}]\n```".format(self),
                color=discord.Color.gold(),
            )
            .add_field(name="Durée", value=self.source.duration)
            .add_field(name="Demandée par", value=self.requester.mention)
            .add_field(
                name="Uploader",
                value="[{0.source.uploader}]({0.source.uploader_url})".format(self),
            )
            .add_field(name="URL", value="[Click]({0.source.url})".format(self))
            .add_field(
                name="Likes/Dislikes",
                value=f"{self.source.likes}/{self.source.dislikes}",
            )
            #  .add_field(name='Dislikes', value=self.source.dislikes)
            .add_field(name="Vues", value=self.source.views)
            .set_thumbnail(url=self.source.thumbnail)
        )

        return embed


class SongQueue(asyncio.Queue):
    def __getitem__(self, item):
        if isinstance(item, slice):
            return list(itertools.islice(self._queue, item.start, item.stop, item.step))
        else:
            return self._queue[item]

    def __iter__(self):
        return self._queue.__iter__()

    def __len__(self):
        return self.qsize()

    def clear(self):
        self._queue.clear()

    def shuffle(self):
        random.shuffle(self._queue)

    def remove(self, index: int):
        del self._queue[index]


class VoiceState:
    def __init__(self, bot: commands.Bot, ctx: commands.Context):
        self.bot = bot
        self._ctx = ctx

        self.current = None
        self.voice = None
        self.next = asyncio.Event()
        self.songs = SongQueue()

        self._loop = False
        self._volume = 0.5
        self.skip_votes = set()
        self.skip_votes_number = 3

        self.search_historic = []
        self.historic = []

        self.audio_player = bot.loop.create_task(self.audio_player_task())

    def __del__(self):
        self.audio_player.cancel()

    @property
    def loop(self):
        return self._loop

    @loop.setter
    def loop(self, value: bool):
        self._loop = value

    @property
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, value: float):
        self._volume = value

    @property
    def is_playing(self):
        return self.voice and self.current

    async def audio_player_task(self):
        while True:
            self.next.clear()

            if not self.loop:
                # Try to get the next song within 3 minutes.
                # If no song will be added to the queue in time,
                # the player will disconnect due to performance
                # reasons.
                try:
                    async with timeout(180):  # 3 minutes
                        self.current = await self.songs.get()
                except asyncio.TimeoutError:
                    self.bot.loop.create_task(self.stop())
                    return

            self.current.source.volume = self._volume
            self.voice.play(self.current.source, after=self.play_next_song)
            await self.current.source.channel.send(embed=self.current.create_embed())

            await self.next.wait()

    def play_next_song(self, error=None):
        if error:
            raise VoiceError(str(error))

        self.next.set()

    def skip(self):
        self.skip_votes.clear()

        if self.is_playing:
            self.voice.stop()

    async def stop(self):
        self.songs.clear()

        if self.voice:
            await self.voice.disconnect()
            self.voice = None


class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.voice_states = {}
        self.color = discord.Color(0xFF66CC)  # pink

    def get_voice_state(self, ctx: commands.Context):
        state = self.voice_states.get(ctx.guild.id)
        if not state:
            state = VoiceState(self.bot, ctx)
            self.voice_states[ctx.guild.id] = state
        return state

    def cog_unload(self):
        for state in self.voice_states.values():
            self.bot.loop.create_task(state.stop())

    def cog_check(self, ctx: commands.Context):
        if not ctx.guild:
            raise commands.NoPrivateMessage(
                "Cette commande ne peut pas être exécutée en conversation privée."
            )
        return True

    async def cog_before_invoke(self, ctx: commands.Context):
        ctx.voice_state = self.get_voice_state(ctx)

    @commands.command(name="save")
    async def _save(self, ctx: commands.Context, name: str = None):
        """Sauve la playliste avec un nom."""
        voice_state = self.voice_states[ctx.guild.id]
        urls = [voice_state.current.source.url]
        for song in voice_state.songs:
            urls.append(song.source.url)
        await ctx.send("\n".join(urls))

    def urls(self, ctx: commands.Context):
        """Renvoie la liste des tous les urls."""
        voice_state = self.voice_states[ctx.guild.id]
        urls = [voice_state.current.source.url]
        for song in voice_state.songs:
            urls.append(song.source.url)
        return urls

    @commands.command(name="time-left", aliases=["temps-restant"])
    async def _time_left(self, ctx: commands.Context):
        """Affiche une estimation du temps restant."""
        raise NotImplemented
        # estimated_time = sum(e.duration for e in islice(self.entries, position - 1))
        player = self.get_player()
        estimated_time = player.estimate_time()
        msg = f"Le temps restant est {estimated_time}"
        await ctx.send(msg)

    @commands.command(name="join", invoke_without_subcommand=True, aliases=["rejoins"])
    async def _join(self, ctx: commands.Context):
        """Rejoins un salon vocal."""
        destination = ctx.author.voice.channel
        if ctx.voice_state.voice:
            await ctx.voice_state.voice.move_to(destination)
            return
        ctx.voice_state.voice = await destination.connect()

    @commands.command(name="summon", aliases=["viens"])
    async def _summon(
        self, ctx: commands.Context, *, channel: discord.VoiceChannel = None
    ):
        """Demande le bot dans le salon vocal
        Si aucun salon n'est précisé, le bot rejoins votre salon.
        """
        print(ctx.voice_state)
        if not channel and not ctx.author.voice:
            raise VoiceError("Vous n'avez ni spécifier de salon vocal ni rejoins un.")
        destination = channel or ctx.author.voice.channel
        if ctx.voice_state.voice:
            await ctx.voice_state.voice.move_to(destination)
            return
        ctx.voice_state.voice = await destination.connect()

    @commands.command(name="leave", aliases=["disconnect", "quitte"])
    async def _leave(self, ctx: commands.Context):
        """Nettoie la queue, quitte le salon vocal."""
        if not ctx.voice_state.voice:
            return await ctx.send("Pas connecté à un salon vocal.")
        await ctx.voice_state.stop()
        del self.voice_states[ctx.guild.id]

    @commands.command(name="volume")
    async def _volume(self, ctx: commands.Context, *, volume: int):
        """Change le volume de la playliste."""
        if not ctx.voice_state.is_playing:
            return await ctx.send("Aucune musique n'est jouée pour le moment.")
        if 0 > volume > 100:
            return await ctx.send("Le son doit être compris entre 0 et 100.")
        ctx.voice_state.volume = volume / 100
        await ctx.send("Le volume de la playliste est réglé à {}%".format(volume))

    @commands.command(name="now", aliases=["current", "playing", "maintenant", "mtn"])
    async def _now(self, ctx: commands.Context):
        """Affiche la musique en cours."""
        await ctx.send(embed=ctx.voice_state.current.create_embed())

    @commands.command(name="left", aliases=["restant"])
    async def _left(self, ctx: commands.Context):
        """Affiche le nombre de musiques restantes."""
        try:
            await ctx.send(f"Il reste {ctx.voice_state.queue.qsize()} musiques.")
        except AttributeError:
            await ctx.send(f"La queue est vide.")

    @commands.command(name="pause")
    async def _pause(self, ctx: commands.Context):
        """Pause la musique en cours."""
        if not ctx.voice_state.is_playing and ctx.voice_state.voice.is_playing():
            ctx.voice_state.voice.pause()
            await ctx.message.add_reaction("⏯")

    @commands.command(name="resume", aliases=["reprends"])
    async def _resume(self, ctx: commands.Context):
        """Reprends la musique en cours."""
        if not ctx.voice_state.is_playing and ctx.voice_state.voice.is_paused():
            ctx.voice_state.voice.resume()
            await ctx.message.add_reaction("⏯")

    @commands.command(name="stop")
    async def _stop(self, ctx: commands.Context):
        """Stop la musique et nettoie la queue."""
        ctx.voice_state.stop()
        ctx.voice_state.current = None
        ctx.voice_state.songs.clear()
        if not ctx.voice_state.is_playing:
            ctx.voice_state.voice.stop()
            await ctx.message.add_reaction("⏹")

    @commands.command(name="skip", aliases=["next", "suivant"])
    async def _skip(self, ctx: commands.Context):
        """Vote pour passer une musique.
        un certain nombre de votes sont nécessaires pour
        passer une musique, sauf pour le demandeur."""
        if not ctx.voice_state.is_playing:
            return await ctx.send("Je ne joue pas de musique pour le moment")
        voter = ctx.message.author
        if voter == ctx.voice_state.current.requester:
            await ctx.message.add_reaction("⏭")
            ctx.voice_state.skip()
        elif voter.id not in ctx.voice_state.skip_votes:
            ctx.voice_state.skip_votes.add(voter.id)
            total_votes = len(ctx.voice_state.skip_votes)
            if total_votes >= ctx.voice_state.skip_votes_number:
                await ctx.message.add_reaction("⏭")
                ctx.voice_state.skip()
            else:
                await ctx.send(
                    "Le compte de vote est maintenant à **{}/3**".format(total_votes)
                )
        else:
            await ctx.send("Vous avez voté pour changer de musique.")

    @commands.command(name="queue")
    async def _queue(self, ctx: commands.Context, *, page: int = 1):
        """Affiche la queue à une page."""
        voice_state = self.voice_states[ctx.guild.id]
        if voice_state.current:
            songs = [voice_state.current]
        else:
            songs = []
        songs += list(voice_state.songs)
        if len(songs) == 0:
            return await ctx.send("Queue vide.")
        items_per_page = 10
        pages = math.ceil(len(songs) / items_per_page)
        start = (page - 1) * items_per_page
        end = start + items_per_page
        queue = []
        for i, song in enumerate(songs[start:end], start=start):
            if i == 0:
                queue.append(
                    "`mtn` [**{0.source.title}**]({0.source.url})".format(song)
                )
            else:
                queue.append(
                    "`{0}.` [**{1.source.title}**]({1.source.url})".format(i, song)
                )
        m = len(max(queue, key=lambda s: len(s)))
        description = f"{len(songs)} Musiques"
        n = max((m - len(description) // 2) // 6, 0)
        description = f"```fix\n{' '*n}{description}{' '*n}\n```"
        description = "\n".join([description] + queue)
        embed = discord.Embed(description=description, color=self.color).set_footer(
            text="Page regardée {}/{}".format(page, pages)
        )
        await ctx.send(embed=embed)

    @commands.command(name="shuffle", aliases=["mélange", "shake"])
    async def _shuffle(self, ctx: commands.Context):
        """Mélange la queue."""
        if len(ctx.voice_state.songs) == 0:
            return await ctx.send("Queue vide.")
        ctx.voice_state.songs.shuffle()
        await ctx.message.add_reaction("✅")

    @commands.command(name="remove", aliases=["retire", "enlève"])
    async def _remove(self, ctx: commands.Context, index: int):
        """Retire une musique avec un numéro."""
        if len(ctx.voice_state.songs) == 0:
            return await ctx.send("Queue vide.")
        ctx.voice_state.songs.remove(index - 1)
        await ctx.message.add_reaction("✅")

    @commands.command(name="loop", aliases=["boucle"])
    async def _loop(self, ctx: commands.Context):
        """Joue en boucle la musique en cours.
        Pour arrêter la boucle, retapez la commande."""
        if not ctx.voice_state.is_playing:
            return await ctx.send("Nothing being played at the moment.")
        # Inverse boolean value to loop and unloop.
        ctx.voice_state.loop = not ctx.voice_state.loop
        await ctx.message.add_reaction("✅")

    @commands.command(name="play")
    async def _play(self, ctx: commands.Context, *, search: str):
        """Joue une musique.
        Si il y'a d'autres musiques dans la queue, la musique sera placée
        dans la queue jusqu'à ce que les musiques précédentes se finissent
        Cette commande cherche sur divers sites si aucun url n'est fourni.
        Une liste de cette site peut être trouvée sur:
        https://rg3.github.io/youtube-dl/supportedsites.html
        """
        if not ctx.voice_state.voice:
            await ctx.invoke(self._join)
        async with ctx.typing():
            try:
                sources = await YTDLSource.create_sources(
                    ctx, search, loop=self.bot.loop
                )
            except YTDLError as e:
                await ctx.send(
                    "Une erreur s'est produite pendant le traitement de: {}".format(
                        str(e)
                    )
                )
            else:
                first = True
                for source in sources:
                    song = Song(source)
                    await ctx.voice_state.songs.put(song)
                    content = "Ajoutée à la queue {}".format(str(source))
                    if first:
                        first = False
                        message = await ctx.send(content=content)
                    else:
                        await message.edit(content=content)

    @_join.before_invoke
    async def ensure_voice_state(self, ctx: commands.Context):
        if not ctx.author.voice or not ctx.author.voice.channel:
            raise commands.CommandError("Vous n'êtes pas connecté à un salon vocal.")
        if ctx.voice_client:
            if ctx.voice_client.channel != ctx.author.voice.channel:
                raise commands.CommandError("Le bot est déjà dans un salon vocal.")
        print("voice_state ok")


def setup(bot):
    bot.add_cog(Music(bot))
