from discord.ext import commands, tasks

import pickle


class Farm(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.values = {}


def setup(bot):
    bot.add_cog(Farm(bot))

"""
farm.db {
    customer1 {
        infos, 
        farm {
            field1 {
                carrot, potato
                }
            },
            field2 {
                
            }

"""
