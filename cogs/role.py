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
                "\n> Tapez `"
            )

    @role.command(aliases=['t'])
    async def top(self, ctx:commands.Context, member:discord.Member=None):
        """Affiche le rôle principal d'un joueur."""
        member = member or ctx.author
        if member == ctx.author:
            await ctx.send(f"Vous êtes {member.top_role}.")
        else:
            await ctx.send(f"{member.name} est {member.top_role}.")

    @role.command(name="liste", aliases=['list', 'l'])
    async def role_list(self, ctx:commands.Context):
        """Liste tous les rôles du serveur."""
        #bad way to do it, too much processing
        roles = []
        roles.extend(map(lambda mb:mb.roles, ctx.guild.members))
        roles = list(set(roles))
        msg = f"La liste des rôles présents sur le serveur est: {roles}"
        await ctx.send(msg)

    @commands.command()
    async def roles(self, ctx:commands.Context, member:discord.Member=None):
        """Donne les rôles."""
        member = member or ctx.author
        roles = list(reversed([r.name for r in member.roles]))
        string = f"{', '.join(roles[::-1])} et {roles[-1]}."
        if member == ctx.author:
            await ctx.send(f"Vos rôles sont {string}.")
        else:
            await ctx.send(f"Les rôles de {member.name} sont {string}.")

    # @role.command()
    # async def role_old(self, ctx:)

    # @role.command()

def setup(bot):
    bot.add_cog(Role(bot))
