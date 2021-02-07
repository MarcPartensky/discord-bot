import discord


class NotAuthorized(Exception):
    def __init__(self, user: discord.User, author: discord.User = None):
        self.user = user
        self.author = author
        self.message = self.tell()

    def tell(self):
        if self.author == self.user:
            return "Vous ne pouvez pas vous payer vous même"
        else:
            return f"{self.user.name} n'a pas les droits."

    def __str__(self):
        return self.message
