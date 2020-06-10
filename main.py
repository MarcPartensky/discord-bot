
from config.credentials import token, client_id
from config.config import prefix, masters, delete_after_time, status, access

from discord.ext import commands, tasks
import progressbar
import warnings
warnings.filterwarnings("ignore")
import requests
import datetime
import discord
import sqlite3
import asyncio
import random
import itertools
import html
import time
import re
import os

#TODO
#command prefix

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

client = commands.Bot(command_prefix=prefix, case_insensitive=True)
client.id = client_id

class Main(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot
        self.invited = "invité"
        self.good_invited = "bon invité"
        self.bad_invited = "mauvais invité"
        self.help_every = 5
        self.load_cogs()
        self.load_status()

    def load_status(self):
        """Charge les statuts."""
        self.status = []
        for command in self.bot.commands:
            msg = prefix+command.name+" "+command.short_doc
            self.status.append(msg)
        random.shuffle(self.status)
        i = 0
        while i < len(self.status):
            msg = prefix+"help Voir les commandes."
            self.status.insert(i, msg)
            i += self.help_every
        self.status = itertools.cycle(self.status)

    @commands.command(name="charge-tous")
    @access.admin
    async def load_all(self, ctx:commands.Context):
        """Charge tous les cogs."""
        self.load_cogs()
        await ctx.send("Tous les cogs sont chargés.")

    def load_cogs(self):
        """Charge tous les cogs."""
        cogs = os.listdir('./cogs')
        with progressbar.ProgressBar(max_value=len(cogs)) as bar:
            for i,filename in enumerate(cogs):
                bar.update(i)
                if filename.endswith('.py'):
                    self.bot.load_extension(f"cogs.{filename[:-3]}")

    @commands.command(name="décharge-tous")
    @access.admin
    async def unload_all(self, ctx:commands.Context):
        """Décharge tous les cogs."""
        self.unload_cogs()
        await ctx.send("Tous les cogs sont déchargés.")

    def unload_cogs(self):
        """Décharge tous les cogs."""
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                self.bot.unload_extension(f"cogs.{filename[:-3]}")

    @commands.command(name="charge", aliases=["load"])
    @access.admin
    async def load(self, ctx, extension):
        """Charge les extensions."""
        self.bot.load_extension(f"cogs.{extension}")
        await ctx.send(f"Le cog {extension} a été chargée.")

    @commands.command(name="décharge", aliases=["unload"])
    @access.admin
    async def unload(self, ctx, extension):
        """Décharge les extensions."""
        self.bot.unload_extension(f"cogs.{extension}")
        await ctx.send(f"Le cog {extension} a été déchargée.")

    @tasks.loop(seconds = 10)
    async def change_status(self):
        """Change le statut."""
        await self.bot.change_presence(activity = discord.Game(next(self.status)))

    @commands.Cog.listener()
    async def on_ready(self):
        """Déclarer être prêt."""
        self.change_status.start()
        print(f'{self.bot.user} has connected to Discord!')

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Venue un nouveau membre."""
        await member.add_roles(self.invited)
        await ctx.send(f"{member.name} à été promu en {role.name}.")

        timeout = 60
        for channel in member.guild.channels:
            if channel.name == "général" or channel.name=="general":

                await channel.send(f"Bienvenue sur en {str(channel)} {member.mention}!")
                await channel.send("Dit bonjour.")
                def check(ctx):
                    if ctx.author!=member:
                        return False
                    msg = ctx.content.lower()
                    bonjours = ['hello', 'hi', 'hey', 'slt', 'salut', 'hola', 'bonjour', 'binjour', 'bonsoir']
                    for bonjour in bonjours:
                        if bonjour in msg:
                            return True
                    return False
                try:
                    msg = await self.bot.wait_for('message', check=check, timeout=timeout)
                    await channel.send("T'es un bon toi. T'iras loin!")
                    await member.add_roles(self.good_invited)
                    await ctx.send(f"{member.name} à été promu en {role.name}.")

                except Exception:
                    await channel.send(f"Ça fait déjà {timeout} secondes.\nT'es un mauvais toi. T'iras pas loin.")
                    await member.add_roles(self.bad_invited)
                    await ctx.send(f"{member.name} à été promu en {role.name}.")

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """Départ un nouveau membre."""
        timeout = 60
        for channel in member.guild.channels:
            if channel.name == "général" or channel.name=="general":
                await channel.send(f"Une pensée pour {member} qui a rage quit le serveur.")
                await channel.send(f"Faisons une minute de silence.")
                try:
                    check = lambda ctx:not ctx.author.bot
                    msg = await self.bot.wait_for('message', check=check, timeout=timeout)
                    await channel.send(f"On a dit une minute de silence!")
                except Exception:
                    await channel.send("La minute est passée. Vous pouvez retournez à vos activités.")
                    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error, translating=None):
        """Envoie l'erreur aux utilisateurs."""
        if not translating:
            translating = ctx.author.id not in masters
        if translating:
            from translate import Translator
            translator = Translator(to_lang='fr', from_lang='en')
            message = translator.translate(str(error))
            message = html.unescape(message)
        else:
            message = str(error)
        if message[-1]!=".": message+="."
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

def setup(bot):
    bot.add_cog(Main(bot))

if __name__=="__main__":
    os.system("clear")
    setup(client)
    client.run(token)
   
