from config.emoji import farm
import time


class Fruit:
    def __init__(self, emoji, max_level, growth, price, planted=time.time()):
        self.emoji = emoji
        self.max_level = max_level
        self.growth
        self.planted = planted
        self.price = price

    @property
    def level(self):
        return min((time.time() - self.planted) // self.growth, self.max_level)

    @level.setter
    def level(self, lvl):
        if lvl > self.max_level:
            raise ValueError(f"Le niveau de {self.emoji} ne peux pas excéder {self.max_level}.")
        self.planted = time.time() - lvl * self.growth

    @level.deleter
    def level(self):
        self.planted = time.time()

    def show(self):
        if self.level < 1:
            return farm.seed
        elif self.level == self.max_level:
            return self.emoji

    def replant(self):
        self.level = time.time()
        



class Potato:

    max_level = 2
    def __init__(self, emoji, level=0, max_level=Potato.max_level, growth=5*60):
        super().__init__(emoji, level)s



