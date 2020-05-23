import inspect
import discord

class Access:
    def __init__(self, masters, rejection="Vous n'avez pas les droits."):
        self.masters = masters
        self.rejection = rejection
        self.admin_emoji = "⚜️"
        self.member_emoji = "✅"
        self.bank_emoji = ""
        self.decorated = 0

    def limit(self, *authorized):
        """Limite l'accès à une fonction aux autorisés."""
        def f(func):
            """Impose des limites d'accès à une fonction."""
            async def decorated(obj, ctx, *args, **kwargs):
                if ctx.author.id in authorized or 'authorized' in ctx.__dict__:
                    return await func(obj, ctx, *args, **kwargs)
                else:
                    await ctx.send(self.rejection)
            decorated.__doc__ = self.admin_emoji+func.__doc__                
            if hasattr(func, 'qualified_name'):
                decorated.__name__ = func.qualified_name
            else:
                decorated.__name__ = func.__name__
            sig = inspect.signature(func)
            decorated.__signature__ = inspect.signature(func)
            return decorated
        return f


    def admin(self, func):
        """Impose la condition d'être admin."""
        async def decorated(obj, ctx, *args, **kwargs):
            if ctx.author.id in self.masters or 'authorized' in ctx.__dict__:
                return await func(obj, ctx, *args, **kwargs)
            else:
                await ctx.send(self.rejection)
        decorated.__doc__ = self.admin_emoji+func.__doc__
        decorated.__name__ = func.__name__
        sig = inspect.signature(func)
        # decorator.__signature__ = sig.replace(parameters=tuple(sig.parameters.values())[1:])
        decorated.__signature__ = inspect.signature(func)
        decorated.__admin__ = True
        return decorated

    def cog_admin(self, command):
        """Impose la condition d'être admin à une commande."""
        print('command name in cog admin 1:', command.name)
        command.help = self.admin_emoji+command.help
        def decorator(func):
            async def decorated(obj, ctx, *args, **kwargs):
                print("here's your context:", ctx)
                if ctx.author.id in self.masters or 'authorized' in ctx.__dict__:
                    return await func(obj, ctx, *args, **kwargs)
                else:
                    await ctx.send(self.rejection)
            return decorated
        command.__call__ = decorator(command.__call__)
        print('command name in cog admin 2:', command.name)
        return command

    def member(self, func):
        """Impose la condition d'être membre."""
        async def decorated(ctx, *args, **kwargs):
            if str(ctx.author) in self.masters:
                return await func(ctx, *args, **kwargs)
            else:
                await ctx.send(self.rejection)
        decorated.__name__ = func.__name__
        sig = inspect.signature(func)
        decorated.__signature__ = inspect.signature(func)
        return decorated

    def check(self):
        """Demande une confirmation."""
        pass


class Error:
    def tell(self):
        """Envoie le message d'erreur."""
        discord.ext.commands.errors.MissingRequiredArgument
