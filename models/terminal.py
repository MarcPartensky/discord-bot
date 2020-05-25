from config.config import access, status, masters, prefix
from utils import tools

from discord.ext import commands, tasks
import discord
import subprocess
import sys
import os
import copy

class Terminal(commands.Cog):
    def __init__(self, bot:commands.Bot, **kwargs):
        super().__init__(**kwargs)
        self.bot = bot
        self.on = False
        self.process = None
        self.stdin = ""

    @commands.Cog.listener()
    async def on_message(self, msg:discord.Message):
        """React to messages."""
        if msg.author.bot: return
        if not msg.author.id in masters: return
        if msg.content.startswith(prefix): return
        # if not self.process:
        #     self.process = subprocess.Popen(msg.content, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # else:
        #     self.process = subprocess.Popen(msg.content, shell=True, stdin=self.process.stdin, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # out = self.process.stdout.read()
        # print(out)
        # out = out.decode('utf-8')
        # if out:
        #     await msg.channel.send(out)
        # return


        try:
            result = subprocess.check_output(self.stdin+msg.content, shell=True, universal_newlines=True)
            if result:
                await msg.channel.send(result)
            else:
                self.stdin += msg.content+"; "
        except Exception as e:
            await msg.channel.send(e)

def setup(bot):
    bot.add_cog(Developper(bot))