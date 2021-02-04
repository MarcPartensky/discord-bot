"""
Control your leek in leekwars from discord.
"""

import os

import discord
import requests

from discord.ext import commands
from requests.auth import HTTPBasicAuth
from models.leekwars import APILeekwars


class Leekwars(commands.Cog):
    """Leekwars commands to control your leeks in leekwars."""

    def __init__(self, bot: commands.Bot):
        """Setup the leekwars commands with the bot."""
        self.bot = bot
        self.url = "https://leekwars.com/api/"
        self.color = discord.Color.dark_green()
        self.api = APILeekwars()
        self.farmer: dict = None
        self.leek_id_ = None
        self.token = None

    @property
    def leek_id(self):
        """Return the id of a leek if not stored already."""
        if not self.leek_id_:
            self.leek_id_ = list(self.farmer['leeks'].keys())[0]
        return self.leek_id_

    @leek_id.setter
    def leek_id(self, leek_id):
        """Store the id of a leek if not stored already."""
        self.leek_id_ = leek_id

    @commands.group(aliases=['lk'])
    async def leekwars(self, ctx: commands.Context):
        """API Leekwars."""
        if not self.token:
            url = os.path.join(
                self.url,
                "farmer/login-token",
                os.environ['LEEKWARS_USERNAME'],
                os.environ['LEEKWARS_PASSWORD'],
            )
            profile = requests.get(url=url).json()
            self.farmer = profile['farmer']
            self.token = profile['token']
        if ctx.invoked_subcommand is None:
            await ctx.send("Aucune commande n'est précisée.")

    @leekwars.command()
    async def activate(self, ctx: commands.Context):
        """Activer le compte."""
        await ctx.send(
            self.api.farmer.activate(self.farmer['id']))

    @leekwars.group(name="jardin", aliases=['potager'])
    async def garden(self, ctx: commands.Context):
        """Jardin de leekwars."""
        if ctx.invoked_subcommand is None:
            await self.get_farmer_opponnents(ctx)

    @garden.command(name="récupérer")
    async def get(self, ctx: commands.Context):
        """Récupère le jarding de leekwars."""
        await ctx.send(
            self.api.garden.get(self.token))

    @garden.command(name="défi-solo")
    async def get_solo_challenge(
            self,
            ctx: commands.Context,
            # target_id: str
        ):
        """Liste les défis solo."""
        url = self.api.garden.url + "/get-solo-challenge/" + str(self.leek_id)
        # r = requests.get(url, auth=(
        #     os.environ['LEEKWARS_USERNAME'],
        #     os.environ['LEEKWARS_PASSWORD']
        # ))
        # print(url)
        await ctx.send(
            self.api.session.get(url).json())

    @garden.command(name="combat-solo")
    async def get_solo_fight(self, ctx: commands.Context):
        """Liste les combat solo."""
        url = self.api.garden.url + "/get-solo-fight/" + str(self.leek_id)
        response = requests.get(url, auth=(
            os.environ['LEEKWARS_USERNAME'],
            os.environ['LEEKWARS_PASSWORD']
        ))
        print(response.text)
        print(response)
        await ctx.send(response)


    @garden.command(name="opposants-fermier")
    async def get_farmer_opponnents(self, ctx: commands.Context):
        """Renvoie la liste des opposants d'un fermier."""
        url = self.api.garden.url + "/get-farmer-opponnents/" + str(self.leek_id)# +"/"+token
        # r = self.api.session.get(url).json()
        result = requests.get(
            url,
            auth=HTTPBasicAuth(
                os.environ['LEEKWARS_USERNAME'],
                os.environ['LEEKWARS_PASSWORD']
            ))
        await ctx.send(result)

    @garden.command(name="opposants-poireau")
    async def get_leek_opponnents(self, ctx: commands.Context):
        """Renvoie la liste des opposants du poireau."""
        # result = self.api.garden.get_leek_opponents(self.leek_id) #, self.token)
        url = os.path.join(
            self.url,
            'garden',
            'get-leek-opponents',
            str(self.leek_id)
        )
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,\
                image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Upgrade-Insecure-Requests': str(1),
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5)Appl\
                eWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36'
        }
        print(url)
        print(headers)
        result = requests.get(url, headers=headers)
        print(result.request.__dict__)
        print(result.raw.__dict__)
        await ctx.send(result.request.__dict__)
        await ctx.send(result.raw.__dict__)

    @leekwars.command(name="valide")
    async def check(self, ctx: commands.Context):
        """Vérifie la validité d'un token."""
        result = self.api.token.check(self.token)
        await ctx.send(result)

    @leekwars.command(name="version")
    async def version(self, ctx: commands.Context):
        """Donne la version."""
        await ctx.send(self.api.leekWars.version())

    @leekwars.command(name="connectés")
    async def get_connected(self, ctx: commands.Context):
        """Liste les joueurs connectés."""
        result = self.api.farmer.get_connected()
        lines = [f"```ini\n[Joueurs connectés {result['count']}]\n```"]
        for farmer in result['farmers']:
            line = f"> nom:{farmer['name']} id:{farmer['id']}"
            lines.append(line)
        msg = '\n'.join(lines)
        await ctx.send(msg)


def setup(bot):
    """Setup the leekwars cog."""
    bot.add_cog(Leekwars(bot))
