from discord.ext import commands
import discord

class Field:
    size = (16, 16)
    def __init__(self, size):
        self.grid = grid

    async def show(self, ctx:commands.Context):
        """"Affiche un champ."""

class FieldCase:
    def __init__(self, fruit, level, humidity, fertilizer):
        self.fruit = fruit
        self.humidty = humidity
        self.fertilizer = fertilizer

    def grow(self):
        pass


class EmojiGrid:
    def __init__(self, grid):
        self.grid = grid

    @property
    def size(self):
        return (len(grid), len(grid[0])) # We suppose the columns have the same length.

    async def show(self, msg:discord.Message):
        w, h = self.size
        line = '|'+52*"-"+'|'+"\n"
        line_separator = "|"
        column_separator = "\n"+line
        t = []
        for y in range(h):
            l = []
            for x in range(w):
                l.append(grid[x][y])
            l = '|'+line_separator.join(l)+'|'
            t.append(l)
        text = line+column_separator.join(t)+'\n'+line
        await msg.edit(content=text)
        for number in type(self).numbers:
            emoji = number
            await msg.add_reaction(emoji=emoji)
