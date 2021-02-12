#!/usr/bin/env python

"""Les commandes de Marc sont partout."""

import os
import time
import shlex
import subprocess
import yaml
import discord
import functools
import requests
import progressbar

from discord.ext import commands
from config.config import access


class Marc(commands.Cog):
    """Les commandes de Marc sont vraiment partout."""

    marc = "Marc"
    marc_id = 478552571510915072
    api_url = "https://api.github.com/repos/marcpartensky/discord-bot/git/trees/master?recursive=1"
    raw_url = "https://raw.githubusercontent.com/MarcPartensky/discord-bot/master"
    marc_store = "config/marc_store.yml"

    def __init__(self, bot: commands.Bot):
        """Best commands are here."""
        self.bot = bot

    # c'est pour me chauffer
    @commands.command()
    @access.admin
    async def who_is_marc(self, ctx: commands.Context):
        """Répond Marc est Marc."""
        await ctx.send(f"> **{Marc.marc}** est **Marc**.")

    @commands.command()
    @access.admin
    async def is_marc_the_owner(self, ctx: commands.Context):
        """Évidemment on le sait tous!"""
        await ctx.send(__doc__)

    @commands.command()
    @access.admin
    async def load_marc_cogs(self, ctx: commands.Context):
        """Charge les cogs de Marc."""

        cogs_path = os.path.join(os.getcwd(), "cogs")
        if not os.path.exists(cogs_path):
            os.makedirs(os.path.join(cogs_path))

        d = requests.get(Marc.api_url).json

        cogs = []
        for file_info in d["tree"]:
            if file_info["path"].startswith("cogs"):
                cogs.append(file_info["path"].replace("cogs"))
                text = requests.get(os.path.join(Marc.raw_url, file_info["path"])).text

                with open(cogs_path, "w") as f:
                    f.write(text)

        with progressbar.ProgressBar(max_value=len(cogs) + 1) as bar:
            bar.update(0)
            for i, filename in enumerate(cogs):
                bar.update(i + 1)
                self.bot.load_extension(f"cogs.{filename[:-3]}")

        await ctx.send("> **Done!**")

    @commands.group()
    @access.admin
    async def marc(self, ctx: commands.Context):
        """Groupe de commandes de marc."""
        if not ctx.invoked_subcommand:
            raise Exception("Toutes les commandes de Marc sont permises!")

    @marc.command()
    @access.admin
    async def run(self, ctx: commands.Context, *, command):
        """Run code."""
        await ctx.send(f"> Running: *{command}*")
        if ctx.author.id == Marc.marc_id:
            print(shlex.split(command))
            process = subprocess.Popen(command.split(" "), stdout=subprocess.PIPE)
            stdout = process.communicate()[0]
            # await ctx.send(f"> {process.stdout.read()}")
            await ctx.send(f"{stdout.decode('utf-8')}")
        else:
            time.sleep(1)
            await ctx.send("wait", delete_after=9)
            time.sleep(2)
            await ctx.send("humm", delete_after=7)
            time.sleep(2)
            await ctx.send("let me see", delete_after=5)
            time.sleep(2)
            await ctx.send("humm hummm", delete_after=3)
            time.sleep(3)
            await ctx.send("**NOPE**")

    @marc.command()
    @access.admin
    async def website(self, ctx: commands.Context):
        """"Renvoie l'url du site de Marc."""
        await ctx.send("> https://marcpartensky.com")

    @marc.command()
    @access.admin
    async def fourier(self, ctx: commands.Context):
        """Vive fourier."""
        await ctx.send(
            "https://camo.githubusercontent.com/49845b8edeb"
            "73d1e59403369c9a40e6d404eaa171dc27183fcfdd0537"
            "3c6ffbb/68747470733a2f2f63646e2e646973636f7264"
            "6170702e636f6d2f6174746163686d656e74732f353037"
            "3531393135373338373133323934302f38303830333930"
            "32343032323235373639342f666f75726965722e676966"
        )

    @commands.command()
    @access.admin
    async def store(self, ctx: commands.Context, *args):
        """Send the store."""

        args = list(args)

        config_dir = Marc.marc_store.split("/")[0]
        # config_dir, config_file = Marc.marc_store.split("/")

        if not os.path.exists(config_dir):
            os.makedirs(config_dir)

        if not os.path.exists(Marc.marc_store):
            with open(Marc.marc_store, "w") as stream:
                stream.write("author: Marc")

        if len(args) == 1:
            if args[0] == "reset":
                with open(Marc.marc_store, "w") as stream:
                    stream.write("author: Marc")
                args = []

        # if len(args) == 1:
        #     if args[1] == "delete":
        #         with open(Marc.marc_store, "w") as stream:
        #             stream.write("author: Marc")

        # get all
        if len(args) == 0:
            with open(os.path.abspath(Marc.marc_store), "r") as stream:
                content = stream.read()
            return await ctx.send("```yaml\n{}\n```".format(content))

        with open(os.path.abspath(Marc.marc_store), "r") as stream:
            d = yaml.full_load(stream)

        path = args[0].split("/")
        key = path[-1]

        di = d
        for ki in path[:-1]:
            if ki not in di:
                di[ki] = {}
            # print(d, ki, di[ki])
            di = di[ki]

        # di = functools.reduce(dict.__getitem__, [d] + path)
        # print(di)

        if len(args) == 1:
            return await ctx.send(f"> {di[key]}")

        # set
        elif len(args) > 1:
            value = " ".join(args[1::])
            di[key] = value

            with open(Marc.marc_store, "w") as stream:
                yaml.dump(d, stream)

            return await ctx.send(f"> Stored in **{args[0]}** : **{value}**")


def setup(bot: commands.Bot):
    """Setup le marc cog."""
    bot.add_cog(Marc(bot))
