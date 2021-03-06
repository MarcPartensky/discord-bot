from models.shops.shop import Shop, Item
from config.config import check
from config import emoji
from discord.ext import commands

import discord
import inspect


class CommandsShop(Shop):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.shop.info.default_price = 100

    @property
    def default_price(self):
        return self.shop.info.default_price

    @default_price.setter
    def default_price(self, value):
        self.shop.info.default_price = value

    @default_price.deleter
    def default_price(self):
        del self.shop.info.default_price

    def sell_for(self, *args, **kwargs):
        pass

    def sell(self, func):
        async def decorated(cmd, ctx: commands.Context, *args, **kwargs):
            item = self.shop[func.__qualname__]
            item.setdefaults(
                _id=func.__qualname__,
                name=func.__name__,
                description=func.__doc__,
                price=self.default_price,
            )
            item = self.shop[func.__qualname__]
            if ctx.author.id in self.masters:
                return await func(cmd, ctx, *args, **kwargs)
            checkfunc = check.consent(f"payer {item.price} {emoji.euro}.")(func)
            await ctx.bot.get_cog("Users").connect(ctx)
            user = self.users.accounts[ctx.author.id]
            if user.money < item.price:
                return await ctx.send(
                    "Vous n'avez pas assez d'argent dans votre portefeuille."
                )
            user.money -= item.price
            self.users.accounts.post(user)
            return await checkfunc(cmd, ctx, *args, **kwargs)

        item = self.shop[func.__qualname__]
        item.setdefaults(price=self.default_price)
        decorated.__doc__ = str(item.price) + emoji.money_bag + func.__doc__
        decorated.__name__ = func.__name__
        decorated.__signature__ = inspect.signature(func)
        return decorated
