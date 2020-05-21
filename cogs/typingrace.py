from config.config import cluster
from models.mongo import Post

from discord.ext import commands, tasks
import discord

import unidecode
import time
import asyncio

import string


class TypingRace(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.users = cluster.users
        self.info = self.users.info
        self.bot = bot
        self.timeout = 30
        self.precision_digits = 1
        
    @commands.command(name="type-letters")
    async def type_letters(self, ctx:commands.Context, *, msg:str):
        """Réécrit les lettres en emoji."""
        msg = unidecode.unidecode(msg)
        msg = msg.lower()
        alphabet = "abcdefghijklmnopqrstuvwxyz"
        msg = list(msg)
        for i,c in enumerate(msg):
            if c in alphabet:
                msg[i] = f':regional_indicator_{c}:'
            # else:
            #     msg[i] = f'`{c}`'
        msg = "".join(msg)
        # msg = msg.replace('?', "**.**")
        # msg = msg.replace('!', ":grey_exclamation:")
        # msg = msg.replace('.', ":white_circle:")
        await ctx.send(msg)

    

    @commands.command(name="typing-race", aliases=["tp", "~"])
    async def typing_race(self, ctx:commands.Context, *, msg:str):
        """Joue à une course de typing sur clavier."""
        await ctx.message.delete()
        msg = unidecode.unidecode(msg)
        w = len(msg.split(' '))
        msg = msg.lower()
        timeout = len(msg)
        await self.type_letters(ctx, msg="~"+msg)
        t = time.time()
        f = 10**self.precision_digits
        
        def check(new_msg):
            new_msg = unidecode.unidecode(new_msg.content)
            return new_msg==msg
        try:
            msg = await self.bot.wait_for('message', check=check, timeout=timeout)
            t = time.time()-t
            wpm = w*60/t
            post = self.users.info[msg.author.id] or Post()
            post.last_typing_speed = wpm
            self.users.info[msg.author.id] = post
            msg = f"{msg.author.name} a pris {int(f*t)/f} secondes."
            msg += f"\nSoit {int(f*wpm)/f} mots par minutes."
        except asyncio.exceptions.TimeoutError:
            t = timeout
            wpm = w*60/t
            msg = f"Trop tard vous avez pris plus de {timeout} secondes."
            msg += f"\nSoit {int(f*wpm)/f} mots par minutes."
        await ctx.send(msg)

    


def setup(bot):
    bot.add_cog(TypingRace(bot))
