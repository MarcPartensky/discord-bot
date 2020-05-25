from config.config import access, status, masters
from utils import tools

from discord.ext import commands, tasks
import discord
import subprocess
import os

class Terminal(commands.Cog):
    def __init__(self, bot:commands.Bot, **kwargs):
        super().__init__(**kwargs)
        self.bot = bot
        self.on = False

    @commands.Cog.listener()
    def on_message(self, msg):
        """React to messages."""
        if msg.author.bot: return
        if not msg.author.id in masters: return
        result = subprocess.check_output(cmd, shell=True, universal_newlines=True); 
        await ctx.send(result)

def setup(bot):
    bot.add_cog(Developper(bot))