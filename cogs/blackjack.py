from models import blackjack as bj
from discord.ext import commands
from config.config import cluster
import discord
import asyncio

class Emoji:
    door = "🚪"
    play = "▶️"
    stop =  "❌"
    sleep = "💤"
    card = "🃏"

class Room:
    def __init__(self,
        blackjack:bj.BlackJack=bj.BlackJack(),
        players:dict={},
        message:discord.Message=None,
        embed:discord.Embed=None,
        embed_message:discord.Message=None,
    ):
        self.blackjack = blackjack
        self.players = players
        self.message = message
        self.embed = embed
        self.embed_message = embed_message

    async def stop(self):
        """Arrête la salle."""
        await self.message.delete()
        await self.embed_message.delete()

    def getEmbed(self):
        """Renvoie une nouvelle intégration."""
        embed = discord.Embed(
            title="Blackjack",
            url="https://www.guide-blackjack.com/Regles-du-black-jack.html",
            color=discord.Color.green()) 
        player_names = '\n'.join([f"{user.name}: {bet}" for user, bet in self.players.items()])
        embed.add_field(name='Joueurs', value=player_names)
        embed.set_image(url="https://worldinsport.com/wp-content/uploads/2020/04/blackjack.jpg")
        return embed
        

class BlackJack(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot
        self.blackjacks = {}
        self.rooms = {}
        self.timeout = 5*60
        self.defaultBet = 0
        
    @property
    def accounts():
        return cluster.casino.accounts

    def getRoom(self, ctx:commands.Context):
        """Renvoie une salle."""
        if not ctx.guild.id in self.rooms:
            self.rooms[ctx.guild.id] = Room()
        return self.rooms[ctx.guild.id]
        
    async def send(self, ctx:commands.Context, content:str="", embed=None):
        """Envoie un message sur discord."""
        room = self.getRoom(ctx)
        if embed:
            if room.embed_message:
                await room.embed_message.edit(embed=embed)
            else:
                room.embed_message = await ctx.send(embed=embed)    
        else:
            if room.message:
                room.message.edit(content=content)
            else:
                room.message = await ctx.send(content)

    @commands.group(aliases=['bj'])
    async def blackjack(self, ctx:commands.Context):
        """Groupe de commandes du BlackJack."""
        if not ctx.invoked_subcommand:
            await self.send(ctx, "> Erreur")
        await ctx.message.delete()

    @blackjack.command(name="créer", aliases=['create', 'c'])
    async def create(self, ctx:commands.Context, *members:discord.Member, bet:int=None):
        """Créer une partie de BlackJack."""
        self.checkBet(bet, *members)
        bet = bet or self.defaultBet
        room = self.getRoom(ctx)
        room.players = {member:bet for member in members}
        room.players.update({ctx.author:bet})
        await self.show(ctx)

    def checkBet(self, bet:int, *members:discord.Member):
        """Vérifie les paris de chaque joueurs."""
        for member in members:
            if self.accounts[member.id].coins < bet:
                raise Exception("")

    async def show(self, ctx:commands.Context):
        """Affiche une intégration de BlackJack."""
        await self.send(ctx, f"> Partie de BlackJack crée.")
        await self.updateEmbed(ctx)
        await self.addCreateReactions(ctx)
        await self.react(ctx)

    async def updateEmbed(self, ctx:commands.Context):
        """Mets à jour une intégration discord."""
        room = self.getRoom(ctx)
        embed = self.getEmbed(room)
        await self.send(ctx, embed=embed)
    
    async def addCreateReactions(self, ctx:commands.Context):
        """Ajoute des réactions à une intégration."""
        embed_message = self.getRoom(ctx).embed_message
        await embed_message.add_reaction(Emoji.door)
        await embed_message.add_reaction(Emoji.play)

    async def addGameReactions(self, ctx:commands.Context):
        """Ajoute les réactions du blackjack."""
        embed_message = self.getRoom(ctx).embed_message
        await embed_message.add_reaction(Emoji.sleep)
        await embed_message.add_reaction(Emojoi.player)

    async def react(self, ctx:commands.Context):
        """Attend une réaction."""
        loop = True
        room = self.getRoom(ctx)
        while loop:
            try:
                reaction, user = await self.bot.wait_for(
                    'reaction_add', timeout=self.timeout, check=lambda r,u:not u.bot)
                await reaction.remove(user)
                if reaction.emoji == Emoji.door:
                    if user in room.players:
                        await self.removeUser(ctx, user)
                    else:
                        await self.addUser(ctx, user)
                            
                if reaction.emoji == Emoji.play:
                    await self.startGame(ctx)
                
            except asyncio.exceptions.TimeoutError:
                await self.stop(ctx)
        return False

    @blackjack.command(name="rejoindre", aliases=['join', 'j'])
    async def join(self, ctx:commands.Context, bet:int=None):
        """Rejoins la partie de BlackJack.
        Si elle n'existe pas en crée une."""
        if ctx.guild.id not in self.rooms:
            await self.create(ctx, bet=bet)
        bet = bet or self.defaultBet
        room = self.rooms[ctx.guild.id]
        room.players[ctx.author] = bet
        await self.send(ctx, f"> **{ctx.author.name}** avez bien rejoins la salle d'attente.")
        await self.updateEmbed(ctx)
        
    @blackjack.command(name="quitter", aliases=['leave', 'q', 'quit'])
    async def leave(self, ctx:commands.Context):
        """Quitte une partie de blackjack."""
        room = self.getRoom(ctx)
        del room.players[ctx.author]
        await self.send(ctx, f"> **{ctx.author.name}** a bien quitté la salle d'attente.")
        if room.players:
            await self.updateEmbed(ctx)
        else:
            await self.stop(ctx)

    async def removeUser(self, ctx:commands.Context, user:discord.User):
        """Kick un utilisateur de la partie"""
        room = self.getRoom(ctx)
        del room.players[user]
        await self.send(ctx, f"> **{user.name}** a bien quitté la salle d'attente.")
        if room.players:
            await self.updateEmbed(ctx)
        else:
            await self.stop(ctx)
    
    async def addUser(self, ctx:commands.Context, user:discord.User):
        """Ajoute un utilisateur à la partie"""
        room = self.getRoom(ctx)
        room.players[user] = self.defaultBet
        await self.send(ctx, f"> **{user.name}** a bien rejoint la salle d'attente.")
        await self.updateEmbed(ctx)

    @blackjack.command(name="parier", aliases = ['bet'])
    async def bet(self, ctx:commands.Context, bet:int=None):
        """Parie un certain montant."""
        if ctx.guild.id not in self.rooms:
            await self.create(ctx)
        bet = bet or self.defaultBet
        if bet < 0:
            raise Exception("Il faut parier une somme positive.")
        if self.accounts[player.id].coins < bet:
            raise Exception("Vous ne pouvez pas pariez plus ce que vous avez.")
        room = self.getRoom(ctx)
        room.players[ctx.author] = bet
        await self.send(ctx, f"> **{ctx.author.name}** a parié {bet} coins.")

    @blackjack.command()
    async def start(self, ctx:commands):
        """Lance la partie de BlackJack."""
        room = self.getRoom(ctx)
        await self.addGameReactions(ctx)
        for player, bet in room.players.items():
            self.accounts[player.id].coins -= bet 
        # self.accounts[ctx.author.id].coins -= bet
        # jouer
        #  self.accounts[ctx.author.id].coins += 2*bet

    async def startGame(self, ctx):
        """Lance la partie de BlackJack."""
        await self.addGameReactions(ctx)
  

    @blackjack.command()
    async def stop(self, ctx:commands.Context):
        """Arrête la partie."""
        if ctx.guild.id not in self.rooms:
            raise Exception("Partie inexistante.")
        room = self.rooms[ctx.guid.id] 
        await room.stop()
        del self.rooms[ctx.guid.id]

    @blackjack.command(name="ici", aliases=['here'])
    async def here(self, ctx:commands.Context):
        """Déplace le blackjack en bas."""
        room = self.getRoom(ctx)
        await room.stop(ctx)
        await self.show(ctx)

    @blackjack.command()
    async def kick(self, ctx:commands.Context, member:discord.Member):
        """Déplace le blackjack en bas."""
        room = self.getRoom(ctx)
        await self.removeUser(ctx, member)
        if room.players:
            await self.updateEmbed(ctx)
        else:
            await self.stop(ctx)


def setup(bot):
    bot.add_cog(BlackJack(bot))
