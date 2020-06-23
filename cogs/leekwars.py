from models.leekwars import APILeekwars

from discord.ext import commands
import discord

import requests
import os

print('here i am')


class Leekwars(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot
        self.url = "https://leekwars.com/api/"
        self.color = discord.Color.dark_green()
        self.api = APILeekwars()
        self.farmer:dict = None
        self.leek_id_ = None
        self.token = None
        print('leekwars api init')

    @property
    def leek_id(self):
        if not self.leek_id_:
            self.leek_id_ = list(self.farmer['leeks'].keys())[0]
        return self.leek_id_

    @leek_id.setter
    def leek_id(self, id):
        self.leek_id_ = id

    @commands.group(aliases=['lk'])
    async def leekwars(self, ctx:commands.Context):
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
    async def activate(self, ctx:commands.Context):
        """Activer le compte."""
        r = self.api.farmer.activate(self.farmer['id'])
        await ctx.send(r)

    @leekwars.group(name="jardin", aliases=['potager'])
    async def garden(self, ctx:commands.Context):
        """Jardin de leekwars."""
        if ctx.invoked_subcommand is None:
            await self.get_farmer_opponnents(ctx)

    @garden.command(name="récupérer")
    async def get(self, ctx:commands.Context):
        """Récupère le jarding de leekwars."""
        r = self.api.garden.get(self.token)
        await ctx.send(r)

    @garden.command(name="défi-solo")
    async def get_solo_challenge(self, ctx:commands.Context, target_id:str):
        """Liste les défis solo."""
        url = self.api.garden.url + "/get-solo-challenge/" + str(self.leek_id)
        # r = requests.get(url, auth=(
        #     os.environ['LEEKWARS_USERNAME'],
        #     os.environ['LEEKWARS_PASSWORD']
        # ))
        # print(url)
        # r = self.api.session.get(url).json()
        print(r)
        await ctx.send(r)

    @garden.command(name="combat-solo")
    async def get_solo_fight(self, ctx:commands.Context):
        """Liste les combat solo."""
        url = self.api.garden.url + "/get-solo-fight/" + str(self.leek_id)
        r = requests.get(url, auth=(
            os.environ['LEEKWARS_USERNAME'],
            os.environ['LEEKWARS_PASSWORD']
        ))
        print(r.text)
        print(r)
        await ctx.send(r)


    @garden.command(name="opposants-fermier")
    async def get_farmer_opponnents(self, ctx:commands.Context):
        """Renvoie la liste des opposants d'un fermier."""
        from requests.auth import HTTPBasicAuth
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
    async def get_leek_opponnents(self, ctx:commands.Context):
        """Renvoie la liste des opposants du poireau."""
        # result = self.api.garden.get_leek_opponents(self.leek_id) #, self.token)
        url = os.path.join(self.url, 'garden',
            'get-leek-opponents', str(self.leek_id))
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Upgrade-Insecure-Requests': str(1),
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36'
        }
        print(url)
        print(headers)
        result = requests.get(url, headers=headers)
        print(result.request.__dict__)
        print(result.raw.__dict__)
        import json
        await ctx.send(result.request.__dict__)
        await ctx.send(result.raw.__dict__)

    @leekwars.command(name="valide")
    async def check(self, ctx:commands.Context):
        """Vérifie la validité d'un token."""
        r = self.api.token.check(self.token)
        await ctx.send(r)

    @leekwars.command(name="version")
    async def version(self, ctx:commands.Context):
        """Donne la version."""
        await ctx.send(self.api.leekWars.version())

    @leekwars.command(name="connectés")
    async def get_connected(self, ctx:commands.Context):
        """Se connected."""
        r = self.api.farmer.get_connected()
        lines = []
        for p in r['farmers']:
            line = f"> nom:{p['name']} id:{p['id']}"
            lines.append(line)
        msg = '\n'.join(lines)
        await ctx.send(msg)




def setup(bot):
    bot.add_cog(Leekwars(bot))