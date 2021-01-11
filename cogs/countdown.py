"""
Gère les compte à rebours.
"""

import datetime
import itertools
import discord

from discord.ext import commands, tasks
from config.config import cluster, access
from models.mongo import MongoDatabase


class CountDown(commands.Cog):
    """Cog des comptes à rebours."""

    def __init__(self, bot: commands.Bot):
        """Count down."""
        self.bot = bot
        self.color = discord.Color(0xff0033)
        self.update.start()

    @property
    def countdowns(self):
        """Return the mongo countdown database."""
        return cluster.countdown.countdown

    @commands.group(
        name='compte-à-rebours',
        aliases=['countdown', 'count']
    )
    async def countdown(self, ctx: commands.Context):
        """Gestion de compte à rebours"""
        if not ctx.invoked_subcommand:
            print("Vous n'avez pas invoké de sous-commande.")

    @countdown.command(name='réinitialiser', alises=['reset', 'rs'])
    @access.admin
    async def reset(self, ctx: commands.Context):
        """Réinitialise la base de données."""
        del cluster['countdown']
        await ctx.send(f'> La base de données **countdown** a été supprimée.')

    @countdown.command(name="ajouter", aliases=['add', 'a'])
    async def add(self, ctx: commands.Context, name: str,
                  date: str, time: str = '00:00:00'):
        """Ajoute un compte à rebours."""
        datetime_str = date + " " + time
        print(datetime_str)
        datetime_ = datetime.datetime.strptime(
            datetime_str, '%Y-%m-%d %H:%M:%S')
        embed = self.get_embed(name, datetime_)
        message: discord.Message = await ctx.send(embed=embed)
        self.countdowns[name].datetime = datetime_
        self.countdowns[name].message = message.id
        self.countdowns[name].guild = message.guild.id
        self.countdowns[name].channel = message.channel.id

    @countdown.command(name='supprimer', aliases=['remove', 'rm'])
    async def remove(self, ctx: commands.Context, name: str):
        """Retire un compte à rebours."""
        del self.countdowns[name]
        await ctx.send(f"> Le compte à rebours {name} a été supprimé.")

    @countdown.command(name="trouver", aliases=['find', 'f'])
    async def find(self, ctx: commands.Context, *names: str):
        """Trouve des comptes à rebours."""
        for countdown in self.countdowns.find():
            await self.refresh(ctx,  countdown)

    async def refresh(self, ctx:commands.Context, countdown: dict):
        """Rafraîchi la collection,
        ainsi que le message."""
        name = countdown['_id']
        datetime_ = countdown['datetime']

        message = await self.get_countdown_message(countdown)

        await message.delete()

        embed = self.get_embed(
            countdown['_id'],
            datetime_
        )

        del self.countdowns[countdown['_id']]
        message: discord.Message = await ctx.send(embed=embed)

        self.countdowns[name].datetime = datetime_
        self.countdowns[name].message = message.id
        self.countdowns[name].guild = message.guild.id
        self.countdowns[name].channel = message.channel.id


    def get_embed(self, name: str, datetime_: datetime.datetime) -> discord.Embed:
        """Crée une intégration discord pour les comptes à rebours."""
        now = datetime.datetime.now().replace(microsecond=0)
        time_left = datetime_ - now
        # time_left_str = time_left.strftime("%Y/%m/%d %H:%M:%S")
        time_left_str = str(time_left)
        # print('time left:', time_left_str)
        embed = discord.Embed(
            title=time_left_str,
            description=name,
            color=self.color
        )
        return embed

    async def get_countdown_message(self, countdown: dict) -> discord.Message:
        """Return the message."""
        channel_id = int(countdown['channel'])
        guild_id = int(countdown['guild'])
        guild : discord.Guild = self.bot.get_guild(guild_id)
        channel : discord.TextChannel = guild.get_channel(channel_id)
        message = await channel.fetch_message(countdown['message'])
        return message

    @tasks.loop(seconds=1)
    async def update(self):
        """Actualise les compteurs."""
        # print(list(self.countdowns.find()))
        for countdown in self.countdowns.find():
            datetime_ = countdown['datetime']
            try:
                message = await self.get_countdown_message(countdown)
            except:
                print('[countdown] cant find message', countdown)
                continue
            now = datetime.datetime.now().replace(microsecond=0)
            time_left = datetime_ - now
            if time_left.total_seconds() < 0:
                del self.countdowns[countdown['_id']]
                await message.delete()
                continue
            embed = self.get_embed(
                countdown['_id'],
                datetime_
            )
            await message.edit(embed=embed)

    def cog_unload(self):
        """Retire les tâches de fonds."""
        self.update.cancel()

    @update.before_loop
    async def before_printer(self):
        """Wait until the bot is ready."""
        await self.bot.wait_until_ready()


def setup(bot):
    """Setup the CountDown cog."""
    bot.add_cog(CountDown(bot))
