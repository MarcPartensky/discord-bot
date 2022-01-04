"""Monitor voice channels."""

from typing import List
import discord
from discord.ext import commands
from discord import Message, PartialEmoji
from utils.date


class VoiceChannel(commands.Cog):
    """Monitor voice channels."""

    def __init__(self, bot: commands.Bot, **kwargs):
        """Initialize the cog."""
        super().__init__(**kwargs)
        self.bot = bot
        self.role = "Voix"



    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState,
    ):
        """Detect any changes on voice channels"""
        # if after.channel.id == channel_id and not member.bot:
        #     voice_client = await channel.connect()
        self.
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
        print("leave")
        print(member, before)
        channel: discord.VoiceChannel = before.channel
        members: List[discord.Member] = channel.members
        self.mute_if_single(members)

    async def join(
        self,
        member: discord.Member,
        after: discord.VoiceState,
    ):
        """Detect when a user leaves."""
        print(member, after)
        channel: discord.VoiceChannel = after.channel
        members: List[discord.Member] = channel.members
        self.mute_if_single(members)

    async def move(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState,
    ):
        """Detect when a user leaves."""
        print(member, before, after)
        before_channel: discord.VoiceChannel = before.channel
        members: List[discord.Member] = before_channel.members
        self.mute_if_single(members)
        self.join_if_single(members)

    def mute_if_single(self, members: List[discord.Member]):
        """Mute a member if single."""
        members = list(filter(lambda m: not m.bot, members))
        if len(members) == 1:
            member = members[0]
            if self.role in map(lambda r: r.name, member.roles):
                member.voice.mute = True

    def join_if_single(self, members: List[discord.Member]):
        """Mute a member if single."""
        members = list(filter(lambda m: not m.bot, members))
        if len(members) == 1:
            member = members[0]
            member.voice.mute = True

    async def join(self, ctx: commands.Context):
        """Rejoins un salon vocal."""
        destination = ctx.author.voice.channel
        if ctx.voice_state.voice:
            await ctx.voice_state.voice.move_to(destination)
            return
        ctx.voice_state.voice = await destination.connect()

    # @commands.command(name="nettoyer-salon", aliases=["nettoyer-chat"])
    # async def notify_on_join(self, ctx: commands.Context):
    #     """Test"""

    # @commands.Cog.listener()
    # async def on_message(self, msg: discord.Message):
    #     """Nettoie les messages des salons innapropriés, dès que
    #     ceux-ci sont postés."""
    #     if msg.author.bot:
    #         return

    # @commands.Cog.listener(name="reaction_add")
    # async def reaction_add(self, reaction, user):
    #     print(reaction, user)
    #     # await msg.channel.send("je vois")


def setup(bot):
    bot.add_cog(VoiceChannel(bot))
