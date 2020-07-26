import random
import urllib.request
from PIL import Image
from collections import namedtuple
import os
# import PIL

# urllib.request.urlretrieve(
#     "https://upload.wikimedia.org/wikipedia/commons/thumb/3/36/Playing_card_club_A.svg/1024px-Playing_card_club_A.svg.png",
#     "as de trêfle.jpg")



class CardDeck:


    base_url = ""
    "Trèfles"
    "https://upload.wikimedia.org/wikipedia/commons/thumb/3/36/Playing_card_club_A.svg/1024px-Playing_card_club_A.svg.png"
    "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f5/Playing_card_club_2.svg/1024px-Playing_card_club_2.svg.png"
    "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Playing_card_club_3.svg/1024px-Playing_card_club_3.svg.png"
    "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3d/Playing_card_club_4.svg/1024px-Playing_card_club_4.svg.png"
    "https://upload.wikimedia.org/wikipedia/commons/thumb/5/50/Playing_card_club_5.svg/1024px-Playing_card_club_5.svg.png"
    "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a0/Playing_card_club_6.svg/1024px-Playing_card_club_6.svg.png"
    "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Playing_card_club_7.svg/1024px-Playing_card_club_7.svg.png"
    "https://upload.wikimedia.org/wikipedia/commons/thumb/e/eb/Playing_card_club_8.svg/1024px-Playing_card_club_8.svg.png"
    "https://upload.wikimedia.org/wikipedia/commons/thumb/2/27/Playing_card_club_9.svg/1024px-Playing_card_club_9.svg.png"
    "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3e/Playing_card_club_10.svg/1024px-Playing_card_club_10.svg.png"
    "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b7/Playing_card_club_J.svg/1024px-Playing_card_club_J.svg.png"
    "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f2/Playing_card_club_Q.svg/1024px-Playing_card_club_Q.svg.png"
    "https://upload.wikimedia.org/wikipedia/commons/thumb/2/22/Playing_card_club_K.svg/1024px-Playing_card_club_K.svg.png"

    # dos noir
    "https://opengameart.org/sites/default/files/card%20back%20black.png"
    # dos rouge
    "https://opengameart.org/sites/default/files/card%20back%20red_0.png"

    "Pique"
    "https://upload.wikimedia.org/wikipedia/commons/thumb/2/25/Playing_card_spade_A.svg/1024px-Playing_card_spade_A.svg.png"
    "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f2/Playing_card_spade_2.svg/1024px-Playing_card_spade_2.svg.png"
    "https://upload.wikimedia.org/wikipedia/commons/thumb/5/52/Playing_card_spade_3.svg/1024px-Playing_card_spade_3.svg.png"
    "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2c/Playing_card_spade_4.svg/1024px-Playing_card_spade_4.svg.png"
    "https://upload.wikimedia.org/wikipedia/commons/thumb/9/94/Playing_card_spade_5.svg/1024px-Playing_card_spade_5.svg.png"
    "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d2/Playing_card_spade_6.svg/1024px-Playing_card_spade_6.svg.png"
    "https://upload.wikimedia.org/wikipedia/commons/thumb/6/66/Playing_card_spade_7.svg/800px-Playing_card_spade_7.svg.png"
    "https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Playing_card_spade_8.svg/800px-Playing_card_spade_8.svg.png"
    "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Playing_card_spade_9.svg/800px-Playing_card_spade_9.svg.png"
    "https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/Playing_card_spade_10.svg/800px-Playing_card_spade_10.svg.png"
    "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bd/Playing_card_spade_J.svg/800px-Playing_card_spade_J.svg.png"
    "https://upload.wikimedia.org/wikipedia/commons/thumb/5/51/Playing_card_spade_Q.svg/800px-Playing_card_spade_Q.svg.png"
    "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9f/Playing_card_spade_K.svg/800px-Playing_card_spade_K.svg.png"
    
    "Coeur"
    "https://upload.wikimedia.org/wikipedia/commons/thumb/5/57/Playing_card_heart_A.svg/800px-Playing_card_heart_A.svg.png"
    "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Playing_card_heart_2.svg/800px-Playing_card_heart_2.svg.png"
    "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b6/Playing_card_heart_3.svg/800px-Playing_card_heart_3.svg.png"
    "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Playing_card_heart_4.svg/800px-Playing_card_heart_4.svg.png"
    "https://upload.wikimedia.org/wikipedia/commons/thumb/5/52/Playing_card_heart_5.svg/800px-Playing_card_heart_5.svg.png"
    "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cd/Playing_card_heart_6.svg/800px-Playing_card_heart_6.svg.png"
    "https://upload.wikimedia.org/wikipedia/commons/thumb/9/94/Playing_card_heart_7.svg/800px-Playing_card_heart_7.svg.png"
    "https://upload.wikimedia.org/wikipedia/commons/thumb/5/50/Playing_card_heart_8.svg/800px-Playing_card_heart_8.svg.png"
    "https://upload.wikimedia.org/wikipedia/commons/thumb/5/50/Playing_card_heart_9.svg/800px-Playing_card_heart_9.svg.png"
    "https://upload.wikimedia.org/wikipedia/commons/thumb/9/98/Playing_card_heart_10.svg/800px-Playing_card_heart_10.svg.png"
    "https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/Playing_card_heart_J.svg/800px-Playing_card_heart_J.svg.png"
    "https://upload.wikimedia.org/wikipedia/commons/thumb/7/72/Playing_card_heart_Q.svg/800px-Playing_card_heart_Q.svg.png"
    "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dc/Playing_card_heart_K.svg/800px-Playing_card_heart_K.svg.png"


    "Carreau"
    "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d3/Playing_card_diamond_A.svg/800px-Playing_card_diamond_A.svg.png"
    "https://upload.wikimedia.org/wikipedia/commons/thumb/5/59/Playing_card_diamond_2.svg/800px-Playing_card_diamond_2.svg.png"
    "https://upload.wikimedia.org/wikipedia/commons/thumb/8/82/Playing_card_diamond_3.svg/800px-Playing_card_diamond_3.svg.png"
    "https://upload.wikimedia.org/wikipedia/commons/thumb/2/20/Playing_card_diamond_4.svg/800px-Playing_card_diamond_4.svg.png"
    "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fd/Playing_card_diamond_5.svg/800px-Playing_card_diamond_5.svg.png"
    "https://upload.wikimedia.org/wikipedia/commons/thumb/8/80/Playing_card_diamond_6.svg/800px-Playing_card_diamond_6.svg.png"
    "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e6/Playing_card_diamond_7.svg/800px-Playing_card_diamond_7.svg.png"
    "https://upload.wikimedia.org/wikipedia/commons/thumb/7/78/Playing_card_diamond_8.svg/800px-Playing_card_diamond_8.svg.png"
    "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9e/Playing_card_diamond_9.svg/800px-Playing_card_diamond_9.svg.png"
    "https://upload.wikimedia.org/wikipedia/commons/thumb/3/34/Playing_card_diamond_10.svg/800px-Playing_card_diamond_10.svg.png"
    "https://upload.wikimedia.org/wikipedia/commons/thumb/a/af/Playing_card_diamond_J.svg/800px-Playing_card_diamond_J.svg.png"
    "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0b/Playing_card_diamond_Q.svg/800px-Playing_card_diamond_Q.svg.png"
    "https://upload.wikimedia.org/wikipedia/commons/thumb/7/78/Playing_card_diamond_K.svg/800px-Playing_card_diamond_K.svg.png"



class Card:
    categories = ['coeur', 'trèfle', 'carreau', 'pique']
    number = [str(i) for i in range(10)] + ['jack', 'queen', 'king']

    def getUrl(self, category, number):
        """Find the the url of a given card."""
        pass

    def __init__(self, category:str, number:str, visible:bool=False, sleeping:bool=False):
        self.category = category
        self.number = number
        self.visible = visible
        self.sleeping = sleeping

    @property
    def value(self):
        if self.number.isdigit():
            n = int(self.number)
            if n == 1:
                return [1, 11]
            return [n]
        else:
            return [10]

class Player:
    def __init__(self, cards:list=[], sleeping:bool=False):
        """Créee un joueur avec ses cartes et s'il est couché."""
        self.cards = cards
        self.sleeping = sleeping

    def hasBlackJack(self):
        """Vérifie si le joueur fait un blackjack."""
        return len(self.cards) == 2 and self.totalValue == 21

    def checkSleeping(self):
        """Vérifie si le joueur est couché."""
        if self.totalValue > 21:
            self.sleeping = True
            
    @property
    def totalValue(self):
        """Affiche le total des cartes d'un joueur."""
        return sum([card.value for card in self.cards])

    def draw(self, game, visible:bool=True):
        """Retire une carte."""
        self.cards.append(game.cards.pop(0))
        self.cards[-1].visible = visible
        self.checkOutOfNumber(game)

class NormalPlayer(Player):
    def __init__(self, id:int, bet:int, cards:list=[], sleeping:bool=False):
        """Définit un joueur normal avec son id, pari, ses cartes et s'il est couché."""
        super().__init__(cards, sleeping)
        self.bet = bet
        self.id = id
        
    def gains(self, banker):
        """Calcule le gain d'un joueur."""
        if player.hasBlackJack():
            return 1.5*player.bet
        if  21 >= player.totalValue > banker.totalValue or (banker.totalValue >= 21 and player.totalValue <= 21):
            return 2*player.bet
        if player.totalValue == banker.totalValue <= 21:
            return bet
        return 0

class Cheater(Player):
    def play(self, game):
        game.cards[0]

class Banker(Player):
    def __init__(self, cards:list=[], sleeping:bool=False):
        """Définit un banquier avec ses cartes et s'il est couché."""
        super().__init__(cards, sleeping)
    
    def play(self, game):
        """Le banquier joue."""
        for card in self.cards:
            card.visible = True       #Rend toutes les cartes du banquier visibles
        if self.cardsValue(cards) <= 17:
            self.draw(game, banker)            #Pioche jusqu'à avoir une valeur d'au moins 17
        self.sleeping = True
        
    def drawAll(self, game, visible, n):
        """Le banquier distribue n cartes aux joueurs."""
        for i in range(n):
            for player in game.players:
                player.draw(game, visible)
    
Vector = namedtuple('Vector', ['x', 'y'])

class Table:
    backgroundPath  = os.path.abspath('assets/blackjack/imgs/green-background.jpg')
    borderPath = os.path.abspath('assets/blackjack/imgs/white-border.png')
    cardSize = Vector(1040, 832)
    
    def __init__(self,
            backgroundPath:str=None,
            borderPath:str=None
        ):
        self.backgroundPath = backgroundPath or Table.backgroundPath
        self.borderPath = borderPath or Table.borderPath
        self.background = Image.open(self.backgroundPath)
        self.border = Image.open(self.borderPath)

    def resize(self):
        """Resize the image of the blackjack."""
        bg = Vector(*self.background.size)
        ratio = Table.cardSize.y/Table.cardSize.x # card ratio in pixel
        c = Vector(bg.x/10, ratio*bg.x/10)
        self.border = self.border.resize((c.x, c.y))
        # bd = Vector(*self.border.size)

    def save(self, filename:str):
        """Save the image of the blackjack created."""
        pass

    def insert(self, cardurl, i):
        """Insert a card on the image."""
        pass


class BlackJack:
    maxPlayers = 8

    @property
    @classmethod
    def allCards(cls):
        return [Card(c, n) for c in cls.categories for n in cls.number]

    def __init__(self, players=[], banker=Banker()):
        """Crée un jeu de blackjack avec ses joueurs et son banquier."""
        self.cards = BlackJack.allCards
        self.table = Table()
        self.inGameCards = []
        self.players = players
        self.banker = banker

    @property
    def bankerTurn(self):
        return all([player.sleeping for player in self.players])
    
    def burn(self, n):
        """Brûle n cartes."""
        for i in range(n):
            del self.cards[0]

    def shuffle(self):
        """Mélange les cartes."""
        self.cards = BlackJack.cards
        random.shuffle(self.cards)

    def main(self):
        self.shuffle()
        self.firstTurn()
        while not self.bankerTurn:
            pass
        banker.play(self)
        self.gains
        
    def firstTurn(self):
        self.burn(5)
        self.banker.drawAll(self,True,2)
        self.banker.draw(self, False)
        self.banker.draw(self)

    def allElementsFalse(self,liste):
        for element in liste:
            if element:
                return False
            return True

    def bankerTurn():
        return all([not player.drawing for player in self.players])


    def show(self):
        """Affiche la table de blackjack actuel."""
        # cw, ch = namedtuple
        # border.resize
        # bgw, bgh = background.size
        # bdw, bdh = border.size[]
        n = len(self.players)
        # bd


