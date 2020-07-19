from models import blackjack as bj
from discord.ext import commands
from config.config import cluster
import discord

class BlackJack(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot
        self.blackjacks = {}
        self.rooms = {}
        self.players = [] 

    @property

    @property
    def accounts():
        return cluster.casino.accounts
        # self.accounts[ctx.author.id].coins

    @commands.group(aliases=['bj'])
    async def blackjack(self, ctx:commands.Context):
        """Groupe de commandes du BlackJack."""
        if not ctx.invoked_subcommand:
            await ctx.send("> Erreur")

    @blackjack.command(name="créer", aliases=['create'])
    async def create(self, ctx:commands.Context, *members:discord.Member):
        """Créer une partie de BlackJack."""
        self.rooms[ctx.guild.id] = members
        discord.Embed
        await ctx.send(f"> Partie de BlackJack crée.")

    @blackjack.command(name="rejoindre", aliases=['join'])
    async def join(self, ctx:commands.Context):
        """Rejoins la partie de BlackJack."""
        self.rooms[ctx.guild.id].append(ctx.author)
        await ctx.send(f"> **{ctx.author.name}** avez bien rejoins la salle d'attente.")
    
    @blackjack.command(name="joueurs", aliases=['players'])
    async def players(self, ctx:commands.Context):
        """Affiche la liste des joueurs."""
        if ctx.guild.id in self.rooms:
            msg = "> "+"\n".join([player.name for player in self.rooms[ctx.guild.id]])
        else:
            msg = "> Aucun joueur de blackjack trouvé."
        message = await ctx.send(msg)
        # await message.add_reaction('✅')
        # await message.edit(content='truc')

    @blackjack.command()

    @blackjack.command()
    async def start(self, ctx:commands):
        """Lance la partie de BlackJack."""
        id_
        room = self.rooms.pop(ctx.guild.id)
        bet = 5

        self.accounts[ctx.author.id].coins -= bet

        # jouer

         self.accounts[ctx.author.id].coins += 2*bet


        

        for player in room:
            self.players.append(bj.Player(player.id))
            
            
        self.blackjacks[ctx.guild.id] = bj.BlackJack()

def setup(bot):
    bot.add_cog(BlackJack(bot))