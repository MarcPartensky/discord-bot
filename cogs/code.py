from discord.ext import commands
import discord

from utils import tools
from config.config import access, masters
from config import emoji
import asyncio


class Code(commands.Cog):

    def __init__(self, bot:commands.Bot):
        self.bot = bot
        self.repeat_limit = 5
        self.users_list = []
        self.locals_dict = {}
        self.color = discord.Color.dark_teal()
        self.time_limit = 10 #seconds
        self.time_limit_error_message = f"Vous avez excédé la limite de temps de {self.time_limit} secondes."
        self.activated_message = "Shell python activée."
        self.quit_message = "Shell python déactivée."
        self.globals = globals().copy()

    def get_locals(self, id):
        if id not in self.locals_dict:
            self.locals_dict[id] = {}
        return self.locals_dict[id]

    @commands.command(name="exec", aliases=["exe", "x"])
    @access.admin
    async def execute(self, ctx, *, cmd):
        """Exécute une commande."""
        try:
            with tools.time_limit(self.time_limit):
                if '|' in cmd:
                    cmd, args = cmd.split('|')
                    args = args.split(',')
                    cmd = tools.parse(cmd, *args)
                with tools.Capturing() as out:
                    locals_ = self.get_locals(ctx.author.id)
                    exec(cmd, self.globals, locals_)
                if out:
                    out = ['> '+line for line in out]
                    await ctx.send("\n".join(out))
                    
        except TimeoutError:
            await ctx.send('> '+self.time_limit_error_message)
        except SystemExit:
            del self.users_list[ctx.author.id]
            await ctx.send('> '+self.quit_message)
        except Exception as e:
            await ctx.send('> '+str(e))
            
    @commands.command(name="eval", aliases=["v"])
    @access.admin
    async def evaluate(self, ctx:commands.Context, *, cmd:str):
        """Evalue une commande."""
        try:
            with tools.time_limit(self.time_limit):
                if '|' in cmd:
                    cmd, args = cmd.split('|')
                    args = args.split(',')
                    cmd = tools.parse(cmd, *args)
                try:
                    locals_ = self.get_locals(ctx.author.id)
                    result = eval(cmd, self.globals, locals_)
                    await ctx.send(f"> {result}")
                except Exception as e:
                    await ctx.send('> '+str(e))
        except TimeoutError:
            await ctx.send('> '+self.time_limit_error_message)
        except SystemExit:
            del self.users_list[ctx.author.id]
            await ctx.send('> '+self.quit_message)
        except Exception as e:
            await ctx.send('> '+str(e))

    @commands.command(aliases=["c"])
    @access.admin
    async def code(self, ctx:commands.Context, *, cmd:str):
        """Evalue ou exécute une commande."""
        try:
            with tools.time_limit(self.time_limit):
                if '|' in cmd:
                    cmd, args = cmd.split('|')
                    args = args.split(',')
                    cmd = tools.parse(cmd, *args)
                try:
                    locals_ = self.get_locals(ctx.author.id)
                    result = eval(cmd, self.globals, locals_)
                    await ctx.send(f"> {result}")
                except Exception as e:
                    try:
                        with tools.Capturing() as out:
                            locals_ = self.locals_dict[ctx.author.id]
                            exec(cmd, globals(), locals_)
                        if out:
                            out = ['> '+line for line in out]
                            await ctx.send("\n".join(out))
                    except Exception as e:
                        await ctx.send(cmd)
        except TimeoutError:
            await ctx.send('> '+self.time_limit_error_message)
        except SystemExit:
            del self.users_list[ctx.author.id]
            await ctx.send('> '+self.quit_message)
        except Exception as e:
            await ctx.send('> '+str(e))
    
    @commands.command(name="locals")
    async def locals_(self, ctx:commands.Context):
        """Affiche les variables de la shell."""
        embed = discord.Embed(title="Variables", color=self.color)
        for k,v in self.locals.items():
            embed.add_field(name=k, value=v)
        await ctx.send(embed=embed)

    @commands.command(name="python", aliases=['shell', 'p'])
    async def python(self, ctx:commands.Context):
        """Utilise la shell python sans commandes."""
        self.users_list.append(ctx.author.id)
        await ctx.send(self.activated_message)

    @commands.Cog.listener(name="on_message")
    async def on_message(self, msg:discord.Message):
        """Lis tout les messages"""
        if msg.author == self.bot.user: return
        code = msg.content.replace('```python\n','').replace('```py\n','').replace('```','')
        class ctx:
            send = msg.channel.send
            author = msg.author
        if ctx.author.id in self.users_list:
            if msg.content=="?python":
                pass
            else:
                await self.execute(ctx, cmd=code)
        elif msg.content.startswith('```python\n') or msg.content.startswith('```py\n'):
            emojis = [emoji.play, emoji.cross]
            for emoji_ in emojis:
                await msg.add_reaction(emoji=emoji_)
            def check(reaction, user):
                return (not user.bot and
                    user==msg.author and
                    str(reaction.emoji) in emojis)
            class DestroyReactions(Exception):
                """Destroy the reactions."""
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
                if str(reaction.emoji)==emoji.play:
                    await self.execute(ctx, cmd=code)
                elif str(reaction.emoji)==emoji.cross:
                    raise asyncio.exceptions.TimeoutError
            finally:
                await msg.clear_reactions()

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

    @commands.group()
    async def git(ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('Invalid git command passed...')

    @git.command()
    async def push(ctx, remote: str, branch: str):
        await ctx.send('Pushing to {} {}'.format(remote, branch))

def setup(bot):
    bot.add_cog(Code(bot))