from config.config import access, status, delete_after_time, masters
from config import emoji

from utils.date import days, months
from utils import tools

from discord.ext import commands, tasks
from discord.ext.commands import Bot
from translate import Translator
from discord.utils import get
from discord import Message, PartialEmoji, Emoji
from bs4 import BeautifulSoup
import datetime
import discord
import random

# e = Emoji()
# rock = PartialEmoji(name=":rock:")


class Basic(commands.Cog):
    def __init__(self, bot, **kwargs):
        super().__init__(**kwargs)
        self.bot = bot

    @commands.command()
    @access.admin
    async def admin(self, ctx):
        """Détermine si vous êtes admin."""
        await ctx.send("Vous êtes admin.")

    @commands.command()
    @access.admin
    async def master(self, ctx):
        """Détermine si vous êtes master."""
        await ctx.send("Vous êtes master.")

    @commands.command()
    async def like(self, ctx):
        """Like le message."""
        await ctx.message.add_reaction('\N{THUMBS UP SIGN}')

    @commands.command(name="réagit")
    async def react(self, ctx, emoji:PartialEmoji, *, message:Message):
        """Réagit à un message avec un emoji."""
        await ctx.send(message)
        await ctx.message.add_reaction(emoji)

    @commands.command()
    async def ping(self, ctx):
        """Donne le ping."""
        await ctx.send(f'Pong! {round(self.bot.latency * 1000)}ms')

    @commands.command()
    async def language(self, ctx):
        """Renvoie 'language' de captain america."""
        await ctx.send("https://i.pinimg.com/originals/d9/4b/4e/d94b4e32dc787df8ae7c5d8a95184796.png")

    @commands.command(name="salut", aliases=["slt"])
    async def hello(self, ctx, *names):
        """Dit bonjour."""
        if len(names):
            await ctx.send(f"Salut "+", ".join(names)+"!")
        else:
            await ctx.send(f"Salut {ctx.author}!")

    # @commands.command(name="historique")
    # @access.admin
    # async def history(self, ctx, limit=5):
    #     """Donne l'historique des messages."""
    #     async for message in ctx.author.history(limit=limit):
    #         await ctx.send(message)

    @commands.command(name="est-amis")
    async def is_friend(self, ctx):
        """Détermine si vous êtes amis."""
        if ctx.author.is_friend():
            await ctx.send("Oui vous êtes amis.")
        else:
            await ctx.send("Non vous n'êtes pas amis.")


    @commands.command()
    async def howgay(self, ctx):
        """Détermine à quel point vous êtes gay."""
        # colors = ['red', 'orange', 'yellow', 'green', 'blue', 'purple']
        colors = [0xff0000, 0xffaa00, 0xffff00, 0x00ff00, 0x0000ff, 0xaa00aa]
        n = random.randint(0,100)
        i = int(len(colors)*n/101)
        color = colors[i]
        description = f"Vous êtes {n}% gay. :gay_pride_flag:"
        embed = discord.Embed(title="How gay?", description=description, color=discord.Color(color))
        await ctx.send(embed=embed)

    @commands.command()
    async def tts(self, ctx, *, msg):
        """Dit à l'oral les messages écrits."""
        await ctx.send(msg, tts=True)

    @commands.command(name='mes-servers')
    async def my_servers(self, ctx:commands.Context):
        """Donnes les serveurs où vous êtes connectés."""
        ctx.author.guild
        await ctx.send()

    @commands.command(name="auteur", aliases=["aut"])
    async def author(self, ctx):
        """Dit bonjour."""
        await ctx.send(f"Vous êtes {ctx.author}.")

    @commands.command(name="tag-à-nom")
    async def tag_to_name(self, ctx, tag:str):
        """Renvoie le nom associé au tag."""
        id = tools.to_id(tag)
        name = self.bot.get_user(id).name
        await ctx.send(name)

    @commands.command(name="nom-à-tag")
    async def name_to_tag(self, ctx, name:str):
        """Renvoie le nom associé au tag"""
        id = tools.name_to_id(ctx, name)
        tag = tools.to_tag(id)
        await ctx.send(tag)

    @commands.command()
    async def permissions(self, ctx, user:discord.Member=None, translating=True):
        """Donne les permissions."""
        if translating:
            from translate import Translator
            t = Translator(to_lang='fr', from_lang='en')
        user = user or ctx.author
        if not isinstance(user, discord.Member):
            if user == ctx.author:
                await ctx.send("Vous n'avez pas de permissions sur une conversation privée!")
            else:
                await ctx.send(f"{user.name} n'a pas de permissions sur une conversation privée!")
        else:
            permissions = ', '.join([str(p[0]).replace('_',' ') for p in user.guild_permissions if p[1]])
            if translating:
                permissions = t.translate(permissions).lower().replace('&#39;',"'")
            if user == ctx.author:
                await ctx.send(f"Vos permissions sont:\n{permissions}.")
            else:
                await ctx.send(f"{user.name} a les permissions:\n{permissions}.")        

    @commands.command()
    async def role(self, ctx, user:discord.Member=None):
        """Donne le rôle."""
        user = user or ctx.author
        if not isinstance(user, discord.Member):
            if user == ctx.author:
                await ctx.send("Vous n'avez pas de rôle sur une conversation privée!")
            else:
                await ctx.send(f"{user.name} n'a pas de rôle sur une conversation privée!")
        else:
            if user == ctx.author:
                await ctx.send(f"Vous êtes {user.top_role}.")
            else:
                await ctx.send(f"{user.name} est {user.top_role}.")

    @commands.command()
    async def roles(self, ctx, user:discord.Member=None):
        """Donne les rôles."""
        user = user or ctx.author
        if not isinstance(ctx.author, discord.Member):
            if user == ctx.author:
                await ctx.send("Vous n'avez pas de rôle sur une conversation privée!")
            else:
                await ctx.send(f"{user.name} n'a pas de rôle sur une conversation privée!")
        else:
            if user == ctx.author:
                await ctx.send("Vos rôles sont:  "+", ".join(reversed([r.name for r in user.roles[2:]]))+" et "+user.roles[1].name+".")
            else:
                await ctx.send(f"Les rôles de {user.name} sont:  "+", ".join(reversed([r.name for r in user.roles[2:]]))+" et "+user.roles[1].name+".")

    @commands.command(name="date-complète")
    async def full_date(self, ctx):
        """Donne la date complète."""
        n = datetime.datetime.now()
        await ctx.send(f'Nous sommes le {days[n.weekday()]} {n.day} {months[n.month]} {n.year}', delete_after=delete_after_time)

    @commands.command()
    async def heure(self, ctx):
        """Donne l'heure."""
        await ctx.send(f'Il est: {datetime.datetime.now().strftime("%X")}', delete_after=delete_after_time)

    @commands.command()
    async def date(self, ctx):
        """Donne la date."""
        await ctx.send(f'Nous sommes le {datetime.datetime.now().strftime("%d/%M/%Y")}', delete_after=delete_after_time)

    @commands.command(name='vérifie', aliases=['verif', 'vérif', 'vf'])
    async def french_check(self, ctx, *, message):
        """Vérifie un message."""
        translator = Translator(to_lang='en', from_lang='fr')
        translation = translator.translate(message)
        await self.check(ctx, message=translation)

    @commands.command()
    async def check(self, ctx, *, message):
        """Vérifie les insultes d'un message."""
        from profanity_check import predict_prob
        p = predict_prob([message])
        judgments = ['est gentil', 'est cool', 'est sympathique', 'est pas fou', 'est moyen', 'est pas cool', 'est insultant', 'est vulgaire', 'est violent', 'est innacceptable', 'mérite un ban']
        i = min(int(p*len(judgments)), len(judgments)-1)
        judgment = judgments[i]
        title = f"`{int(p*100)}% vulgaire`"
        r = int(255*p)
        g = int(255*(1-p))
        color = 256**2*r+256*g
        color = discord.Color(color)
        description = f"Ce message {judgment}!"
        embed = discord.Embed(title=title, description=description, color=color)
        await ctx.send(embed=embed)

    @commands.command(aliases=["muets"])
    @access.admin
    async def muted(self, ctx:commands.Context):
        """Liste tous les membre muets."""
        muted_members = []
        for member in ctx.guild.members:
            role_names = [role.name for role in member.roles]
            if self.muted_role_name in role_names:
                muted_members.append(member)
        if len(muted_members):
            color = 0xff0000 #red
            title = "Les membres muets sont:"
            description = "\n".join(map(lambda m:m.name, muted_members))
        else:
            color = 0x00ff00 #green
            title = "Aucun membre n'est muet."
            description = "Tout le monde est sympa."
        embed = discord.Embed(title=title, description=description, color=color)
        await ctx.send(embed=embed)

    @commands.command(name="eval", aliases=["v"])
    @access.admin
    async def evaluate(self, ctx, *, cmd):
        """Evalue une commande."""
        if '|' in cmd:
            cmd, args = cmd.split('|')
            args = args.split(',')
            cmd = tools.parse(cmd, *args)
        try:
            await ctx.send(eval(cmd))
        except Exception as e:
            await ctx.send(e)

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

    @commands.command(aliases=["c"])
    @access.admin
    async def code(self, ctx, *, cmd):
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

    @commands.command(name="historique")
    @access.admin
    async def historic(self, ctx, n=5):
        """Donne l'historique de la conversation."""
        async for message in ctx.channel.history(limit=n):
            await ctx.send(message.content)

    @commands.command(name="réactions")
    @access.admin
    async def reactions(self, ctx, n=5):
        """Donne les réactions de la conversation."""
        async for message in ctx.channel.history(limit=n):
            await ctx.send(message.reactions)

    @commands.command(name="script")
    async def script(self, ctx, *args, n=2):
        """Donne les réactions de la conversation."""
        async for message in ctx.channel.history(limit=n):
            if message.content.startswith('```python\n'):
                code = message.content.replace('```','').replace('python\n','')
                await self.execute(ctx, code, *args)

    @commands.command(name="couleur")
    async def color(self, ctx, color:discord.Color, *, message):
        """Colorie le message."""
        embed = discord.Embed(title="title", description=message, color=color)
        await ctx.send(embed=embed)

    @commands.Cog.listener(name="on_message")
    async def on_message(self, msg):
        """Lis tout les messages"""
        if msg.author == self.bot.user: return
        elif msg.content.startswith('```python\n'):
            code = msg.content.replace('```','').replace('python\n','')
            class ctx:
                send = msg.channel.send
                author = msg.author
            def check(reaction, user):
                print(emoji.play, reaction.emoji)
                return user==msg.author and str(reaction.emoji)==emoji.play 
            try:
                user, reaction = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
                await self.execute(ctx, code)
            except:
                pass

    @commands.Cog.listener(name="reaction_add")
    async def reaction_add(self, reaction, user):
        print(reaction, user)
        # await msg.channel.send("je vois")    








def setup(bot):
    bot.add_cog(Basic(bot))