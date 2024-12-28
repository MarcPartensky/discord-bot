
#!/bin/env python

from config.config import access, cluster
from discord.ext import commands, tasks
from discord.ext.commands import MessageNotFound
import os
import discord
import yaml

ROLE = "Library"

class Library(commands.Cog):
    """Store config on discord servers as attachments."""
    tmp_directory = os.environ.get("TMP_DIRECTORY") or "/tmp"

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.filename = "config.yml"
        self.filepath = f"/tmp/{self.filename}"
        self.channel_id = int(os.environ.get("CHANNEL_ID_CONFIG") or 0)

    # @property
    # def storage(self):
    #     return self.bot.get_cog("Storage")

    @property
    def channel(self) -> discord.TextChannel:
        return self.bot.get_channel(self.channel_id)

    async def create_config(self):
        """Créer un fichier de config pour la librairie si une existe pas déjà."""
        config = dict(library=dict(channel_id=self.channel_id))
        with open(self.filepath, "w") as f:
            yaml.safe_dump(config, f)

        if not self.channel:
            raise ValueError("Discord channel not found")

        with open(self.filepath, 'rb') as f:
            await self.channel.send(file=discord.File(f, filename=self.filename))


    @commands.group(aliases=["lib"])
    async def library(self, ctx: commands.Context):
        """Groupe de commandes du cog 'Backup'."""
        if not ctx.invoked_subcommand:
            if not self.channel_id:
                await ctx.send("> Un salon textuel doit être claim pour utiliser la config.")
            else:
                await ctx.send("> Aucune sous-commande invokée.")

    @library.command(name="claim")
    @commands.has_role(ROLE)
    async def claim_channel(self, ctx: commands.Context):
        """Déclare le salon textuel de la library."""
        self.channel_id = ctx.channel.id
        await self.create_config()
        await ctx.send(f"> Salon textuel {ctx.channel.id} sélectionné pour le stockage de la config.")

    @library.command(name="write")
    @commands.has_role(ROLE)
    async def write_cmd(self, ctx: commands.Context, key: str, value):
        """Écrit une valeur dans la library."""
        await self.write(key, value)
        # await ctx.send(f"> Salon textuel {ctx.channel.id} sélectionné pour le stockage de la config.")

    async def read(self, attribute):
        return (await self.get_library())[attribute]

    async def write(self, attribute, value):
        library =  await self.get_library()
        print(1, library)
        library[attribute] = value
        print(2, library)
        await self.set_library(library)

    async def search_attachment(self, limit: int):
        """Search for the attachment and message."""
        async for message in self.channel.history(limit=limit, oldest_first=False):  # Adjust limit as needed
            for attachment in message.attachments:
                print(f"attachement: {attachment.filename}")
                if attachment.filename == self.filename:
                    return (message, attachment)
        raise MessageNotFound("No library file found.")

    async def get_library(self, limit=10) -> dict:
        """Get the library from discord"""
        _, attachment = await self.search_attachment(limit)
        await attachment.save(self.filepath)
        with open(self.filepath, "r") as f:
            d = yaml.safe_load(f)
        return d


    async def set_library(self, library, limit=10):
        """Set the library to discord"""
        message, attachment = await self.search_attachment(limit)
        # await message.remove_attachments(attachment)
        await message.delete()

        with open(self.filepath, "w") as f:
            yaml.safe_dump(library, f)

        with open(self.filepath, "rb") as f:
            # await message.add_files()
            file = discord.File(fp=f, filename=self.filename)
            await self.channel.send(file=file)


async def setup(bot: commands.Bot):
    await bot.add_cog(Library(bot))
