from discord.ext import commands
import discord

from utils import tools
from config.config import access, masters


class Code(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot
        self.repeat_limit = 5

    @commands.command(name="exec", aliases=["exe", "x"])
    @access.admin
    async def execute(self, ctx, *, cmd):
        """Exécute une commande."""
        if '|' in cmd:
            cmd, args = cmd.split('|')
            args = args.split(',')
            cmd = tools.parse(cmd, *args)
        with tools.Capturing() as out:
            exec(cmd, globals(), locals())
        await ctx.send("\n".join(out))

    @commands.command(name="eval", aliases=["v"])
    @access.admin
    async def evaluate(self, ctx:commands.Context, *, cmd:str):
        """Evalue une commande."""
        if '|' in cmd:
            cmd, args = cmd.split('|')
            args = args.split(',')
            cmd = tools.parse(cmd, *args)
        try:
            await ctx.send(eval(cmd))
        except Exception as e:
            await ctx.send(e)

    @commands.command(aliases=["c"])
    @access.admin
    async def code(self, ctx:commands.Context, *, cmd:str):
        """Evalue ou exécute une commande."""
        if '|' in cmd:
            cmd, args = cmd.split('|')
            args = args.split(',')
            cmd = tools.parse(cmd, *args)
        try:
            await ctx.send(eval(cmd))
        except Exception as e:
            try:
                with tools.Capturing() as out:
                    exec(cmd, globals(), locals())
                await ctx.send("\n".join(out))
            except Exception as e:
                await ctx.send(cmd)

    @commands.command(name='répète', aliases=['rp', 'repeat'])
    async def repeat(self, ctx:commands.Context, n:int=1, member:discord.Member=None):
        """Répète les n derniers messages d'un membre.
        Cela permet de facilité le développement du bot."""
        user = member or ctx.author
        if ctx.author.id not in masters:
            if n>self.repeat_limit:
                msg = f"Vous êtes limités à {self.repeat_limit} messages."
                return await ctx.send(msg)
        await ctx.message.delete()
        lines = []
        i = 0
        async for message in ctx.channel.history():
            if i>=n:
                break
            if user.id == message.author.id:
                i += 1
                line = f"> "+message.content
                lines.append(line)
        msg = '\n'.join(reversed(lines))
        await ctx.send(msg)





def setup(bot):
    bot.add_cog(Code(bot))