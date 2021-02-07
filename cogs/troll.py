from discord.ext import commands
import discord


class Troll(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="nyan-cat", aliases=["nyan"])
    async def nyan_cat(
        self,
        ctx: commands.Context,
        channel: discord.VoiceChannel,
        *members: discord.Member
    ):
        """Mets du nyan cat."""
        await ctx.message.delete()
        music = self.bot.get_cog("Music")
        ctx.voice_state = music.get_voice_state(ctx)
        await music._summon(ctx, channel=channel)
        await music._play(ctx, search="nyan cat 10 hours")
        for member in members:
            member.move_to(channel)

    @commands.command()
    async def spam(self, ctx: commands.Context, *members: discord.Member):
        """Spam des membres dès qu'ils parlent."""
        await ctx.send("En développement")


def setup(bot):
    bot.add_cog(Troll(bot))
