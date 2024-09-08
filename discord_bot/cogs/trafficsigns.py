# This cog is only in french since only french rules are
# applied for this one and it is based upon a french website.
from config.config import masters, cluster
from discord.ext import commands
import discord
import requests
import random
import os
import re
import asyncio
import html


class TrafficSign(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.site_url = "https://www.passetoncode.fr/panneaux-de-signalisation/"
        self.image_url = "https://static.passetoncode.fr/img-panneaux/"
        self.categories = {
            "panneaux/agglomeration": 2,
            "panneaux/danger": 29,
            "panneaux/direction": 61,
            "panneaux/indication": 119,
            "panneaux/interdiction": 50,
            "panneaux/localisation": 14,
            "panneaux/obligation": 26,
            "panneaux/priorites": 9,
            "panneaux/travaux": 46,
            "panneaux/zone": 16,
            "balises": 14,
            "cartouches": 7,
            "ideogrammes": 56,
            "panonceaux": 85,
            "symboles": 37,
        }
        self.category = None
        self.color = discord.Color.blue()
        self.scores = cluster.traffic_signs.scores
        self.index = 0

    @property
    def total(self):
        return sum(self.categories.values())

    @property
    def possibilities(self):
        return [(k, i + 1) for k, n in self.categories.items() for i in range(n)]

    @property
    def default_score(self):
        return dict(true=0, false=0, unknown=0)

    @commands.group(name="panneau", aliases=["pn"])
    async def sign(self, ctx: commands.Context):
        """Groupe de commandes des panneaux routier."""
        if ctx.invoked_subcommand == None:
            await ctx.send("Aucune commande précisé")

    @sign.group(name="catégorie", aliases=["c"])
    async def category(self, ctx: commands.Context):
        """Catégorie sélectionnée."""
        if ctx.not_invoked:
            await self.show_category(ctx)

    @category.command(name="show")
    async def show_category(self, ctx: commands.Context):
        """Affiche la catégorie sélectionnée."""
        if self.category:
            msg = f"Vous avez choisi la catégorie **{self.category}**."
        else:
            msg = "Vous n'avez pas sélectionné de catégorie."
        await ctx.send(msg)

    @category.command(name="choisir-catégorie", aliases=["cc"])
    async def choose_category(self, ctx: commands.Context, category: str):
        """Choisis une catégorie de panneau."""
        self.category = category

    @sign.command(name="catégories", aliases=["cs"])
    async def categories(self, ctx: commands.Context):
        """Catégories disponibles."""
        msg = "\n".join([f"{k}: {v}" for k, v in self.categories.items()])
        embed = discord.Embed(
            title="Catégories",
            description=msg,
            color=self.color,
        )
        embed.set_footer(text=f"total: {self.total}")
        await ctx.send(embed=embed)

    def get_one(self, category: str = None, number: str = None):
        """Return a traffic sign."""
        if category:
            if number:
                return (category, number)
            else:
                return (category, random.randint(1, self.categories[category]))
        elif self.category:
            if number:
                return (self.category, number)
            else:
                return (
                    self.category,
                    random.randint(1, self.categories[self.category]),
                )
        else:
            return random.choice(self.possibilities)

    def valid_category(self, category: str = None):
        if category:
            if not category in self.categories:
                raise Exception("Ce n'est pas une catégorie.")

    def get_text(self, html_code, category, number):
        """Affiche le texte d'un panneau."""
        pattern = re.compile(r'<p class="mt-xlg">[^<]+[^>]+>([^<]+)</p>')
        results = re.findall(pattern=pattern, string=html_code)
        return results[0]

    def get_image(self, html_code, category, number):
        """Affiche l'image d'un panneau."""
        pattern = re.compile(
            r'<img src="(https:\/\/static.passetoncode\.fr\/img-panneaux\/[^"]+)'
        )
        results = re.findall(pattern=pattern, string=html_code)
        # print(results)
        return results[-1]

    @sign.command(name="afficher", aliases=["a", "show", "s"])
    async def show(
        self, ctx: commands.Context, category: str = None, number: int = None
    ):
        """Affiche un panneau."""
        self.valid_category(category)
        category, number = self.get_one(category, number)
        url = os.path.join(self.site_url, category, str(number))
        # print(category, number, url)
        html_code = requests.get(url).text
        text = self.get_text(html_code, category, number)
        image = self.get_image(html_code, category, number)
        # print(text, image)
        embed = discord.Embed(
            color=self.color, description=html.unescape(text), url=url
        )
        embed.set_image(url=image)
        footer = f"catégorie: {category},  numéro: {number}"
        embed.set_footer(text=footer)
        await ctx.send(embed=embed)

    @sign.command(name="voir", aliases=["v", "see"])
    async def see(
        self, ctx: commands.Context, category: str = None, number: int = None
    ):
        """Voir une question spécifique."""
        while True:
            score = await self.show_score(ctx)
            question = await self.ask_question(ctx, category, number)
            next_ = await self.react_question(question)
            await question.delete()
            if not next_:
                break
            else:
                await score.delete()

    async def ask_question(
        self, ctx: commands.Context, category: str = None, number: int = None
    ):
        """Pose une question."""
        embed = self.embed_question(category, number)
        return await ctx.send(embed=embed)

    def embed_question(self, category: str = None, number: int = None):
        self.valid_category(category)
        category, number = self.get_one(category, number)
        url = os.path.join(self.site_url, category, str(number))
        html_code = requests.get(url).text
        image = self.get_image(html_code, category, number)
        text = self.get_text(html_code, category, number)
        # print(url, number, category, image, text)
        embed = discord.Embed(description=f"||{html.unescape(text)}||")
        embed.set_image(url=image)
        embed.add_field(name="lien", value=url)
        footer = f"catégorie: {category},  numéro: {number}"
        embed.set_footer(text=footer)
        return embed

    async def react_question(self, question):
        """Réagit à une question."""
        await question.add_reaction("✅")
        await question.add_reaction("❌")
        await question.add_reaction("❔")
        await question.add_reaction("⏭️")
        await question.add_reaction("🗑️")
        reactions = ["✅", "❌", "❔", "🗑️"]
        next_question = False
        loop = True
        while loop:
            try:
                reaction, user = await self.bot.wait_for(
                    "reaction_add", timeout=60.0, check=lambda r, u: not u.bot
                )
                await reaction.remove(user)
                if user.id not in self.scores:
                    self.scores[user.id] = self.default_score
                if reaction.emoji == "✅":
                    self.scores[user.id].true += 1
                elif reaction.emoji == "❌":
                    self.scores[user.id].false += 1
                elif reaction.emoji == "❔":
                    self.scores[user.id].unknown += 1
                elif reaction.emoji == "⏭️":
                    return True
                elif reaction.emoji == "🗑️":
                    loop = False
            except asyncio.exceptions.TimeoutError:
                pass
        return False

    @sign.command(name="question", aliases=["q", "quizz", "questionnaire"])
    async def quiz(
        self,
        ctx: commands.Context,
        limit: int = None,
        category: str = None,
        number: int = None,
    ):
        """Pose une série questions sur des panneaux.
        À chaque panneau affiché l'utilisateur
        doit deviner sa signification. Ce dernier peut
        ensuite afficher la réponse et s'auto-évaluer."""
        limit = limit or float("inf")
        index = 1

        def get_value(index):
            if limit == float("inf"):
                return f"{index}"
            else:
                return f"{index}/{limit}"

        member = ctx.author
        score_embed = self.embed_score(member)
        question_embed = self.embed_question(category, number)
        question_embed.add_field(name="n°", value=get_value(index))
        score_message = await ctx.send(embed=score_embed)
        question_message = await ctx.send(embed=question_embed)
        while index < limit:
            next_ = await self.react_question(question_message)
            if not next_:
                break
            index += 1
            question_embed = self.embed_question(category, number)
            question_embed.add_field(name="n°", value=get_value(index))
            score_embed = self.embed_score(member)
            await score_message.edit(embed=score_embed)
            await question_message.edit(embed=question_embed)
        await question_message.delete()
        await score_message.delete()

    # @tasks.loop(seconds=5.0)
    # async def question_quizz(self, ctx:commands.Context):
    # self.index += 1

    @sign.group()
    async def score(self, ctx: commands.Context):
        """Score d'un membre."""
        if not ctx.invoked_subcommand:
            return await self.show_score(ctx)

    @score.command(name="propre")
    async def show_score(self, ctx: commands.Context, member: discord.Member = None):
        """Affiche le score d'un membre."""
        member = member or ctx.author
        if not member.id in self.scores:
            return await ctx.send(f"{member.name} n'a pas de score.")
        embed = self.embed_score(member)
        return await ctx.send(embed=embed)

    def embed_score(self, member: discord.Member):
        """Renvoie une intégration discord du score."""
        embed = discord.Embed(title=member.name, color=member.color)
        embed.set_thumbnail(url=member.avatar_url)
        for k, v in self.scores[member.id].items():
            if k == "_id":
                continue
            k = k.replace("true", "bonne réponse")
            k = k.replace("false", "mauvaise réponse")
            k = k.replace("unknown", "presque trouvé")
            embed.add_field(name=k, value=v)
        return embed

    @score.command(name="brute")
    async def show_raw_score(
        self, ctx: commands.Context, member: discord.Member = None
    ):
        """Affiche le score brute d'un membre."""
        member = member or ctx.author
        if not member.id in self.scores:
            return await ctx.send(f"{member.name} n'a pas de score.")
        return await ctx.send(self.scores[member.id])

    @sign.group()
    async def scores(self, ctx: commands.Context):
        """Scores de tous les membres."""
        if not ctx.invoked_subcommand:
            return await self.show_scores(ctx)

    @scores.command(name="propres")
    async def show_scores(self, ctx: commands.Context):
        """Affiche les scores de tous les membres."""
        lines = []
        for score in self.scores:
            member = self.bot.get_user(score["_id"])
            member_score = ", ".join(
                [f"{k}: {v}" for k, v in score.items() if k != "_id"]
            )
            line = f"- {member.name}: {member_score}"
            line = (
                line.replace("true", "bonne réponse")
                .replace("false", "mauvaise réponse")
                .replace("unknown", "presque trouvé")
            )
            lines.append(line)
        embed = discord.Embed(
            title="Scores de panneaux routier",
            color=self.color,
            description="\n".join(lines),
        )
        return await ctx.send(embed=embed)

    @scores.command(name="brutes")
    async def show_raw_scores(self, ctx: commands.Context):
        """Affiche les scores brutes des membres."""
        return await ctx.send("\n".join(map(str, self.scores)))

    @sign.group()
    async def competition(self, ctx: commands.Context):
        """Compétition sous forme de quiz."""


def setup(bot):
    bot.add_cog(TrafficSign(bot))
