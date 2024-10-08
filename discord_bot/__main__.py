#!/usr/bin/env python
"""Entry point for executing the bot."""

import os
import random
import itertools
import asyncio
import warnings
from rich import print

import html
import progressbar

import discord
from discord.ext import commands, tasks

from dotenv import load_dotenv
load_dotenv()

from config.config import prefix, masters, access
from config.credentials import token, client_id



# TODO
# command prefix

# def get_prefix(bot, message):
#     """A callable Prefix for our bot. This could be edited to allow per server prefixes."""

#     # Notice how you can use spaces in prefixes. Try to keep them simple though.
#     prefixes = ['>?', 'lol ', '!?']

#     # Check to see if we are outside of a guild. e.g DM's etc.
#     if not message.guild:
#         # Only allow ? to be used in DMs
#         return '?'

#     # If we are in a guild, we allow for the user to mention us or use any of the prefixes in our list.
#     return commands.when_mentioned_or(*prefixes)(bot, message)


class Main(commands.Bot):
    """Main cog for commands."""

    def __init__(self, *args, client_id, **kwargs):
        """Create the main cog using the bot as argument."""
        super().__init__(*args, **kwargs)
        self.id = client_id
        self.invited = "invité"
        self.good_invited = "bon invité"
        self.bad_invited = "mauvais invité"
        self.help_every = 5

    async def setup_hook(self) -> None:
        """Automatically run by discord.py."""
        self.load_status()
        await self.load_cogs()

    def load_status(self):
        """Charge les statuts."""
        self._status = []
        for command in self.commands:
            msg = prefix + command.name + " " + command.short_doc
            self._status.append(msg)
        random.shuffle(self._status)
        i = 0
        while i < len(self._status):
            msg = prefix + "help Voir les commandes."
            self._status.insert(i, msg)
            i += self.help_every
        self._status = itertools.cycle(self._status)

    async def load_cogs(self):
        """Charge tous les cogs."""
        cogs = os.listdir("./cogs")
        with progressbar.ProgressBar(max_value=len(cogs)) as bar:
            for i, filename in enumerate(cogs):
                bar.update(i)
                if filename.endswith(".py"):
                    print(filename)
                    await self.load_extension(f"cogs.{filename[:-3]}")

    @commands.command()
    async def environment(self, ctx: commands.Context):
        """Affiche l'environnement dans lequel le bot tourne."""
        host = os.environ.get("HOST")
        print(f"environment: {host}")
        await ctx.send(f"> Environment: **{host}**")

    @commands.command(name="charge-tous")
    @access.admin
    async def load_all(self, ctx: commands.Context):
        """Charge tous les cogs."""
        await self.load_cogs()
        await ctx.send("Tous les cogs sont chargés.")


    @commands.command()
    async def list_cogs(self, ctx: commands.Context):
        """Liste tous les cogs."""
        cog_list = []
        for file in os.listdir("./cogs"):
            if file.endswith(".py"):
                if file.endswith(".py"):
                    file = "- " + file[:-3]
                    cog_list.append(file)
        list_text = "\n".join(cog_list)
        text = "```md\n" + list_text + "\n```"
        await ctx.send(text)

    @commands.command()
    async def loaded_cogs(self, ctx: commands.Context):
        """Liste tous les cogs."""
        loaded_cog_list = [f"- {s[5:]}" for s in self.extensions.keys()]
        if len(loaded_cog_list) == 0:
            await ctx.send("> Aucun cog chargé")
        else:
            list_text = "\n".join(loaded_cog_list)
            text = "```md\n" + list_text + "\n```"
            print(text)
            await ctx.send(text)

    @commands.command(name="décharge-tous")
    @access.admin
    async def unload_all(self, ctx: commands.Context):
        """Décharge tous les cogs."""
        await self.unload_cogs()
        await ctx.send("Tous les cogs sont déchargés.")

    async def unload_cogs(self):
        """Décharge tous les cogs."""
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                await self.unload_extension(f"cogs.{filename[:-3]}")

    @commands.command(name="charge", aliases=["load"])
    @access.admin
    async def load(self, ctx, extension):
        """Charge les extensions."""
        await self.load_extension(f"cogs.{extension}")
        await ctx.send(f"Le cog {extension} a été chargée.")

    @commands.command(name="décharge", aliases=["unload"])
    @access.admin
    async def unload(self, ctx, extension):
        """Décharge les extensions."""
        await self.unload_extension(f"cogs.{extension}")
        await ctx.send(f"Le cog {extension} a été déchargée.")

    @tasks.loop(seconds=10)
    async def change_status(self):
        """Change le statut.

        Exemples de status:
            - discord.ActivityType.listening,
            - discord.ActivityType.playing,
            - discord.ActivityType.playing,
            - discord.ActivityType.watching,
            - discord.ActivityType.competing
        """
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching, name=next(self._status)
            )
        )

    @commands.Cog.listener()
    async def on_ready(self):
        """Déclare être prêt."""
        self.change_status.start()
        print(f"{self.user} is connected to Discord!")

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Venue un nouveau membre."""
        await member.add_roles(self.invited)
        await ctx.send(f"{member.name} à été promu en {role.name}.")

        timeout = 60
        for channel in member.guild.channels:
            if channel.name == "général" or channel.name == "general":

                await channel.send(f"Bienvenue sur en {str(channel)} {member.mention}!")
                await channel.send("Dit bonjour.")

                def check(ctx):
                    if ctx.author != member:
                        return False
                    msg = ctx.content.lower()
                    bonjours = [
                        "hello",
                        "hi",
                        "hey",
                        "slt",
                        "salut",
                        "hola",
                        "bonjour",
                        "binjour",
                        "bonsoir",
                    ]
                    for bonjour in bonjours:
                        if bonjour in msg:
                            return True
                    return False

                try:
                    msg = await self.wait_for(
                        "message", check=check, timeout=timeout
                    )
                    await channel.send("T'es un bon toi. T'iras loin!")
                    await member.add_roles(self.good_invited)
                    await ctx.send(f"{member.name} à été promu en {role.name}.")
                except Exception:
                    await channel.send(
                        f"Ça fait déjà {timeout} secondes.\nT'es un mauvais toi. T'iras pas loin."
                    )
                    await member.add_roles(self.bad_invited)
                    await ctx.send(f"{member.name} à été promu en {role.name}.")

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        """Départ un nouveau membre."""
        timeout = 60
        for channel in member.guild.channels:
            if channel.name == "général" or channel.name == "general":
                await channel.send(
                    f"Une pensée pour {member} qui a rage quit le serveur."
                )
                await channel.send(f"Faisons une minute de silence.")
                try:

                    def check(ctx):
                        return not ctx.author.bot

                    msg = await self.wait_for(
                        "message", check=check, timeout=timeout
                    )
                    await channel.send(f"On a dit une minute de silence!")
                except Exception:
                    await channel.send(
                        "La minute est passée. Vous pouvez retournez à vos activités."
                    )

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error, translating=None):
        """Envoie l'erreur aux utilisateurs."""
        if not translating:
            translating = ctx.author.id not in masters
        if translating:
            from translate import Translator

            translator = Translator(to_lang="fr", from_lang="en")
            message = translator.translate(str(error))
            message = html.unescape(message)
        else:
            message = str(error)
        if message[-1] != ".":
            message += "."
        await ctx.send(message)
        raise error


# elif ctn.startswith('bot'):
#     ctn = ctn.replace('bot', '', 1).strip()
#     user = client.get_user(270904126974590976)
#     await user.send(ctn)
#     # for bot in bots:
#     #     print(ctn, bot, ctn.startswith(bot))
#     if ctn.startswith(bot):
#         ctn = ctn.replace(bot, '', 1).strip()
#         user = await client.get_user(bots)
#         await client.send_message(user,ctn)
#         print(f'sent to {bot}')
#         break


async def main():
    """Setup the bot for the main cog."""
    os.system("clear")
    print(f"prefix: {prefix}")

    # warnings.filterwarnings("ignore")
    intents = discord.Intents.default()
    intents.message_content = True

    # client = commands.Bot(command_prefix=prefix, case_insensitive=True)
    bot = Main(intents=intents, command_prefix=prefix, case_insensitive=False, client_id=client_id)

    async with bot:
        await bot.start(token)


if __name__ == "__main__":
    asyncio.run(main())
