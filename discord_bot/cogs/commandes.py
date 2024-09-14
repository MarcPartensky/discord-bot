import datetime
import time
from os.path import abspath, dirname, join

import discord
import pymongo
from discord.ext import commands

from config.config import access, check, cluster, masters, prefix
from models.database import Database
from models.mongo import Post
from utils import tools


class Commandes(commands.Cog):
    def __init__(self, bot: commands.Bot):
        """Crée la catégorie des commandes avec le bot en argument."""
        self.bot = bot
        self.commands = cluster.commands.commands
        # self.commands.create_index([('command', pymongo.ASCENDING)], unique=True)
        self.max_commands_shown = 10
        self.learn_separator = "=>"
        self.search_prefix = ","
        self.timeout = 60

    @commands.group(name="commande", aliases=["cmd"])
    async def command(self, ctx: commands.Context):
        """Groupe de commandes sur les commandes."""
        if not ctx.invoked_subcommand:
            await ctx.send(
                "> Erreur: commande inexistante."
                f"\n> Tapez `{prefix}help commande` pour voir les commandes disponibles."
            )

    @command.command(name="migrer")
    @access.admin
    async def migrate(self, ctx: commands.Context):
        """Migre commandes d'sqlite vers mongodb."""
        path = join(dirname(dirname(abspath(__file__))), "database/answers.db")
        sqldb = Database(path=path)
        sqldb.select("answers")
        for (t, u, r, a) in sqldb.fetchall():
            name = u.split("#")[0]
            author = discord.utils.get(ctx.guild.members, name=name)
            if author:
                author = author.id
            post = Post(
                _id=r,
                result=a,
                author=author,
                creation=float(t),
                time=time.time(),
                use=0,
                user=None,
            )
            self.commands[r] = post
            msg = f"> La commande **{r}** a été apprise."
            # await ctx.send(msg)
            print(msg)

    @command.command(name="apprends", aliases=["retiens", "learn"])
    async def learn(self, ctx: commands.Context, command, result):
        """Apprends une commande."""
        post = self.commands.find_one({"command": command})
        if post:
            author = self.bot.fetch_user(post._id)
            if (not author == ctx.author.id) and (not ctx.author.id in masters):
                return await ctx.send(
                    f"> La commande **{command}** est réservée par **{author.name}**."
                )
        post = Post(
            _id=command,
            author=ctx.author.id,
            result=result,
            creation=time.time(),
            time=time.time(),
            use=0,
            user=None,
        )
        self.commands[command] = post
        await ctx.send(f"> La commande **{command}** a été apprise.")

    @command.command(name="cherche", aliases=["search", "find"])
    async def search(self, ctx: commands.Context, command: str, *args, regex: bool = True, show_cmd: bool = True):
        """Cherche une commande."""
        if regex:
            cursor = self.commands.find(dict(_id={'$regex': ".*" + command + ".*"}))
        else:
            cursor = self.commands.find(dict(_id=command))
        n = -1
        for n, post in enumerate(cursor):
            post.setdefault("use", 0)
            post["use"] = post["use"] + 1
            post["user"] = ctx.author.id
            code = self.bot.get_cog("Code")
            if not "result" in post:
                del post
                continue
            ctx.authorized = True
            cmd = tools.parse(post["result"], *args)
            if post["author"] in masters:
                if show_cmd:
                    await ctx.send(f"> {post['_id']} =>")
                await code.code(ctx, cmd=cmd)
                continue
            if post["result"]:
                response = post["result"]
                if show_cmd:
                    response = f"> {post['_id']}" + " =>\n" + response
                await ctx.send(response)
                continue
            await ctx.send("> Pas de réponse configurée.")

        if n == -1:
            return await ctx.send(f"> Aucun résultat pour la commande **{command}**")

    @command.command(aliases=["info"])
    async def information(self, ctx: commands.Context, *, command: str):
        """Informe sur une commande."""
        post = self.commands[command]
        if not post:
            return await ctx.send(f"> La commande **{command}** n'existe pas.")
        creation = datetime.datetime.fromtimestamp(int(post.creation))
        time = datetime.datetime.fromtimestamp(int(post.time))
        author = self.bot.get_user(post.author)
        user = self.bot.get_user(post.user) or "personne"
        msg = [
            f"> __Informations sur **{command}**:__",
            f"> - commande: {post._id}",
            f"> - réponse: {post.result}",
            f"> - auteur: {author}",
            f"> - crée le {creation}",
            f"> - utilisée {post.use} fois",
            f"> - dernière utilisation le {time}",
            f"> - par {user}",
        ]
        msg = "\n".join(msg)
        await ctx.send(msg)

    @command.command(name="nombre", aliases=["number", "n"])
    async def number(self, ctx: commands.Context):
        """Affiche le nombre de commandes."""
        n = len(self.commands)
        await ctx.send(f"> Il y'a **{n}** commandes enregistrées.")

    @command.command(name="toutes", aliases=["all"])
    async def all_commands(self, ctx: commands.Context, n=5, order="desc"):
        """Affiche les commandes enregistrées."""
        if ctx.author.id not in masters:
            n = min(n, self.max_commands_shown)
        posts = list(self.commands.find(limit=n, sort=[("time", pymongo.DESCENDING)]))
        if len(posts) == 0:
            return await ctx.send("> Aucune commande n'est enregistrée.")
        await self.send_commands(ctx, posts)

    @command.command(name="moi", aliases=["me"])
    async def my_commands(self, ctx: commands.Context, n=5, order="desc"):
        """Affiche mes commandes enregistrées."""
        if ctx.author.id not in masters:
            n = min(n, self.max_commands_shown)
        posts = list(
            self.commands.find(
                {"author": ctx.author.id}, limit=n, sort=[("time", pymongo.DESCENDING)]
            )
        )
        if len(posts) == 0:
            return await ctx.send("> Vous n'avez enregistré aucune commande.")
        await self.send_commands(ctx, posts)

    @command.command(name="lui", aliases=["his", "her"])
    async def his_commands(
        self, ctx: commands.Context, member: discord.Member, n=5, order="desc"
    ):
        """Affiche ses commandes enregistrées."""
        if ctx.author.id not in masters:
            n = min(n, self.max_commands_shown)
        posts = list(
            self.commands.find(
                {"author": member.id}, limit=n, sort=[("time", pymongo.DESCENDING)]
            )
        )
        if len(posts) == 0:
            return await ctx.send("> Il n'a enregistré aucune commande.")
        await self.send_commands(ctx, posts)

    async def send_commands(self, ctx, posts):
        lines = []
        for post in posts:
            post = Post(post)
            name = self.bot.get_user(post.author)
            t = datetime.datetime.fromtimestamp(post.time)
            line = f"> {post._id} => {post.result} par {name}."
            lines.append(line)
        txt = "\n".join(lines)
        await ctx.send(txt)

    @command.command(name="supprimer", aliases=["delete", "d", "s"])
    @access.admin
    @check.validation
    async def delete(self, ctx: commands.Context):
        """Supprime toutes les commandes enregistrées."""
        self.commands.delete_many({})
        await ctx.send("> Toutes les commandes ont été supprimées.")

    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message):
        """Lis tout les messages."""
        if msg.author.bot:
            return

        class ctx:
            send = msg.channel.send
            author = msg.author

        if self.learn_separator in msg.content:
            req, resp = msg.content.split(self.learn_separator)
            await self.learn(ctx, req.strip(), resp.strip())
        elif msg.content.startswith(self.search_prefix):
            req = msg.content.replace(self.search_prefix, "", 1)
            await self.search(ctx, *map(lambda r: r.strip(), req.strip().split("|")), regex=False, show_cmd=False)


async def setup(bot: commands.Bot):
    await bot.add_cog(Commandes(bot))


# TODO: Test the cog
