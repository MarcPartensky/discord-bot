from libs.sherlock.sherlock.sherlocktest import search
from discord.ext import commands
import discord


class Sherlock(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def sherlock(self, ctx: commands.Context, *, username: str):
        """Cherche quelqu'un sur internet."""
        msg = await ctx.send(f"> Recherche de {username} en cours.")
        async with ctx.typing():
            results = search(username)
        await msg.delete()
        embed = discord.Embed(color=ctx.author.color)
        txt = ""
        n = 1
        for (name, result) in results.items():
            value = result["url_user"]
            if result["http_status"] == 200:
                if len(txt + name + value) > 6000:
                    embed.set_footer(text=f"n°{n}")
                    await ctx.send(embed=embed)
                    txt = ""
                    n += 1
                    embed = discord.Embed(color=ctx.author.color)
                txt += name + value
                embed.add_field(name=name, value=value)
        embed.set_footer(text=f"n°{n}")
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Sherlock(bot))
