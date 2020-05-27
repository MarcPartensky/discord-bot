import inspect
from discord.ext import commands
from utils import tools
from config import emoji

class Check:
    @staticmethod
    def same_author(msg, ctx):
        return msg.author == ctx.author

    def __init__(self, timeout=60):
        self.timeout = timeout
        self.message = None
        self.warning_emoji = emoji.warning
        self.help_message = "Répondre par `oui` ou `non`."
        self.consent_message = "En effectuant cette action vous consentez à"
        self.sure = "Êtes-vous sur?"
        self.yes = ['oui', 'yes', 'yep', 'yup', 'y', 'affirmatif', '+1']
        self.no = ['non', 'no', 'nope', 'nop', 'nah', 'n', 'flemme', 'negatif', '-1']
        self.cancel_answer = "La commande n'a pas été effectué."
        self.invalid_answer = "Réponse invalide veuillez répondre par 'oui' ou 'non'."
        self.timemout_answer = "La validation de cette commande a expiré."

    async def wait_for_check(self, ctx, timeout=None):
        timeout = timeout or self.timeout
        try:
            msg = await ctx.bot.wait_for('message', check=tools.post_passer(Check.same_author, ctx), timeout=self.timeout)
            if msg.content.lower() in self.yes:
                return True
            elif msg.content.lower() in self.no:
                await ctx.send(self.cancel_answer)
            else:
                await ctx.send(self.invalid_answer)
        except TimeoutError:
            await ctx.send(self.timeout_answer)
        return False
    
    def consent(self, message):
        message = self.consent_message + " " + message
        return tools.post_passer(self.validation, message)

    def validate(self, message):
        return tools.post_passer(self.validation, message)

    def warn(self, message):
        return tools.post_passer(tools.post_passer(self.validation, message), True)

    def validation(self, func, message=None, warning=False):
        async def decorated(command, ctx:commands.Context, *args):
            msg = message or self.sure
            msg += (" " + self.help_message)
            await ctx.send(msg)
            self.message = None
            if await self.wait_for_check(ctx):
                return await func(command, ctx, *args)
        if warning:
             decorated.__doc__ = self.warning_emoji+func.__doc__
        else:
            decorated.__doc__ = func.__doc__
        decorated.__name__ = func.__name__
        decorated.__signature__ = inspect.signature(func)
        decorated.__validation__ = True
        return decorated

    def inform(self, message):
        pass


