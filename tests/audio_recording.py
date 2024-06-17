from enum import Enum

import discord
import os
import dotenv
from discord import Forbidden

dotenv.load_dotenv()

bot = discord.Bot(debug_guilds=["Beta"])
connections = {}


class Sinks(Enum):
    mp3 = discord.sinks.MP3Sink()
    wav = discord.sinks.WaveSink()
    pcm = discord.sinks.PCMSink()
    ogg = discord.sinks.OGGSink()
    mka = discord.sinks.MKASink()
    mkv = discord.sinks.MKVSink()
    mp4 = discord.sinks.MP4Sink()
    m4a = discord.sinks.M4ASink()


async def finished_callback(sink, channel: discord.TextChannel, *args):
    recorded_users = [f"<@{user_id}>" for user_id, audio in sink.audio_data.items()]
    await sink.vc.disconnect()
    files = [
        discord.File(audio.file, f"{user_id}.{sink.encoding}")
        for user_id, audio in sink.audio_data.items()
    ]
    await channel.send(
        f"Finished! Recorded audio for {', '.join(recorded_users)}.", files=files
    )



@bot.command()
async def get_channels(ctx, id):
    try:
        guild = await bot.get_guild(id)
    except Forbidden:
        await ctx.send("I do not have access to that guild or it doesn't exist.")
    else:
        for channel in guild.channels:
            print(channel.id)


@bot.command()
async def start(ctx: discord.ApplicationContext, sink: Sinks):
    """Record your voice!"""
    voice = ctx.author.voice

    if not voice:
        return await ctx.respond("You're not in a vc right now")

    vc = await voice.channel.connect()
    connections.update({ctx.guild.id: vc})

    vc.start_recording(
        sink.value,
        finished_callback,
        ctx.channel,
    )

    await ctx.respond("The recording has started!")


@bot.command()
async def stop(ctx: discord.ApplicationContext):
    """Stop recording."""
    if ctx.guild.id in connections:
        vc = connections[ctx.guild.id]
        vc.stop_recording()
        del connections[ctx.guild.id]
        await ctx.delete()
    else:
        await ctx.respond("Not recording in this guild.")


bot.run(os.environ["DISCORD_TOKEN"])
