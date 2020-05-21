import inspect
from discord.ext import commands

class Check:
    def __init__(self, timeout=60):
        self.timeout = timeout

    def validation(self, func):
        async def decorated(command, ctx:commands.Context, *args):
            await ctx.send("Êtes-vous sur?")
            def check(msg):
                if msg.author == ctx.author:
                    return True
                return False
            try:
                msg = await ctx.bot.wait_for('message', check=check, timeout=self.timeout)
                if msg.content.lower() in ['oui', 'yes', 'yep', 'yup', 'y']:
                    await func(command, ctx, *args)
                elif msg.content.lower() in ['non', 'no', 'nope', 'nop', 'nah', 'n']:
                    await ctx.send("La commande n'a pas été effectué.")
                else:
                    await ctx.send("Réponse invalide veuillez répondre par 'oui' ou 'non'.")
            except TimeoutError:
                await ctx.send("La validation de cette commande a expiré.")
        decorated.__doc__ = func.__doc__
        decorated.__name__ = func.__name__
        decorated.__signature__ = inspect.signature(func)
        decorated.__validation__ = True
        return decorated