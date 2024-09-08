from models import blackjack as bj
from discord.ext import commands
from config.config import cluster
import discord
import asyncio


class Emoji:
    door = "🚪"
    play = "▶️"
    stop = "❌"
    sleep = "💤"
    card = "🃏"
    double = "2️⃣"


class Room:
    def __init__(
        self,
        blackjack: bj.BlackJack = bj.BlackJack(),
        players: dict = {},
        message: discord.Message = None,
        embed: discord.Embed = None,
        embed_message: discord.Message = None,
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
            color=discord.Color.green(),
        )
        player_names = "\n".join(
            [f"{user.name}: {bet}" for user, bet in self.players.items()]
        )
        embed.add_field(name="Joueurs", value=player_names)
        embed.set_image(
            url="https://worldinsport.com/wp-content/uploads/2020/04/blackjack.jpg"
        )
        return embed

    def find(self, member: discord.Member):
        """Trouve un joueur dans la salle."""
        i = 0
        for player in room.blackjack.players:
            i += 1
            if player.id == member.id:
                return player
        return None


class BlackJack(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.blackjacks = {}
        self.rooms = {}
        self.timeout = 5 * 60
        self.defaultBet = 0

    @property
    def accounts(self):
        return cluster.casino.accounts

    def getRoom(self, ctx: commands.Context) -> Room:
        """Renvoie une salle."""
        if not ctx.guild.id in self.rooms:
            self.rooms[ctx.guild.id] = Room()
        return self.rooms[ctx.guild.id]

    async def send(self, ctx: commands.Context, content: str = "", embed=None):
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

    @commands.group(aliases=["bj"])
    async def blackjack(self, ctx: commands.Context):
        """Groupe de commandes du BlackJack."""
        if not ctx.invoked_subcommand:
            await self.send(ctx, "> Erreur")
        await ctx.message.delete()

    # @blackjack.error
    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):
        """Envoie l'erreur aux utilisateurs."""
        self.send(ctx, error)
        print("erreur capturée")

    @blackjack.command(name="créer", aliases=["create", "c"])
    async def create(
        self, ctx: commands.Context, *members: discord.Member, bet: int = None
    ):
        """Créer une partie de BlackJack."""
        self.checkBet(bet, *members)
        bet = bet or self.defaultBet
        room = self.getRoom(ctx)
        room.players = {member: bet for member in members}
        room.players.update({ctx.author: bet})
        await self.show(ctx)

    def checkBet(self, bet: int, *members: discord.Member):
        """Vérifie les paris de chaque joueurs."""
        for member in members:
            if self.accounts[member.id].coins < bet:
                raise Exception(
                    f"> {member.name} n'as pas assez pour pas parier {bet} coins."
                )

    async def show(self, ctx: commands.Context):
        """Affiche une intégration de BlackJack."""
        await self.send(ctx, f"> Partie de BlackJack crée.")
        await self.updateEmbed(ctx)
        await self.addCreateReactions(ctx)
        await self.react(ctx)

    async def updateEmbed(self, ctx: commands.Context):
        """Mets à jour une intégration discord."""
        room = self.getRoom(ctx)
        embed = room.getEmbed()
        await self.send(ctx, embed=embed)

    async def addCreateReactions(self, ctx: commands.Context):
        """Ajoute des réactions à une intégration."""
        embed_message = self.getRoom(ctx).embed_message
        await embed_message.add_reaction(Emoji.door)
        await embed_message.add_reaction(Emoji.play)

    async def addGameReactions(self, ctx: commands.Context):
        """Ajoute les réactions du blackjack."""
        embed_message = self.getRoom(ctx).embed_message
        await embed_message.add_reaction(Emoji.sleep)
        await embed_message.add_reaction(Emojoi.player)
        await embed_message.add_reaction(Emoji.double)

    async def react(self, ctx: commands.Context):
        """Attend une réaction."""
        loop = True
        room = self.getRoom(ctx)
        while loop:
            try:
                reaction, user = await self.bot.wait_for(
                    "reaction_add", timeout=self.timeout, check=lambda r, u: not u.bot
                )
                await reaction.remove(user)
                if reaction.emoji == Emoji.door:
                    if user in room.players:
                        await self.removeUser(ctx, user)
                    else:
                        await self.addUser(ctx, user)
                elif reaction.emoji == Emoji.play:
                    await self.start(ctx)
                elif reaction.emoji == Emoji.card:
                    await self.drawCard(ctx, user)
                elif reaction.emoji == Emoji.double:
                    await self.doubleUser(ctx, user)
                elif reaction.emoji == Emoji.sleep:
                    pass
            except asyncio.exceptions.TimeoutError:
                await self.stop(ctx)
        return False

    @blackjack.command(name="rejoindre", aliases=["join", "j"])
    async def join(self, ctx: commands.Context, bet: int = None):
        """Rejoins la partie de BlackJack.
        Si elle n'existe pas en crée une."""
        self.checkBet(bet, ctx.author)
        if ctx.guild.id not in self.rooms:
            await self.create(ctx, bet=bet)
        bet = bet or self.defaultBet
        room = self.rooms[ctx.guild.id]
        room.players[ctx.author] = bet
        await self.send(
            ctx, f"> **{ctx.author.name}** avez bien rejoins la salle d'attente."
        )
        await self.updateEmbed(ctx)

    @blackjack.command(name="quitter", aliases=["leave", "q", "quit"])
    async def leave(self, ctx: commands.Context):
        """Quitte une partie de blackjack."""
        room = self.getRoom(ctx)
        del room.players[ctx.author]
        await self.send(
            ctx, f"> **{ctx.author.name}** a bien quitté la salle d'attente."
        )
        if room.players:
            await self.updateEmbed(ctx)
        else:
            await self.stop(ctx)

    async def removeUser(self, ctx: commands.Context, user: discord.User):
        """Kick un utilisateur de la partie"""
        room = self.getRoom(ctx)
        del room.players[user]
        await self.send(ctx, f"> **{user.name}** a bien quitté la salle d'attente.")
        if room.players:
            await self.updateEmbed(ctx)
        else:
            await self.stop(ctx)

    async def addUser(self, ctx: commands.Context, user: discord.User):
        """Ajoute un utilisateur à la partie."""
        room = self.getRoom(ctx)
        room.players[user] = self.defaultBet
        await self.send(ctx, f"> **{user.name}** a bien rejoint la salle d'attente.")
        await self.updateEmbed(ctx)

    @blackjack.command()
    async def sleep(self, ctx: commands.Context):
        """Se coucher."""
        await self.sleepUser(ctx)

    async def sleepUser(self, ctx: commands.Context, member: discord.Member = None):
        """Couche un utilisateur."""
        member = member or ctx.author
        room = self.getRoom(ctx)
        player = room.find(member)
        player.drawing = False
        self.send(ctx, f"> {member.name} se couche.")

    @blackjack.command(name="retirer", aliases=["draw", "r", "d"])
    async def draw(self, ctx: commands.Context):
        """Retire une carte."""
        await self.drawCard(ctx)

    async def drawCard(
        self, ctx: commands.Context, member: discord.Member = None, visible: bool = True
    ):
        """Tire une carte"""
        member = member or ctx.author
        room = self.getRoom(ctx)

        player = find(ctx, room)
        if not player:
            return await self.send("> Vous n'êtes pas un joueur.")

        if not player.drawing:
            return await self.send("> Vous vous êtes couchés.")

        player.draw(room.blackjack, visible)
        await self.send(f"> {ctx.author.name} a tiré une carte.")

    @blackjack.command(name="doubler", aliases=["double"])
    async def double(self, ctx: commands.Context):
        """Double la mise."""
        await self.doubleUser(ctx)

    async def doubleUser(self, ctx: commands.Context, user: discord.Member = None):
        """Double la mise d'un joueur."""
        member = user or ctx.author
        player = room.find(ctx.author)
        self.checkBet(player.bet, member)
        player.bet += player.bet
        await self.drawCard(ctx, user)
        player.drawing = False

    @blackjack.command(name="parier", aliases=["bet"])
    async def bet(self, ctx: commands.Context, bet: int):
        """Parie un certain montant."""
        if ctx.guild.id not in self.rooms:
            await self.create(ctx)
        bet = bet or self.defaultBet
        if bet < 0:
            raise Exception("Il faut parier une somme positive.")
        self.checkBet(bet, ctx.author)
        room = self.getRoom(ctx)
        room.players[ctx.author] = bet
        await self.send(ctx, f"> **{ctx.author.name}** a parié {bet} coins.")

    @blackjack.command()
    async def start(self, ctx: commands):
        """Lance la partie de BlackJack."""
        room = self.getRoom(ctx)
        await self.addGameReactions(ctx)
        players = []
        for player, bet in room.players.items():
            self.accounts[
                player.id
            ].coins -= bet  # Enleve la somme misée du total des coins du joueur
            bj.Player()
            players.append(bj.NormalPlayer(player.id, bet))

        room.blackjack = bj.BlackJack(players)
        room.blackjack.main()

    @blackjack.command()
    async def stop(self, ctx: commands.Context):
        """Arrête la partie."""
        if ctx.guild.id not in self.rooms:
            raise Exception("Partie inexistante.")
        room = self.rooms[ctx.guid.id]
        await room.stop()
        del self.rooms[ctx.guid.id]

    @blackjack.command(name="ici", aliases=["here"])
    async def here(self, ctx: commands.Context):
        """Déplace le blackjack en bas."""
        room = self.getRoom(ctx)
        await room.stop(ctx)
        await self.show(ctx)

    @blackjack.command()
    async def kick(self, ctx: commands.Context, member: discord.Member):
        """Déplace le blackjack en bas."""
        room = self.getRoom(ctx)
        await self.removeUser(ctx, member)
        if room.players:
            await self.updateEmbed(ctx)
        else:
            await self.stop(ctx)


def setup(bot):
    bot.add_cog(BlackJack(bot))
