#!/usr/bin/env python
"""HTTP web service to interact with the bot."""
__author__ = "Marc Partensky"

# from config.config import cluster, access, check
# from utils.check import check
# from utils import tools

from discord.ext import commands

# import discord
import os

import server
from aiohttp import web


class API(commands.Cog):
    """HTTP web service to interact with the bot."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.server = server.HTTPServer(
            bot=self.bot,
            host=os.environ.get("DISCORD_BOT_HOST") or "localhost",
            port=int(os.environ.get("DISCORD_BOT_PORT") or "8000"),
        )
        self.bot.loop.create_task(self._start_server())

    async def _start_server(self):
        """Task to run the HTTP server."""
        await self.bot.wait_until_ready()
        await self.server.start()

    # async def checker(self, request):
    #     return request.headers.get("authorization") == "password"

    async def fail_handler(self, request):
        return web.json_response(data={"message": "you are not authorized"}, status=401)

    @server.add_route(path="/", method="GET", cog="API")
    @server.check(predicate="checker", fail_handler="fail_handler")
    async def home(self, request):
        # self.bot.mes
        return web.json_response(data={"foo": "bar"}, status=200)


def setup(bot: commands.Bot):
    bot.add_cog(API(bot))
