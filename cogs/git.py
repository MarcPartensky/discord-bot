from dataclasses import dataclass
from discord.ext import commands
from utils import tools
from config.config import access

from github import Github
import discord
import os


@dataclass
class Git(commands.Cog):
    github: Github

    def __init__(self, bot:commands.Bot):
        self.bot = bot

    @commands.group()
    async def github(self, ctx:commands.Context):
        """Utilise github."""
        self.github = Github(os.environ['PYGITHUB_TOKEN'])

    @github.command(name='user')
    async def show_user(self, ctx:commands.Context):
        """Affiche un répositoire."""
        user = self.github.get_user()
        embed = discord.Embed(title=user.name, color=discord.Color.purple())
        for k,v in getattr(user, '_rawData').items():
            embed.add_field(name=k, value=v or "aucun")
        await ctx.send(embed=embed)

    @github.group(name='repos')
    async def repositories(self, ctx:commands.Context):
        """Affiches les répositoires github."""
        self.repos = self.github.get_user().get_repos()
        # if not msg:
        #     await self.names(ctx)

    @repositories.command()
    async def names(self, ctx:commands.Context):
        """Affiches les noms des répositoires githubs."""
        print("")
        msg = '\n'.join(map(lambda r:r.name, self.repos))
        await ctx.send(msg)

    @repositories.command()
    async def number(self, ctx:commands.Context):
        """Affiche le nombre de repo."""
        pass

    @github.group(name='repo')
    async def repository(self, ctx:commands.Context):
        """Affiche des informations sur un répositoire."""
        pass


    @repository.command(name='choose', aliases=['='])
    async def choose(self, ctx:commands.Context, name:str):
        """Choisi un répositoire github."""
        self.repos = self.github.get_user().get_repos()
        self.repo = next(filter(lambda r:r.name==name, self.repos))

    @repository.command(name="show")
    async def show_repo(self, ctx:commands.Context):
        """Affiche un répositoire."""
        embed = discord.Embed(title=self.repo.name, color=discord.Color.purple())
        for k,v in getattr(self.repo, '_rawData').items():
            if k!='owner':
                embed.add_field(name=k, value=v)
        await ctx.send(embed=embed)

    @commands.group()
    @access.admin
    async def git(self, ctx:commands.Context):
        """Utilise git."""
        if ctx.invoked_subcommand is None:
            await ctx.send('Commande git invalide.')

    @git.command()
    async def add(self, ctx:commands.Context, msg:str="."):
        """Ajoute dans git."""
        cmd = f'git add {msg}'
        with tools.Capturing() as out:
            os.system(cmd)
        await ctx.send(cmd+'\n'+'\n'.join(out))

    @git.command()
    async def commit(self, ctx:commands.Context, msg:str):
        """Commit dans git."""
        cmd = f'git commit -m {msg}'
        with tools.Capturing() as out:
            os.system(cmd)
        await ctx.send(cmd+'\n'+'\n'.join(out))

    @git.command()
    async def push(self, ctx:commands.Context, remote:str, branch:str="master"):
        """Push dans git."""
        cmd = f'git push {remote} {branch}'
        with tools.Capturing() as out:
            os.system(cmd)
        await ctx.send(cmd+'\n'+'\n'.join(out))


def setup(bot):
    bot.add_cog(Git(bot))