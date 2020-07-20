from models import blackjack as bj
from discord.ext import commands
from config.config import cluster
import discord

class Emoji:
    door = "🚪"
    play = "▶️"
    stop =  "❌"
    sleep = "💤"

class BlackJack(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot
        self.blackjacks = {}
        self.rooms = {}
        self.messages = {}
        self.embeds = {}

    @property

    @property
    def accounts():
        return cluster.casino.accounts
        # self.accounts[ctx.author.id].coins

    async def send(self, ctx:commands.Context, content:str="", embed=None):
        """Envoie un message sur discord."""
        if embed:
            if ctx.guild.id in self.embeds:
                await self.embeds[ctx.guild.id].edit(embed=embed)
            else:
                self.embeds[ctx.guild.id] = await ctx.send(embed=embed)    
        else:
            if ctx.guild.id in self.messages:
                await self.messages[ctx.guild.id].edit(content=content)
            else:
                self.messages[ctx.guild.id] = await ctx.send(content)    

    @commands.group(aliases=['bj'])
    async def blackjack(self, ctx:commands.Context):
        """Groupe de commandes du BlackJack."""
        if not ctx.invoked_subcommand:
            await self.send(ctx, "> Erreur")

    @blackjack.command(name="créer", aliases=['create', 'c'])
    async def create(self, ctx:commands.Context, *members:discord.Member):
        """Créer une partie de BlackJack."""
        self.rooms[ctx.guild.id] = list(members) + [ctx.author]
        await self.send(ctx, f"> Partie de BlackJack crée.")
        embed = discord.Embed(
            title="Blackjack",
            url="https://www.guide-blackjack.com/Regles-du-black-jack.html",
            color=discord.Color.green())
        player_names = ', '.join([p.name for p in self.rooms[ctx.guild.id]])
        embed.add_field(name='Joueurs', value=player_names)
        embed.set_image(url="https://worldinsport.com/wp-content/uploads/2020/04/blackjack.jpg")
        await self.send(ctx, embed=embed)
        # ctx.message.
        await self.add_reactions(ctx)

    async def add_reactions(self, ctx:commands.Context):
        """Ajoute des réactions à une intégration."""
        embed_message = self.embeds[ctx.guild.id]
        await embed_message.add_reaction(Emoji.door)
        await embed_message.add_reaction(Emoji.play)
        await embed_message.add_reaction(Emoji.sleep)
        await embed_message.add_reaction(Emoji.stop)

    @blackjack.command(name="rejoindre", aliases=['join', 'j'])
    async def join(self, ctx:commands.Context):
        """Rejoins la partie de BlackJack."""
        self.rooms[ctx.guild.id].append(ctx.author)
        await self.send(ctx, f"> **{ctx.author.name}** avez bien rejoins la salle d'attente.")
        
    @blackjack.command(name="quitter", aliases=['leave', 'q', 'quit'])
    async def leave(self, ctx:commands.Context):
        """Quitte une partie de blackjack."""
        self.rooms[ctx.guild.id].pop(ctx.author)
        await self.send(ctx, f"> **{ctx.author.name}** avez bien quitté la salle d'attente.")

    @blackjack.command(name="parier", aliases = ['bet'])
    async def bet(self, ctx:commands.Context, bet:int):
        """Parie un certain montant."""







    
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
    async def start(self, ctx:commands):
        """Lance la partie de BlackJack."""
        id_
        room = self.rooms.pop(ctx.guild.id)
        bet = 5


        # self.accounts[ctx.author.id].coins -= bet

        # jouer

        #  self.accounts[ctx.author.id].coins += 2*bet


        

        for player in room:
            self.players[ctx.guild.id].append(bj.Player(player.id))
            
            
        self.blackjacks[ctx.guild.id] = bj.BlackJack()

def setup(bot):
    bot.add_cog(BlackJack(bot))