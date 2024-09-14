from discord.ext import commands
from discord.utils import get
from config.config import cluster, access
from utils.tools import not_invoked_command
from functools import reduce

import discord


class Role(commands.Cog):
    """The goal of this cog is to sell roles or give bonuses when roles are given."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.color = discord.Color.teal()

    @commands.group(name="rôle", aliases=["role"])
    async def role(self, ctx: commands.Context):
        """Groupe des commandes sur les rôles."""
        if not ctx.invoked_subcommand:
            await not_invoked_command(ctx, "role")

    @role.command()
    async def top(self, ctx: commands.Context, member: discord.Member = None):
        """Affiche le rôle principal d'un joueur."""
        member = member or ctx.author
        if member == ctx.author:
            await ctx.send(f"Vous êtes {member.top_role}.")
        else:
            await ctx.send(f"{member.name} est {member.top_role}.")

    @role.command(name="liste", aliases=["list", "l"])
    async def role_list(self, ctx: commands.Context, member: discord.Member = None):
        """Donne tous les rôles d'un membre."""
        # bad way to do it, too much processing
        member = member or ctx.author
        roles = list(reversed([f"*{r.name}*" for r in member.roles]))[:-1]
        string = f"{', '.join(roles[::-1])} et {roles[-1]}."
        if member == ctx.author:
            await ctx.send(f"> Vos rôles sont {string}.")
        else:
            await ctx.send(f"> Les rôles de **{member.name}** sont {string}.")

    @role.command(name="sauvegarder", aliases=["save", "s"])
    async def role_save(self, ctx: commands.Context, member: discord.Member = None):
        """Sauvegarde les rôles d'un membre."""
        member = member or ctx.author
        account = cluster.users.accounts[member.id]
        account.roles = [role.name for role in member.roles[1::]]
        if member == ctx.author:
            msg = "> Vos rôles sont sauvegardés."
        else:
            msg = f"> Les rôles de **{member.name}** sont sauvegardés."
        await ctx.send(msg)

    @role.command(name="choisir", aliases=["set", "c"])
    @access.admin
    async def role_set(self, ctx: commands.Context, level: int, *, role: discord.Role):
        """Choisi le niveau nécessaire pour gagner un rôle."""
        # create = False
        # if not 'users' in cluster:
        # create = True
        # elif not 'options' in cluster.users:
        # create = True
        # elif not 'roles' in cluster.users.options:
        # create = True
        # elif not 'levels_based' in cluster.users.options.roles:
        # create = True
        # if create:
        # cluste.users.options.roles
        cluster.users.options.roles[str(role.id)] = level
        await ctx.send(f"> Le rôle {role} est à {level} levels.")

    @role.group(name="tableau", aliases=["board", "b", "t"])
    async def role_board(self, ctx: commands.Context):
        """Groupe de commandes du tableau de rôles."""
        if not ctx.invoked_subcommand:
            await self.role_board_see(ctx)

    @role_board.command(name="voir", aliases=["see", "v"])
    async def role_board_see(self, ctx: commands.Context):
        """Affiche le tableau des rôles."""
        if len(cluster.users.options.roles) == 1:
            return await ctx.send("> Le tableau des rôles est vide.")
        embed = discord.Embed(title="Tableau des rôles", color=self.color)
        for role_id, level in cluster.users.options.roles.items():
            if role_id != "_id":
                role = get(ctx.guild.roles, id=int(role_id))
                role_name = role.name
                embed.add_field(name=role_name, value=str(level))
        await ctx.send(embed=embed)

    @role_board.command(name="supprimer", aliases=["s", "delete", "d"])
    async def role_board_delete(self, ctx: commands.Context):
        """Supprime tous les rôles du tableau."""
        cluster.users.options.roles.clear()
        await ctx.send(f"> Le tableau des rôles est maintenant vide.")

    @commands.command()
    async def roles(self, ctx: commands.Context, member: discord.Member = None):
        """Liste tous les rôles du serveur."""
        roles = []
        roles.extend(map(lambda mb: mb.roles, ctx.guild.members))
        roles = reduce(lambda a, b: a + b, roles)
        roles = list(map(lambda role: role.name, set(roles)))
        msg = f"> La liste des rôles présents sur le serveur est: {roles}"
        await ctx.send(msg)

    # @role.command()
    # async def role_old(self, ctx:)


async def setup(bot):
    await bot.add_cog(Role(bot))
