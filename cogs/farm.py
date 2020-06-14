from discord.ext import commands, tasks
# from config.emoji import farm
from config.config import cluster, check, access


class Farm(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot
        self.farms:MongoDatabase = cluster.farms
        self.users:MongoDatabase = cluster.users

    @commands.group(name='ferme', aliases=['farm'])
    async def farm(self, ctx:commands.Context):
        """Commandes de la ferme."""


    @farm.command(name="créer")
    async def create(self, ctx:commands.Context, name:str):
        """Crée une ferme."""
        user = self.users.accounts[ctx.author.id]
        user.setdefaults(farms=0, max_farms=1)
        if user.farms >= user.max_farms:
            msg = "Vous ne pouvez pas crée plus de {user.max_farms} fermes."
            return await ctx.send(msg)

        farm = self.farms[name]
        farm.owners = [ctx.author.id]
        farm.farmers = [ctx.author.id]
        farm.fields = 1

        msg = "Vous venez de crée la ferme {name}."
        await ctx.send(msg)

    @farm.command(name="supprimer")
    @check.consent("supprimer cette ferme.")
    async def delete(self, ctx:commands.Context, name:str):
        """Supprime une ferme."""
        farm = self.farms[name]
        if farm.owner == ctx.author.id:
            del self.farms[name]



def setup(bot):
    bot.add_cog(Farm(bot))

"""
users:Database
- accounts:Collection
    - *account:Post
        - ...
        - farms: int = 0
        - max_farms: int = 1
    - items:Post
        - *item: int

users.accounts['machin'].items



farm:Database
- fruits:Collection
    - *fruit:Item
        - id: str (name in snake_case)
        - emoji: str
        - price: int
        - max_level: int
        - products: int
        - seeds: int
        - humidity: int
        - space: int
# - seasons:Collection
# - months:
# - weeks:Collection
- info:Collection
    - structure:

farms:Database
- *farm:Collection
    - *field:Post
        - grid: (list**2)[FieldCase]
    - infos:Post
        owners:list
        farmers:list
    - items:
        - *item
            -
        
    
"""