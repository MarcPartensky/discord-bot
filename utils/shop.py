from discord.ext import commands
from models.mongo import Post
import inspect
import time

"""
Shops(Cluster)
- shop1
- shop2
...

Shop(Database)
- rayon1
- rayon2
- rayon3
...
- info
- owners

Rayon(Collection)
- item1
- item2
- item3
...
- info
- owners

Item(Post)
- id
- name
- description
- value
- price
...
- info
- owners
"""

class Item(Post):
    """Shop item.
    - id: Any
    - name: str
    - description: str
    - value: Any
    - price: int
    - creation: int
    - sold: int
    - last_bought: int
    - last_buyer: int
    - price_updates: int
    - last_price_update: int (time.)
    - last_price: int
    - promotion: int (in percent)
    - stock: int
    """
    class Error:
        """Erreur sur un item."""
        def __init__(self, message:str=None):
            message = message or type(self).__doc__
            super().__init__(message)

    @classmethod
    def new(
        cls,
        post,
        value=None
        price:int=None
        name:str=None,
        description:str=None
        creation:int=time.time(),
        stock:int=None
        sold:int=0,
        last_bought:int=None,
        last_buyer:int=None,
        price_updates:int=0,
        last_price_update:int=time.time(),
        last_price:int=None,
        promotion:int=None
        ):
        item = cls(post)
        if not 'price' in item:
            item.price = price
        if not 'value' in item:
            item.value = value
        if not 'name' in item:
            item.name = name
        if not 'description' in item:
            item.description = description
        if not 'creation' in item:
            item.creation = creation
        if not 'stock' in item:
            item.stock = stock
        if not 'sold' in item:
            item.sold = sold
        if not 'last_bought' in item:
            item.last_bought = last_bought
        if not 'last_buyer' in item:
            item.last_buyer = last_buyer
        if not 'price_updates' in item:
            item.price_updates = price_updates
        if not 'last_price_update' in item:
            item.last_price_update = last_price_update
        if not 'last_price' in item:
            item.last_price = last_price
        return item

@shop.commands.sell

# @etienne.boulangerie.sell("pain", 10)
@shop.boulangerie.sell("pain", 10)

class Aisle:
    class Error:
        """Shop error."""
    class NoItemFound(Error):
        """Aucun item trouvé."""
        def __init(self, id):
            super().__init__(f"L'item {id} n'existe pas.")

    def __init__(self, masters, shop, users, emoji=emoji.money_bag):
        self.masters = masters
        self.shop = shop
        self.users = users
        self.shop_emoji = emoji
        # self.premium_members = masters
        # self.users = cluster.users
        # self.shop = cluster.shop

    def sell(self, name:str):
        """Vend un item."""
        item = self.collection[item]

    def sell_for(self, price:int=None):
        """Vend une commande pour un prix donné."""
        price = price or self.default_price
        def decorator(func):
            async def decorated(command, ctx:commands.Context, *args, **kwargs):
                if ctx.author.id in self.premium_members:
                    # await ctx.send(
                    #     "Comme vous êtes premium, "
                    #     "vous n'avez pas eu à payer la commande "
                    #     f"{func.__name__}."
                    # )
                    return await func(commands, ctx, *args, **kwargs)
                account = self.bank.accounts[ctx.author.id]
                if not account:
                    return await ctx.send(
                        "Vous n'avez pas de compte bancaire.\n"
                        "Aide: `.help Bank`."
                    )
                if account.money < price:
                    return await ctx.send(
                        "Vous n'avez pas assez d'argent en banque.\n"
                        "Pour gagner de l'argent essayez le Casino "
                        "ou la catégorie Game.\n",
                        "Vous pouvez aussi acheter un compte premium."
                    )
                account.money -= price
                self.bank.accounts.post(account)
                return await func(command, ctx, *args, **kwargs)
            decorated.__doc__ = str(price)+self.shop_emoji+func.__doc__
            decorated.__name__ = func.__name__
            decorated.__signature__ = inspect.signature(func)
            decorated.__shop__ = True
            return decorated
        return decorator

# class CommandsShop(Shop):
#     """Shop for commands."""
#     def __init__(self, masters, cluster):

    
