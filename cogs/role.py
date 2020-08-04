from discord.ext import commands
from config.config import cluster, prefix
import discord

class Role(commands.Cog):
    """The goal of this cog is to sell roles or give bonuses when roles are given."""
    def __init__(self, bot:commands.Bot):
        self.bot = bot

    @commands.group(name="rôle", aliases=['role'])
    async def role(self, ctx:commands.Context):
        """Groupe des commandes sur les rôles."""
        if not ctx.invoked_subcommand:
            await ctx.send(
                "> Cette commande est inexistante."
            )

    @role.command(aliases=['t'])
    async def top(self, ctx:commands.Context):
        """Affiche le rôle principal d'un joueur."""




    @role.command(name="liste", aliases=['list', 'l'])
    async def list_roles(self, ctx:commands.Context):
        """Liste tous les rôles du serveur."""
        pass

    @role.command()



