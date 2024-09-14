from config.config import prefix, cluster
from discord.ext import commands
import discord
import random

from models.connect4 import Board, Player, Human, Bot, Token, Color


class Puissance4(commands.Cog):
    tokens = [Token.yellow, Token.red]
    numbers = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣"]
    color_names = ["Jaune", "Rouge"]

    def __init__(self, bot: commands.Bot, board=Board()):
        self.bot = bot
        self.done = False
        self.players = [Human(), Human()]
        self.board = board
        self.tokens = ["   :yellow_circle:  ", "   :red_circle:  ", 11 * " "]
        self.done = False
        self.message = None
        self.grid_message = None
        self.bet = None
        self.player = None
        self.against = None

    @commands.command(name="p4-random")
    async def random(self, ctx):
        """Rempli le plateau aléatoirement."""
        w, h = self.board.size
        for x in range(w):
            for y in range(h):
                self.board.grid[x][y] = random.choice(
                    [Token.red, Token.yellow, Token.empty]
                )
        await self.show()

    @commands.command(
        name="p4-jouer", aliases=["p4-lancer", "p4-play", "p4-start", "p4-rejouer"]
    )
    @random.before_invoke
    async def start(
        self, ctx: commands.Context, against: discord.Member = None, bet: int = None
    ):
        """Lance le jeu du puissance 4."""
        self.player = ctx.author
        self.against = against
        self.bet = bet
        self.done = False
        self.message = await ctx.send("Nouvelle partie.")
        self.grid_message = await ctx.send("grid")
        self.board = Board()
        await self.show()
        color_name = type(self).color_names[self.board.turns % 2]
        await self.message.edit(content=f"Au tour du joueur {color_name}.")

    @commands.command(name="p4-stop")
    async def stop(self, ctx):
        """Arrête le jeu du puissance 4."""
        if self.grid_message and self.message:
            await self.grid_message.delete()
            await self.message.delete()
        else:
            await ctx.send("Aucune partie de puissance 4 en cours.")

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, member: discord.Member):
        """Détecte les réactions des membres."""
        if member.id == int(self.bot.id):
            return
        print(member.id, self.bot.id)
        if str(reaction) in type(self).numbers and member in [
            self.player,
            self.against,
        ]:
            self.choice = type(self).numbers.index(str(reaction))
            await reaction.remove(member)
            await self.play()
            await self.show()

    # @cog_before_invoke(start)
    async def show(self):
        """Affiche le plateau sous forme de message discord."""
        w, h = self.board.size
        line = "|" + 52 * "-" + "|" + "\n"
        line_separator = "|"
        column_separator = "\n" + line
        t = []
        for y in range(h):
            l = []
            for x in range(w):
                if self.board.grid[x][y] == Token.yellow:
                    l.append(self.tokens[0])
                elif self.board.grid[x][y] == Token.red:
                    l.append(self.tokens[1])
                else:
                    l.append(self.tokens[2])
            l = "|" + line_separator.join(l) + "|"
            t.append(l)
        text = line + column_separator.join(t) + "\n" + line
        await self.grid_message.edit(content=text)
        for number in type(self).numbers:
            emoji = number
            await self.grid_message.add_reaction(emoji=emoji)

    # def update(self):
    #     bx, by = self.board.size
    #     for event in pygame.event.get():
    #         if event.type == pygame.QUIT:
    #             self.done = True
    #         elif event.type == MOUSEBUTTONDOWN:
    #             self.mouse = int(bx*event.pos[0]/wx), int(by*event.pos[1]/wy)
    #             self.clicking = True
    #         elif event.type == KEYDOWN:
    #             if event.key==K_q or event.key == K_ESCAPE:
    #                 self.done = True
    #             elif event.key==K_SPACE:
    #                 self.reset()
    #                 self.show()

    async def play(self):
        """Joue au puissance 4."""
        if self.board.full or self.board.won:
            return
        turn = self.board.turns % 2
        player = self.players[turn]
        token = type(self).tokens[turn]
        if isinstance(player, Human):
            choice = self.choice
        elif isinstance(player, Bot):
            choice = player.play(self.board, token)
        try:
            self.board.insert(choice, token)
        except Board.ColumnFull:
            await self.message.edit(content="La colonne est pleine.")
            return
        self.board.update_full()
        self.board.update_won()
        self.board.turns += 1
        color_name = type(self).color_names[self.board.turns % 2]
        await self.message.edit(content=f"Au tour du joueur {color_name}.")
        if self.board.full or self.board.won:
            await self.end()

    async def end(self):
        """Affiche un message de fin quand la partie est finie."""
        last_token = type(self).tokens[(self.board.turns - 1) % 2]
        msg = f" Tapez: '{prefix}p4-rejouer'."
        if self.board.won:
            if last_token == Token.red:
                await self.message.edit(content="Le joueur Rouge gagne." + msg)
            else:  # and yellow
                await self.message.edit(content="Le joueur Jaune gagne." + msg)
        else:
            await self.message.edit(content="Personne ne gagne." + msg)


async def setup(bot):
    await bot.add_cog(Puissance4(bot))
