from discord.ext import commands
import inspect

class Shop:
    def __init__(self, masters, cluster):
        self.default_price = 15
        self.premium_members = masters
        self.users = cluster.users
        self.bank = cluster.bank
        self.shop_emoji = "💰"

    def sell(self, price):
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