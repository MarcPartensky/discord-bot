"""Monitor voice channels."""

import os
import logging
from typing import List

import discord
from discord.ext import commands
from rich import print

from config.config import masters

logging.basicConfig(level=logging.INFO)


class VoiceChannel(commands.Cog):
    """Monitor voice channels."""

    def __init__(self, bot: commands.Bot, **kwargs):
        """Initialize the cog."""
        super().__init__(**kwargs)
        self.bot = bot
        self.role = "Voix"
        self.color = discord.Color.teal()
        self.notify_channel_id: int = os.environ.get("CHNOTIF")
        self.tmp_channel_name = "Temporaire"

    async def get_bot_member(self, guild: discord.Guild):
        """Return the member object of the bot."""
        return guild.fetch_member(self.bot.user.id)

    async def create_role_if_missing(self, guild: discord.Guild):
        """Create the voice role if it doesn't already exist."""
        if self.role in [role.name for role in guild.roles]:
            return
        # Create the role
        role = await guild.create_role(name=self.role, colour=self.color)
        # Add the role to all the masters
        for master in masters:
            if member := await guild.fetch_member(master):
                if self.role in [role.name for role in member.roles]:
                    print(member, member.id, master)
                    await member.add_roles(role)

    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState,
    ):
        """Detect any changes on voice channels"""
        await self.create_role_if_missing(member.guild)
        if member.bot:
            return
        # if after.channel.id == channel_id and not member.bot:
        #     voice_client = await channel.connect()
        if not after.channel:
            await self.leave(member, before)
        elif not before.channel:
            await self.join(member, after)
        else:
            await self.move(member, before, after)
        # after_channel: discord.VoiceChannel = after.channel
        # after_members: typing.List[discord.Member] = after_channel.members
        # before_channel: discord.VoiceChannel = before.channel
        # before_members: typing.List[discord.Member] = before_channel.members
        # print(member, before, after)
        # # if len(members) == 1:
        # print(after_members)
        # print(before_members)

    async def leave(
        self,
        member: discord.Member,
        before: discord.VoiceState,
    ):
        """Detect when a user leaves."""
        logging.info("leave")
        logging.info(member)
        logging.info(before)
        channel: discord.VoiceChannel = before.channel
        members: List[discord.Member] = channel.members
        await self.mute_if_single(members)
        await self.leave_if_alone(members, before.channel)

    async def join(
        self,
        member: discord.Member,
        after: discord.VoiceState,
    ):
        """Detect when a user leaves."""
        logging.info("join")
        logging.info(member)
        logging.info(after)
        channel: discord.VoiceChannel = after.channel
        members: List[discord.Member] = channel.members
        await self.mute_if_single(members)
        await self.notify_on_join(member)
        await self.join_if_single(members)

    async def move(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState,
    ):
        """Detect when a user leaves."""
        logging.info("move")
        logging.info(member)
        logging.info(before)
        logging.info(after)
        before_channel: discord.VoiceChannel = before.channel
        before_members: List[discord.Member] = before_channel.members
        after_channel: discord.VoiceChannel = after.channel
        after_members: List[discord.Member] = after_channel.members
        await self.mute_if_single(before_members)
        await self.join_if_single(after_members)

    async def mute_if_single(self, members: List[discord.Member]):
        """Mute a member if single."""
        logging.info("mute if single")
        logging.info(members)
        members = list(filter(lambda m: not m.bot, members))
        if len(members) != 1:
            return
        member = members[0]
        if member.voice:
            if self.role in map(lambda r: r.name, member.roles):
                print(member.voice)
                await member.edit(mute=True)

    async def join_if_single(self, members: List[discord.Member]):
        """Mute a member if single."""
        logging.info("join if single")
        logging.info(members)
        members = list(filter(lambda m: not m.bot, members))
        if len(members) != 1:
            return
        member = members[0]
        destination = member.voice.channel
        for voice_client in self.bot.voice_clients:
            if voice_client.channel.id == member.voice.channel.id:
                return
            elif voice_client.channel in member.guild.voice_channels:
                await voice_client.move_to(destination)
                return
        print(destination.members)
        print(repr(destination))
        if self.bot.user.id not in [m.id for m in destination.members]:
            print(await destination.connect())
            print(destination.members)

    async def notify_on_join(self, member: discord.Member):
        """Notify me if a member joins."""
        logging.info("notify on join")
        logging.info(member)
        if member.id in masters:
            return
        if member.bot:
            return
        chan_id = self.notify_channel_id
        channel: discord.TextChannel = await self.bot.fetch_channel(chan_id)
        await channel.send(f"> **{member}** a rejoint **{channel}**.", delete_after=60)

    async def leave_if_alone(
        self, members: List[discord.Member], channel: discord.VoiceChannel
    ):
        """Mute a member if single."""
        logging.info("leave if alone")
        true_members = list(filter(lambda m: not m.bot, members))
        if len(true_members) > 0:
            return
        bot_search_results = list(filter(lambda m: m.id == self.bot.user.id, members))
        print(bot_search_results)
        if len(bot_search_results) == 0:
            return
        for voice_client in self.bot.voice_clients:
            if voice_client.channel.id == channel.id:
                await voice_client.disconnect()
                break
        # tmp_channel = await guild.create_voice_channel(name=self.tmp_channel_name)
        # await bot_member.move_to(tmp_channel)
        # await tmp_channel.delete()


def setup(bot):
    bot.add_cog(VoiceChannel(bot))
