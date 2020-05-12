from config.credentials import token, client_id
from config.config import prefixes, masters, delete_after_time, status, access

from discord.ext import commands, tasks
import warnings
warnings.filterwarnings("ignore")
import requests
import datetime
import discord
import sqlite3
import asyncio
import random
import time
import re
import os

#TODO
#command prefix


client = commands.Bot(command_prefix='.', case_insensitive=True)
client.id = client_id


class Main(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.load_cogs()
        self.invited = "invité"
        self.good_invited = "bon invité"
        self.bad_invited = "mauvais invité"

    def load_cogs(self):
        """Charge tous les cogs."""
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                self.bot.load_extension(f"cogs.{filename[:-3]}")

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
        await self.bot.change_presence(activity = discord.Game(next(status)))

    @commands.Cog.listener()
    async def on_ready(self):
        """Déclarer être prêt."""
        self.change_status.start()
        print(f'{self.bot.user} has connected to Discord!')

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Venue un nouveau membre."""
        await member.add_roles(invited)
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
                    await member.add_roles(good_invited)
                    await ctx.send(f"{member.name} à été promu en {role.name}.")

                except Exception:
                    await channel.send(f"Ça fait déjà {timeout} secondes.\nT'es un mauvais toi. T'iras pas loin.")
                    await member.add_roles(bad_invited)
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
                    msg = await self.bot.wait_for('message', check=lambda ctx:True, timeout=timeout)
                    await channel.send(f"On a dit une minute de silence!")
                except Exception:
                    await channel.send("La minute est passée. Vous pouvez retournez à vos activités.")
                    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error, translating=False):
        """Envoie l'erreur aux utilisateurs."""
        if translating:
            from translate import Translator
            translator = Translator(to_lang='fr', from_lang='en')
            message = translator.translate(str(error)).replace('&quot;','\"').replace('&#39;',"'")
        message = str(error)
        await ctx.send(message)
        raise error

# @client.event
# if ctn.startswith('joke'):
#     url = "https://joke3.p.rapidapi.com/v1/joke"
#     payload = "{ \"content\": \"A joke here\", \"nsfw\": \"false\"}"
#     headers = {
#         'x-rapidapi-host': "joke3.p.rapidapi.com",
#         'x-rapidapi-key': "c8657e166emsh302e8584f57b1abp1e41a4jsnf726d8d0c1c7",
#         'content-type': "application/json",
#         'accept': "application/json"
#         }
#     response = requests.request("POST", url, data=payload, headers=headers)
#     print(response.text)
#     await chn.send(response.text)
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
   
