
from discord.ext import commands, tasks
from models.database import Database
from config.config import access, masters
from utils import tools

import discord
import random
import datetime
import time
import re


class Memory(commands.Cog, Database):
    def __init__(self, bot, path, **kwargs):
        commands.Cog.__init__(self, **kwargs)
        Database.__init__(self, path)
        self.bot = bot
        self.fields = {"datetime":"text", "author":"text", "request":"text", "answer":"text"}
        self.table = "answers"
        self.load()
        self.max_command_historic = 10
        self.learn_separator = "=>"
        self.search_prefix = ","

    def load(self):
        self.create_table_if_not_exists(table=self.table, fields=self.fields)
        try:
            self.create_unique_index(table=self.table, id="id", field="request")
        except:
            pass

    @commands.command(name="clm-mémoire", aliases=["colonnes-mémoire"])
    async def memory_columns(self, ctx):
        """Donne le noms des colonnes des commandes."""
        cursor = self.connection.execute(f'select * from {self.table}')
        names = list(map(lambda x: x[0], cursor.description))
        await ctx.send(names)

    @commands.command(name="apprends", aliases=["retiens","learn", "l"])
    async def learn(self, ctx, req, resp):
        """Apprend une commande."""
        self.select(table=self.table, conditions={"request":req})
        result = self.fetchone()
        if not result:
            row = [str(time.time()), str(ctx.author), req, resp]
            self.insert(self.table, row)
            await ctx.send("Je retiens.")
        else:
            aut = result[1]
            if ctx.author.id in masters or str(ctx.author)==aut:
                values = dict(datetime=time.time(), author=str(ctx.author), answer=resp)
                conditions = dict(request=req)
                self.update(self.table, values=values, conditions=conditions)
                await ctx.send("Je retiens de nouveau.")
            else:
                await ctx.send(f"Cette commande est déjà réservé par {aut}.")

    @commands.command(name="chercher", aliases=[""])
    async def search(self, ctx, req, *args):
        """Cherche une commande dans la mémoire."""
        self.select(table=self.table, conditions={"request":req})
        result = self.fetchone()
        if not result:
            await ctx.send(f"Je ne connais pas {req}.")
        else:
            basic = self.bot.get_cog("Basic")
            name = result[1].split('#')[0]
            resp = result[3]
            ctx.guild = ctx.author.guild
            writer = self.bot.get_user(tools.name_to_id(ctx, name))
            ctx.authorized = True
            if writer.id in masters:
                await basic.code(ctx, cmd=resp)
            else:
                await ctx.send(resp)

    @commands.command(name="nombre-commandes", aliases=["taille-mémoire"])
    async def commands_number(self, ctx):
        """Affiche le nombre de commandes."""
        await ctx.send(str(len(self[self.table])))

    @commands.command(name="commandes", aliases=["mémoire"])
    async def all_commands(self, ctx, member:discord.Member=None, n=5, order="desc"):
        """Affiche les commandes enregistrées."""
        if not member: member = ctx.author
        if not ctx.author.id in masters:
            n = min(n, 10)
        conditions = dict(author=str(member))
        self.select(self.table, conditions=conditions, orderby="rowid", order=order)
        results = self.fetchmany(n)
        if len(results) == 0:
            await ctx.send("Aucune commande n'est enregistrée.")
        else:
            cmds = []
            for t,u,r,a in results:
                ti = datetime.datetime.fromtimestamp(float(t))
                cmds.append(f"{r} => {a} // par {u} le {ti.date()} à {ti.strftime('%X')}")
            await ctx.send("\n".join(cmds))

    @commands.command(name="mes-commandes", aliases=["ma-mémoire"])
    async def my_commands(self, ctx, n=5, order="desc"):
        """Affiche ses commandes enregistrées."""
        if not ctx.author.id in masters:
            n = min(n, 10)
        self.select(self.table, conditions=dict(author=str(ctx.author)), orderby="rowid", order=order)
        results = self.fetchmany(n)
        if len(results) == 0:
            await ctx.send("Vous n'avez pas de commandes enregistrées.")
        else:
            cmds = []
            for t,u,r,a in results:
                ti = datetime.datetime.fromtimestamp(float(t))
                cmds.append(f"{r} => {a} // le {ti.date()} à {ti.strftime('%X')}")
            await ctx.send("\n".join(cmds))

    @commands.command(name="oublie")
    @access.admin
    async def forget(self):
        """Oublie toutes les commandes."""
        await super().forget()

    @commands.Cog.listener()
    async def on_message(self, msg:discord.Message):
        """Lis tout les messages"""
        if msg.author == self.bot.user: return
        class ctx:
            send = msg.channel.send
            author = msg.author
        if self.learn_separator in msg.content:
            req, resp = msg.content.split(self.learn_separator)
            await self.learn(ctx, req.strip(), resp.strip())
        elif msg.content.startswith(self.search_prefix):
                req = msg.content.replace(self.search_prefix,'',1)
                await self.search(ctx, req.strip())


def setup(bot): #Production
    from os.path import join, dirname, abspath
    path = join(dirname(dirname(abspath(__file__))), 'database/answers.db')
    memory = Memory(bot, path=path)
    bot.add_cog(memory)