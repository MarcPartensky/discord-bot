# This cog is only in french since only french rules are
# applied for this one and it is based upon a french website.
from discord.ext import commands
import discord
import requests
import random
import os
import re

pj = os.path.join

class TrafficSign(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot
        self.site_url = 'https://www.passetoncode.fr/panneaux-de-signalisation/panneaux'
        self.image_url = "https://static.passetoncode.fr/img-panneaux/panneaux"
        self.categories = dict(
            agglomération=2,
            danger=29,
            direction=61,
            indication=119,
            interdiction=50,
            localisation=14,
            obligation=26,
            priorités=9,
            travaux=46,
            zone=16,
            balise=14,
            cartouches=7,
            idéogrammes=56,
            panonceaux=85,
            symboles=47,
        )
        self.category = None
        self.color = discord.Color.blue()

    @property
    def total(self):
        return sum(*self.categories.values())
    
    @property
    def possibilities(self):
        return [(k,i) for k,n in self.categories.items() for i in range(n)]

    @commands.group(name='panneau', aliases=['pn'])
    async def sign(self, ctx:commands.Context):
        """Groupe de commandes des panneaux routier."""
        if ctx.invoked_subcommand == None:
            await ctx.send('Aucune commande précisé')

    # def random(self):
    #     """Choisi une catégorie aléatoire.
    #     La loi aléatoire n'est pas uniforme selon
    #     les catégories, mais pondérés selon les
    #     panneaux de façon à ce que la répartition
    #     des panneaux sélectionnés soit uniforme."""

    
    @sign.command(name="choisir-catégorie", aliases=['cc'])
    async def choose_category(self, ctx:commands.Context, category:str):
        """Choisis une catégorie de panneau."""
        self.category = category

    @sign.command(name='catégorie', aliases=['c'])
    async def category(self, ctx:commands.Context):
        """Affiche la catégorie sélectionnée."""
        if self.category:
            msg = f"Vous avez choisi la catégorie **{self.category}**."
        else:
            msg = "Vous n'avez pas sélectionné de catégorie."
        await ctx.send(msg)

    @sign.command(name="catégories", aliases=['cs'])
    async def categories(self, ctx:commands.Context):
        """Affiche les catégories disponibles."""
        msg = '\n'.join(self.categories.keys())
        await ctx.send(msg)

    def get_random(self, category:str):
        """Return a random traffic sign."""
        if category:
            return [category, random.randint(1, self.categories[category])]
        elif self.category:
            return [self.category, random.randint(1, self.categories[self.category])]
        else:
            return random.choice(self.possibilities)

    def valid_category(self, category:str=None):
        if category:
            if not category in self.categories:
                raise Exception("Ce n'est pas une catégorie.")
    
    def get_text(self, category, number):
        """Affiche le texte d'un panneau."""
        url = pj(self.site_url, category, str(number))
        text = requests.get(url).text
        pattern = re.compile(r'<p class="mlt-xlg">[^(</p>)]*')
        results = re.findall(pattern=pattern, string=text)
        print(results)
        result = results[0]
        pattern = re.compile(r'"[^"]*')
        results = re.findall(pattern=pattern, string=result)
        print(results)
        result = results[1]
        return result

    @sign.command(name="random")
    async def random(self, ctx:commands.Context, category:str=None):
        """Affiche un panneau random."""
        self.valid_category(category)
        category, number = self.get_random(category)
        text = self.get_text(category, number)
        image = self.get_image(category, number)
        embed = discord.Embed(title=text, url=image)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(TrafficSign(bot))
    