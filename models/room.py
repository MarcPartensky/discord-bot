from discord.ext import commands
import discord

class Room:
    """Representation of a room to differentiate the state of
    the cog depending on the server the bot is in."""

    def __init__(self):
        """Create a room."""
        self.embed_message:discord.Message = None
        self.message:discord.Message = None

    def send(self, ctx:commands.Context, content:str="", embed:discord.Embed=None, **kwargs):
        """Send using one message at a time."""
        if embed:
            if self.embed_message:
                await self.embed_message.edit(content=content, **kwargs)
            else:
                self.embed_message = await ctx.send(content, **kwargs)
        else:
            if self.message:
                await self.message.edit(embed=embed, **kwargs)
            else:
                self.embed_message = await ctx.send(embed=embed, **kwargs)

