from config.config import access, cluster
from config import shops

from discord.ext import commands
from models.terminal import Terminal
import discord
import os
import typing

muted_role_name = "Muet"


class Muted(commands.Converter):
    async def convert(self, ctx, member: str):
        member = await commands.MemberConverter().convert(
            ctx, member
        )  # create member object
        role = discord.utils.get(ctx.guild.roles, name=muted_role_name)
        if role in member.roles:
            return member
        else:
            raise commands.BadArgument("Le membre n'est pas muet.")


class Admin(commands.Cog):
    def __init__(self, bot: commands.Bot, **kwargs):
        """Cog pour administrer un serveur."""
        super().__init__(**kwargs)
        self.bot = bot
        self.kick_reason = "c'est la vie"
        self.ban_reason = "on t'aime pas"
        self.unban_reason = "on t'aime (no homo)"
        self.mute_reason = "tu parles trop mec"
        self.demute_reason = "on veut entendre le doux son de ta voix"
        self.clear_limit = 10
        self.invite_duration = 10 * 60  # in seconds
        self.muted_role_name = muted_role_name
        self.victims_channel_name = "Victimes"
        self.terminal = False

    @commands.command(aliases=["console"])
    @access.admin
    async def terminal(self, ctx: commands.Context):
        """Execute and send terminal output."""
        self.terminal = not self.terminal
        if self.terminal:
            self.bot.add_cog(Terminal(self.bot))
            await ctx.send("> Votre terminal est ouvert.")
        else:
            self.bot.remove_cog("Terminal")
            await ctx.send("> Votre terminal est fermé.")

    @commands.command()
    @shops.commands.sell
    async def rename(
        self, ctx: commands.Context, member: discord.Member, *, nickname: str
    ):
        """Renomme un membre."""
        await member.edit(nick=nickname)
        await ctx.send(
            f"> Le pseudo de **{member.name}** est maintenant **{member.mention}**."
        )

    @commands.command()
    @access.admin
    async def kick(
        self, ctx: commands.Context, member: discord.Member, *, reason: str = None
    ):
        "Expulse un membre du serveur."
        reason = reason or self.kick_reason
        try:
            account = cluster.users.accounts[member.id]
            account.roles = [role.name for role in member.roles[1::]]
            await member.kick(reason=reason)
        except discord.Forbidden:
            return await ctx.send(
                f"> Je n'ai pas le droit de kick car {member} "
                "a un rôle supérieur au mien."
            )
        await ctx.send(
            f"> **{member.name}** a été kick de **{ctx.guild}** parce que **{reason}**."
        )
        await member.send(
            f"> Vous avez été kick de **{ctx.guild}** parce que **{reason}**."
        )

    @commands.command()
    @access.admin
    async def pardon(self, ctx: commands.Context, member: discord.Member):
        """Redonne les rôles à un membre après avoir été kick."""
        account = cluster.users.accounts[member.id]
        for role in account.roles:
            await member.add_roles(role)
        roles = list(account.roles)
        roles = list(map(lambda role: f"*{role}*", roles))
        string_roles = ", ".join(roles[::-1]) + " et " + role[-1]
        await ctx.send(f"> **{member.name}** récupère les rôles {string_roles}.")

    @commands.command()
    @access.admin
    async def invite(
        self, ctx: commands.Context, user: discord.User, duration: int = None
    ):
        """Invite un utilisateur au serveur."""
        duration = duration or self.invite_duration
        link = await ctx.channel.create_invite(max_age=duration)
        await user.send(link)

    @commands.command(name="kick-invite")
    @shops.commands.sell
    async def kick_and_invite(
        self,
        ctx: commands.Context,
        member: discord.Member,
        duration: typing.Optional[int] = None,
        *,
        reason: str = None,
    ):
        "Kick puis réinvite un membre."
        reason = reason or self.kick_reason
        roles = member.roles
        try:
            account = cluster.users.accounts[member.id]
            account.roles = [role.name for member in member.roles[1::]]
            await member.kick(reason=reason)
        except discord.Forbidden:
            return await ctx.send(f"> Je n'ai pas le droit de kick.")
        await ctx.send(
            f"> **{member.name}** a été kick de **{ctx.guild}** parce que **{reason}**."
        )
        await member.send(
            f"> Vous avez été kick de **{ctx.guild}** parce que **{reason}**."
        )
        await member.send(f"> Heuresement vous avez encore le droit de rejoindre.")
        member.add_roles(roles)
        await self.invite(ctx, member, duration)

    @commands.command()
    @access.admin
    async def ban(
        self,
        ctx,
        members: commands.Greedy[discord.Member],
        delete_days: typing.Optional[int] = 0,
        *,
        reason: str = None,
    ):
        """Banni un membre du serveur."""
        reason = reason or self.ban_reason
        for member in members:
            try:
                await member.ban(delete_message_days=delete_days, reason=reason)
                await ctx.send(
                    f"> **{member.name}** a été ban de {ctx.guild} parce que {reason}."
                )
            except discord.Forbidden:
                await ctx.send(f"Je n'ai pas le droit de ban.")

    @commands.command()
    @access.admin
    async def unban(self, ctx, *, member, reason: str = None):
        """Débanni un member du serveur."""
        reason = reason or self.unban_reason
        banned_users = await ctx.guild.bans()
        name, discriminator = member.split("#")
        for ban_entry in banned_users:
            user = ban_entry.user
            if (user.name, user.discriminator) == (name, discriminator):
                await ctx.guild.unban(user)
                await ctx.send(
                    f"> **{name}** a été débanni de **{ctx.guild}** parce que **{reason}**."
                )
                break

    @commands.command()
    async def banned(self, ctx: commands.Context):
        """Liste les membre bannis sur le serveur."""
        msg = "> **Liste des membres bannis:**\n"
        msg += "\n".join(
            [
                f">       - **{ban.user.name}#{ban.user.discriminator}** car **{ban.reason}**."
                for ban in await ctx.guild.bans()
            ]
        )
        return await ctx.send(msg)

    @commands.command()
    @shops.commands.sell
    async def clear(self, ctx, limit: int = None, included=True):
        """Nettoie le chat."""
        limit = limit or self.clear_limit
        await ctx.channel.purge(limit=limit + included)

    @commands.command(name="clear-terminal")
    @access.admin
    async def clear_terminal(self, ctx):
        """Nettoie le terminal."""
        os.system("clear")

    @commands.command(name="exit", aliases=["quitter"])
    @access.admin
    async def exit(self, ctx):
        """Arrête le programme du bot."""
        await ctx.send("> Je quitte discord. Au revoir!")
        raise SystemExit

    @commands.command()
    @access.admin
    async def promote(self, ctx, member: discord.Member, *, role: discord.Role):
        """Promouvoie un membre à un rôle."""
        try:
            await member.add_roles(role)
            await ctx.send(f"> **{member.name}** à été promu en **{role.name}**.")
        except discord.Forbidden:
            await ctx.send("> Je n'ai pas le droit de promouvoir un membre d'un rôle.")

    @commands.command()
    @access.admin
    async def demote(self, ctx, member: discord.Member, *, role: discord.Role):
        """Destitue un membre d'un rôle."""
        try:
            await member.remove_roles(role)
            await ctx.send(
                f"> **{member.name}** à été destitué et perd le rôle **{role.name}**."
            )
        except discord.Forbidden:
            await ctx.send("> Je n'ai pas le droit de destituer un membre d'un rôle.")

    @commands.command()
    @shops.commands.sell
    async def mute(
        self, ctx: commands.Context, member: discord.Member, *, reason: str = None
    ):
        """Mute un membre."""
        role_names = [role.name for role in member.roles]
        if muted_role_name in role_names:
            return await ctx.send(f"> **{member}** est déjà muet.")
        reason = reason or self.mute_reason
        role = discord.utils.get(ctx.guild.roles, name=self.muted_role_name)
        if not role:  # create a role for the muted
            try:
                role = await ctx.guild.create_role(
                    name=self.muted_role_name,
                    reason="Pour muter les gens trop bavards.",
                )
                for channel in ctx.guild.channels:  # removes permission to view and send in the channel
                    await channel.set_permissions(
                        role,
                        send_messages=False,
                        read_message_history=False,
                        read_messages=False,
                    )
            except discord.Forbidden:
                return await ctx.send(
                    "> Je n'ai pas le droit de créer de rôle pour les muets."
                )
        await member.add_roles(role)
        await ctx.send(
            f"> **{member.name}** a été mute sur tous les salons vocaux parce **{reason}**."
        )
        await self.kick_from_voice_channel(ctx, member)

    @commands.command(aliases=["muets"])
    @access.admin
    async def muted(self, ctx: commands.Context):
        """Liste tous les membre muets."""
        muted_members = []
        for member in ctx.guild.members:
            role_names = [role.name for role in member.roles]
            if self.muted_role_name in role_names:
                muted_members.append(member)
        if len(muted_members):
            color = 0xFF0000  # red
            title = "Les membres muets sont:"
            description = "\n".join(map(lambda m: m.name, muted_members))
        else:
            color = 0x00FF00  # green
            title = "Aucun membre n'est muet."
            description = "Tout le monde est sympa."
        embed = discord.Embed(title=title, description=description, color=color)
        await ctx.send(embed=embed)

    @commands.command(name="déplacer", aliases=["mettre", "move-to", "move"])
    @shops.commands.sell
    async def move_to(
        self,
        ctx: commands.Context,
        member: discord.Member,
        channel: discord.VoiceChannel,
    ):
        """Déplace vers dans un salon vocal."""
        await member.move_to(channel)

    @commands.command(
        name="kick-vocal", aliases=["kick-du-vocal", "shut-up", "ftg", "tg"]
    )
    @shops.commands.sell
    async def kick_from_voice_channel(
        self, ctx: commands.Context, member: discord.Member = None
    ):
        """Kick un membre du salon vocal."""
        # print(dir(member))
        if not member:
            # await self.quit_voice_channel(ctx)
            # return
            # discord.Member(data=)
            # member = await self.bot.fetch_user(self.bot.id)
            # print(member)
            # member = self.bot
            # member = self.bot.get_user(self.bot.)
            self.bot.join
        try:
            victims_channel = await ctx.guild.create_voice_channel(
                name=self.victims_channel_name
            )
            await member.move_to(victims_channel)
        except Exception as e:
            print(e)
        finally:
            await victims_channel.delete()

    @commands.command(name="quitter-vocal", aliases=["quit-vocal", "leave-vocal"])
    @access.admin
    async def quit_voice_channel(self, ctx, channel: discord.VoiceChannel = None):
        """Quitte un salon vocal."""
        if not channel:
            for voice_client in self.bot.voice_clients:
                if voice_client.guild == ctx.guild:
                    await voice_client.disconnect()
                    await ctx.send(f"> J'ai quitté **{voice_client.channel}**.")
                    return
            await ctx.send(f"> Je ne suis pas connecté à un salon vocal.")
        else:
            await channel.disconnect()

    @commands.command(name="quitter-vocaux", aliases=["quit-vocals", "leave-vocals"])
    @access.admin
    async def quit_all_voice_channels(self, ctx, channel: discord.VoiceChannel = None):
        """Quitte tous les salons vocaux."""
        for voice_client in self.bot.voice_clients:
            await voice_client.disconnect()
        await ctx.send("> J'ai quitté tous les salons vocaux.")

    @commands.command(aliases=["demute"])
    @access.admin
    async def unmute(self, ctx, member: Muted, *, reason: str = None):
        """Démute un membre."""
        reason = reason or self.demute_reason
        try:
            await member.remove_roles(
                discord.utils.get(ctx.guild.roles, name=self.muted_role_name)
            )  # removes muted role
            await ctx.send(f"> **{member.name}** a été démute parce que {reason}.")
        except discord.Forbidden:
            await ctx.send("> Je n'ai pas le droit de démute des membres.")

    @commands.command(aliases=["guilds"])
    @access.admin
    async def servers(self, ctx: commands.Context):
        """Liste tous les serveurs du bot."""
        names = [guild.name for guild in self.bot.guilds]
        msg = ", ".join(names)
        await ctx.send(msg)


async def setup(bot):
    await bot.add_cog(Admin(bot))
