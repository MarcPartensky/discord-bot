import random
import urllib.request

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

    def __init__(self, category:str, number:str, visible:bool=False):
        self.category = category
        self.number = number
        self.visible = visible

    @property
    def value(self):
        if self.number.isdigit():
            n = int(self.number)
            if n == 1:
                return [1, 11]
            return [n]
        else:
            return [10]
    

class BlackJack:
    # cards =  ["co1","co2","co3","co4","co5","co6","co7","co8","co9","co10","coJ","coQ","coK","t1","t2","t3","t4","t5","t6","t7","t8","t9","t10","tJ","tQ","tK","p1","p2","p3","p4","p5","p6","p7","p8","p9","p10","pJ","pQ","pK","ca1","ca2","ca3","ca4","ca5","ca6","ca7","ca8","ca9","ca10","caJ","caQ","caK"]
    maxPlayers = 8

    @property
    @classmethod
    def allCards(cls):
        return [Card(c, n) for c in cls.categories for n in cls.number]

    def __init__(self, players=[], banker=Banker()):
        self.cards = BlackJack.allCards
        self.inGameCards = []
        self.players = players
        self.banker = banker
        self.turn = 0

    def burn(self, n):
        for i in range(n):
            del self.cards[0]

    def shuffle(self):
        self.cards = BlackJack.cards
        random.shuffle(self.cards)

    def main(self):
        self.banker.drawAll(self)
        self.turn = 0
        self.shuffle()
        while not self.isDone():
            self.turn += 1
            if turn == 1:
                self.firstTurn()
            elif turn == 2:
                self.secondTurn()
            else:
                self.typicalTurn()
            self.play()
            for player in self.players:
                player.totalValue = 0
                for card in player.cards:
                    player.totalValue += card.value

    def firstTurn(self):
        self.burn(self, 5)
        self.banker.drawAll(self, True,2)
        self.banker.draw(self, banker, False)
        return True
    
    def secondTurn(self):
        for player in self.players:
            if bool(input("Spliter ?")):
                player.split()

            elif bool(input("Doubler la mise ?")):
                player.bet += player.bet
                banker.draw(game, player,visible)

            elif bool(input("Demander une carte ? ")):
                banker.draw(game, player,visible)
                player.outOfNumber()
            
            if bool(input("Stoper ? ")):
                player.drawing = False

        ####Tour Banker####
    
    def typicalTurn(self):
        for player in self.players:
            if player.drawing == True:

                if bool(input("Demander une carte ? ")):
                    draw = "🃏"
                    banker.draw(game, player,visible)
                    player.outOfNumber()

                if bool(input("Stoper ? ")):
                    stop = "❌"
                    player.drawing = False


    def play():
        for player in self.players:
            if not player.drawing:
                continue
            player.play(self)

    def isDone():
        return all([not player.drawing for player in self.players])


class Player:
    def blackJack(self, game):
        self.totalValue = 0
        for card in self.cards:
            self.totalValue += card.value

        if len(self.cards) == 2 and self.totalValue == 21:
            self.draw = False
            self.blackJack = True
        return self.blackJack

    def outOfNumber(self, game):
        self.totalValue = 0
        for card in player.cards:           
            self.totalValue += card.value
        if totalValue > 21:
            self.drawing = False
        return not self.drawing


class NormalPlayer(Player):
    def __init__(self, id:int, bet:int, cards:list=[], drawing:bool=True):
        self.bet = bet
        self.cards = cards
        self.drawing = drawing
        self.id = id
        self.totalValue = 0
        self.blackJack = False

class Cheater(Player):
    def play(self, game):
        game.shuffledCards

class Banker(Player):

    def __init__(self, cards:list=[], drawing=True):
        self.cards = cards
        self.drawing = drawing
        self.totalValue = 0
        self.blackJack =  False
    
    def draw(self, game, player, visible):
        player.cards.append(self.cards.pop(0))
        player.cards[-1].visible = visible
        
    def drawAll(self, game, visible, n):
        for i in range(n):
            for player in self.players:
                self.draw(self, game, player, visible)
    

