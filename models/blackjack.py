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
    def allCards(cls):
        return [Card(c, n) for c in cls.categories for n in cls.number]

    def __init__(self, players=[]):
        self.cards = BlackJack.allCards
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
        self.burn(self,5)
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
    

