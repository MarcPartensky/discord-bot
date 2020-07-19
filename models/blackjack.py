
import random

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
    def cards(cls):
        return [Card(c, n) for c in cls.categories for n in cls.number]

    def __init__(self, players=[]):
        self.cards = BlackJack.cards
        self.inGameCards = []
        self.players = players
        self.banker = Banker()
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
            self.play()

    def firstTurn(self):
        self.burn(self,5)
        self.banker.drawAll(self, True,2)
        self.banker.draw(self, banker, False)
        return True

    def play():
        for player in self.players:
            if not player.drawing:
                continue
            player.play(self)

    def isDone():
        return all([not player.drawing for player in self.players])

class Player:
    def __init__(self, id:int, bet:int, cards:list=[], drawing:bool=True):
        self.bet = bet
        self.cards = cards
        self.drawing = drawing
        self.id = id

    def play(self, game):
        pass

    # def bet(self, game, bet):
    #     self.bet = bet

class Cheater:
    def play(self, game):
        game.shuffledCards


class Banker:
    def __init__(self, cards:list=[], drawing=True):
        self.cards = cards
        self.drawing = drawing
    
    def draw(self, game, player, visible):
        player.cards.append(self.cards.pop(0))
        player.cards[-1].visible = visible
        
    def drawAll(self, game, visible, n):
        for i in range(n):
            for player in self.players:
                self.draw(self, game, player, visible)
