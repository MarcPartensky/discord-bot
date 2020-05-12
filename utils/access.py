import inspect
import discord

class Access:
    def __init__(self, masters, rejection="Vous n'avez pas les droits."):
        self.masters = masters
        self.rejection = rejection
        self.admin_emoji = "⚜️"
        self.member_emoji = "✅"
        self.bank_emoji = ""

    def limit(self, *authorized):
        """Limite l'accès à une fonction aux autorisés."""
        def f(func):
            """Impose des limites d'accès à une fonction."""
            async def decorator(obj, ctx, *args, **kwargs):
                if ctx.author.id in authorized or 'authorized' in ctx.__dict__:
                    return await func(obj, ctx, *args, **kwargs)
                else:
                    await ctx.send(self.rejection)
            decorator.__doc__ = self.admin_emoji+func.__doc__                
            decorator.__name__ = func.__name__
            sig = inspect.signature(func)
            decorator.__signature__ = inspect.signature(func)
            return decorator
        return f


    def admin(self, func):
        """Impose la condition d'être admin."""
        async def decorator(obj, ctx, *args, **kwargs):
            if ctx.author.id in self.masters or 'authorized' in ctx.__dict__:
                return await func(obj, ctx, *args, **kwargs)
            else:
                await ctx.send(self.rejection)
        decorator.__doc__ = self.admin_emoji+func.__doc__                
        decorator.__name__ = func.__name__
        sig = inspect.signature(func)
        # decorator.__signature__ = sig.replace(parameters=tuple(sig.parameters.values())[1:])
        decorator.__signature__ = inspect.signature(func)
        return decorator


    def member(self, func):
        """Impose la condition d'être membre."""
        async def decorator(ctx, *args, **kwargs):
            if str(ctx.author) in self.masters:
                return await func(ctx, *args, **kwargs)
            else:
                await ctx.send(self.rejection)
        decorator.__name__ = func.__name__
        sig = inspect.signature(func)
        decorator.__signature__ = inspect.signature(func)
        return decorator

    def check(self):
        """Demande une confirmation."""
        pass


class Error:
    def tell(self):
        """Envoie le message d'erreur."""
        discord.ext.commands.errors.MissingRequiredArgument
