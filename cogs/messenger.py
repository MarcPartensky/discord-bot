from discord.ext import commands
import discord

from config.config import access
from models.messenger import MessengerClient
import os
import datetime


class Messenger(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.client: MessengerClient = None
        self.color = discord.Color.blue()
        self.threads = {}

    @commands.group(aliases=["msg", "mes"])
    @access.admin
    async def messenger(self, ctx: commands.Context):
        """Utilise messenger."""
        if not self.client:
            await self.connect(ctx)

    @messenger.command(name="connecter", aliases=["connect", "reconnect"])
    async def connect(self, ctx: commands.Context):
        """Se connecte à un compte facebook."""
        mail = os.environ["FACEBOOK_MAIL"]
        password = os.environ["FACEBOOK_PASSWORD"]
        msg = await ctx.send(f"Connexion au messenger de {mail}.")
        self.client = MessengerClient(mail, password)
        await msg.delete()

    @messenger.command(
        name="déconnecter", aliases=["déconnexion", "disconnect", "logout"]
    )
    async def disconnect(self, ctx: commands.Context):
        """Se déconnecte de messenger."""
        self.client.logout()
        msg = f"{ctx.author.name} est déconnecté de messenger."
        await ctx.send(msg)

    @messenger.command(name="messages")
    async def messages(self, ctx: commands.Context, *, limit: int = 20):
        """Affiche les messages d'un conversation."""
        messages = self.client.fetchThreadMessages(
            thread_id=self.threads[ctx.author], limit=limit
        )
        lines = []
        authors = {}
        for message in reversed(messages):
            if message.author not in authors:
                authors[message.author] = self.client.fetchUserInfo(message.author)[
                    message.author
                ]
            user = authors[message.author]
            line = f"> {user.name}: {message.text}"
            lines.append(line)
        msg = "\n".join(lines)
        await ctx.send(msg)

        # embed = discord.Embed(title=name, color=self.color)
        # for message in messages:
        # user = self.client.fetchUserInfo(message.author)[message.author]
        # embed = discord.Embed(color=self.color)
        # embed.add_field(name=user.name, value=message.text)
        # # t = datetime.datetime.fromtimestamp(int(message.timestamp))
        # # embed.add_field(name="à", value=t)
        # embed.set_footer(text=("lu" if message.is_read else "non lu"))
        # await ctx.send(embed=embed)

    @messenger.command(name="envoie")
    async def send_message(self, ctx: commands.Context, *, msg: str):
        """Envoie un message sur messenger."""
        self.client.sendMessage(msg, thread_id=self.threads[ctx.author])
        await ctx.send(f"> {ctx.author}: {msg}")

    @messenger.command(name="info")
    async def info(self, ctx: commands.Context, *names: str):
        user_ids = [self.name_to_id(name) for name in names]
        self.client.fetchUserInfo(user_ids=user_ids)

    @messenger.command(name="non-lues", aliases=["nouveaux", "news"])
    async def unread(self, ctx: commands.Context):
        """Affiche les conversations non lues."""
        threads = self.client.fetchUnread()
        for thread in threads:
            thread = self.client.fetchThreadInfo(thread)[thread]
            await ctx.send(thread)
            # embed = self.embed_thread(thread)
            # msg = await ctx.send(embed=embed)
            # if thread.emoji:
            # await msg.add_reaction(emoji=thread.emoji)
        # await ctx.send(threads)

    def name_to_id(self, name: str):
        """Renvoie un nom avec un id de conversation."""
        threads = self.client.fetchThreadList()
        for thread in threads:
            if thread.name == name:
                return thread.uid

    def id_to_name(self, id: str):
        """Renvoie un id avec un nom de conversation."""
        threads = self.client.fetchThreadList()
        for thread in threads:
            if thread.uid == id:
                return thread.name

    @messenger.group(name="contacts", aliases=["users", "all-users", "utilisateurs"])
    async def contacts(self, ctx: commands.Context):
        """Utilise les contacts."""

    @contacts.command(name="afficher", alises=["show"])
    async def show(self, ctx: commands.Context, limit: int = None):
        """Affiche tous les utilisateurs."""
        users = self.client.fetchAllUsers()
        for user in users[:limit]:
            embed = self.embed_user_thread(user)
            await ctx.send(embed=embed)

    @contacts.command(name="nombre", aliases=["number"])
    async def number(self, ctx: commands.Context):
        """Affiche tous les utilisateurs."""
        users = self.client.fetchAllUsers()
        msg = f"{ctx.author.name} a {len(users)} contacts."
        await ctx.send(msg)

    @messenger.command(name="conversation", aliases=["conv"])
    async def thread(self, ctx: commands.Context, *, name: str = None):
        """Choisi ou affiche la conversation courante."""
        if name:
            self.threads[ctx.author] = self.name_to_id(name)
        else:
            if not self.thread:
                return await ctx.send("Vous n'êtes sur aucune conversation.")
        uid = self.threads[ctx.author]
        try:
            thread = self.client.fetchThreadInfo(uid)[uid]
        except:
            return await ctx.send(f"> La conversation {name} n'existe pas.")
        embed = self.embed_thread(thread)
        msg = await ctx.send(embed=embed)
        if thread.emoji:
            await msg.add_reaction(emoji=thread.emoji)

    @messenger.command(name="conversations", aliases=["convs"])
    async def threads(self, ctx: commands.Context):
        """Affiche la liste des conversations."""
        threads = self.client.fetchThreadList()
        for thread in threads:
            embed = self.embed_thread(thread)
            msg = await ctx.send(embed=embed)
            if thread.emoji:
                await msg.add_reaction(emoji=thread.emoji)

    def embed_user_thread(self, thread):
        """Crée une intégration discord avec une conversation d'utilisateur."""
        embed = discord.Embed(title=thread.name, color=self.color)
        embed.add_field(name="sexe", value=thread.gender)
        embed.add_field(name="messages", value=thread.message_count)
        if thread.photo:
            embed.set_thumbnail(url=thread.photo)
        embed.set_footer(text=thread.uid)
        return embed

    def embed_thread(self, thread):
        """Crée une intégration discord avec une conversation."""
        embed = discord.Embed(title=thread.name, color=self.color)
        embed.add_field(name="messages", value=thread.message_count)
        if str(thread.type) == "ThreadType.GROUP":
            names = [
                participant.name
                for participant in self.client.fetchThreadInfo(
                    *thread.participants
                ).values()
            ]
            names = "\n".join(names)
            embed.add_field(name="membres", value=names)
        if thread.photo:
            embed.set_thumbnail(url=thread.photo)
        embed.set_footer(text=thread.uid)
        return embed


def setup(bot):
    bot.add_cog(Messenger(bot))
