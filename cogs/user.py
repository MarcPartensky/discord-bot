"""Cog of user related commands."""

import time
import discord

from discord.ext import commands

from models.user import User as UserAccount
from config.config import cluster, access
from config import emoji


class User(commands.Cog, name="Utilisateur"):
    """The user cog contains command to interact with the users informations."""

    def __init__(self, bot: commands.Bot):
        """Create an user cog using the bot."""
        self.bot = bot
        self.users = cluster.users
        self.info = self.users.info
        self.accounts = self.users.accounts
        self.starter_wallet_size = 1000
        self.starter_wallet_money = 5
        self.wait_message: discord.Message = None

    @property
    def defaults(self) -> dict:
        """Renvoie les champs des utilisateurs par défaults."""
        return dict(
            creation=time.time(),
            use=0,
            last_use=time.time(),
            money=0,
            xp=0,
            messages=0,
        )

    def __getitem__(self, member: discord.Member) -> UserAccount:
        """Renvoie un compte d'utilisateur étant donné le membre."""
        return UserAccount(_collection=self.accounts, _id=member.id)

    # def get(self, member:discord.Member): -> UserAccount
    #     """Renvoie un compte d'utilisateur étant donné le membre."""
    #     return UserAccount(_collection=self.accounts, _id=member.id)

    @commands.group(aliases=['prf'])
    async def profil(self, ctx: commands.Context):
        """Groupe de commande sur les profils des membres."""
        if not ctx.invoked_subcommand:
           await self.profil_info(ctx)

    @profil.command(name='information', aliases=['info', 'i'])
    async def profil_info(self, ctx: commands.Context, member: discord.Member = None):
        """Affiche le profil d'un membre."""
        member = member or ctx.author
        account = self[member]
        account.update()
        embed = discord.Embed(title=str(member), color=member.color)
        embed.set_thumbnail(url=member.avatar_url)
        embed.add_field(
            name="xp", value=f"{account.xp} {emoji.xp}")
        embed.add_field(
            name="niveau", value=f"{account.level} {emoji.level}")
        embed.add_field(
            name="énergie", value=f"{account.energy} {emoji.energy}")
        embed.add_field(
            name="portefeuille", value=f"{account.wallet} {emoji.euro}")
        if 'money' in cluster.bank.accounts:
            embed.add_field(
                name="banque", value=f"{cluster.bank.accounts[member.id].money} {emoji.money_bag}")
        if 'coins' in cluster.casino.accounts[member.id]:
            embed.add_field(
                name="coins", value=f"{cluster.casino.accounts[member.id].coins} {emoji.coin}")
        embed.set_footer(text=f"id: {member.id}")
        await ctx.send(embed=embed)

    @profil.command(name="brut", aliases=['raw', 'b'])
    @access.admin
    async def profil_raw(self, ctx: commands.Context, member: discord.Member = None):
        """Affiche un profil brute comme stocké sur mongo."""
        member = member or ctx.author
        account = self[member]
        await ctx.send('\n'.join(map(lambda x:f"> {':'.join(map(str, x))}",
                                     account.items())))

    @commands.group(name='portefeuille', aliases=['portemonnaie'])
    async def wallet(self, ctx: commands.Context, member: discord.Member = None):
        """Affiche l'argent d'un utilisateur."""
        user = member or ctx.author
        account = self.accounts[user.id]
        if ctx.author == user:
            msg = f"Vous avez **{account.money}** {emoji.euro} dans votre portefeuille."
        else:
            msg = f"{user.name} a **{account.money}** {emoji.money} dans son portefeuille."
        await ctx.send(msg)

    @wallet.command(name='=', aliases=['choisir', 'set', 'c'])
    @access.admin
    async def wallet_set(self, ctx: commands.Context, money: int, member: discord.Member = None):
        """Choisi l'argent d'un utilisateur."""
        member = member or ctx.author
        account = self[member]
        account.money = money
        if ctx.author == member:
            msg = f"> Vous avez maintenant **{account.money}** {emoji.euro} \
                dans votre portefeuille."
        else:
            msg = f"> {member.name} a maintenant **{account.money}** {emoji.money} \
                dans son portefeuille."
        await ctx.send(msg)

    @commands.command(name="dernier-message")
    async def last_message(self, ctx: commands.Context, member: discord.Member = None):
        """Affiche votre dernier message."""
        user = member or ctx.author
        account = self.accounts[user.id]
        id = account.last_message
        msg = "> Dernier message introuvable."
        for channel in self.bot.get_all_channels():
            try:
                if isinstance(channel, discord.channel.TextChannel):
                    msg = await channel.fetch_message(id)
                    break
            except Exception as e:
                print(e)
        await ctx.send("> "+msg.content)

    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message):
        """Détecte les messages des utilisateurs et incrémente l'xp."""
        if msg.author.bot:
            return
        account = self[msg.author]
        account.update(msg.author)
        account.xp += 1
        account.messages += 1
        account.last_message = msg.id

    @commands.group(name="xp", aliases=['expérience', 'experience'])
    async def xp(self, ctx: commands.Context):
        """Groupe de commandes liées à l'xp."""
        if not ctx.invoked_subcommand:
            await self.xp_info(ctx)

    @xp.command(name="info", aliases=['i'])
    async def xp_info(self, ctx: commands.Context, member: discord.Member = None):
        """Affiche l'xp d'un utilisateur."""
        user = member or ctx.author
        account = self[user.id]
        if ctx.author == member:
            msg = f"Vous avez **{account.xp}** {emoji.xp}."
        else:
            msg = f"{member.name} a **{account.xp}** {emoji.xp}."
        await ctx.send(msg)

    @xp.command(name='choisir', aliases=['=', 'set', "c"])
    @access.admin
    async def xp_set(self, ctx: commands.Context, xp: int, member: discord.Member = None):
        """Choisi l'xp d'un utilisateur."""
        member = member or ctx.author
        account = self[member]
        account.xp = xp
        if ctx.author == member:
            msg = f"Vous avez maintenant **{account.xp}** {emoji.xp}."
        else:
            msg = f"{member.name} a maintenant **{account.xp}** {emoji.xp}."
        await ctx.send(msg)

    @xp.command(name="ajouter", aliases=["+=", "add", "a"])
    @access.admin
    async def xp_add(self, ctx: commands.Context, member: discord.Member = None):
        """Augmente l'expérience d'un utilisateur."""
        member = member or ctx.author
        account = self.accounts[member.id]
        account.setdefaults(xp=0)
        account.xp += 1
        await self.xp_info(ctx, member)

    @xp.command(name="retirer", aliases=["-=", "soustraire", "sub", "s", 'remove'])
    @access.admin
    async def xp_remove(self, ctx: commands.Context, member: discord.Member = None):
        """Reitre l'expérience d'un utilisateur."""
        member = member or ctx.author
        account = self[member]
        account.setdefaults(xp=0)
        account.xp -= 1
        await self.xp_info(ctx, member)

    @xp.command(name="restant", aliases=['left'])
    async def xp_left(self, ctx: commands.Context, member: discord.Member = None):
        """Affiche l'xp restante pour monter en niveau."""
        member = member or ctx.author
        account = self[member]
        await ctx.send(f"> {member.name} doit gagner **{account.xp_left}** {emoji.xp} pour monter en niveau.")

    @commands.command(name="attendre", aliases=['wait'])
    async def wait(self, ctx: commands.Context, member: discord.Member = None):
        """Attend un utilisateur."""
        member = member or ctx.author
        sounddeck = self.bot.get_cog('SoundDeck')
        await sounddeck.play(ctx, name='ascenceur')
        self.wait_message = await ctx.send(
            f"> {member.name} va revenir dans quelques instants."
            "\n> Veuillez patienter.")

    @commands.command(name="re", aliases=['back'])
    async def back(self, ctx: commands.Context):
        """Retour de l'utilisateur."""
        music = self.bot.get_cog('Music')
        await music.cog_before_invoke(ctx)
        await music._leave(ctx)
        await self.wait_message.delete()

    @commands.group(name="niveau", aliases=['level'])
    async def level(self, ctx: commands.Context):
        """Groupe de commande des niveaux."""
        if not ctx.invoked_subcommand:
            await self.level_info(ctx)

    @level.command(name='info', aliases=['i'])
    async def level_info(self, ctx: commands.Context, member: discord.Member = None):
        """Affiche le niveau d'un membre."""
        member = member or ctx.author
        user = self[member]
        await ctx.send(f"> {member.name} est niveau **{user.level}** {emoji.level}.")

    @commands.group(name="énergie", aliases=['energie', 'energy', 'en'])
    async def energy(self, ctx: commands.Context):
        """Groupe de commande des énergies."""
        if not ctx.invoked_subcommand:
            await self.energy_info(ctx)

    @energy.command(name='info', aliases=['i'])
    async def energy_info(self, ctx: commands.Context, member: discord.Member = None):
        """Affiche l'énergie d'un membre."""
        member = member or ctx.author
        account = self[member]
        account.update_energy()
        await ctx.send(f"> {member.name} est énergie **{account.energy}** {emoji.energy}.")

    @energy.command(name="ajouter", aliases=['+=', 'a', 'add'])
    async def energy_add(self, ctx: commands.Context, amount: int, member: discord.Member = None):
        """Ajoute de l'énergie à un membre."""
        member = member or ctx.author
        account = self[member]
        account.update_energy()
        account.energy += amount

        await ctx.send(
            f"> {member.name} est maintenant énergie **{account.energy}** {emoji.energy}.")


def setup(bot):
    """Setup the user cog."""
    bot.add_cog(User(bot))
