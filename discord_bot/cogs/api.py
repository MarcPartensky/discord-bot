#!/usr/bin/env python
"""HTTP web service to interact with the bot."""
__author__ = "Marc Partensky"

# from config.config import cluster, access, check
# from utils.check import check
# from utils import tools

import os, time
import typing
import uuid
import traceback
import asyncio
import discord
import aiofiles
from discord.ext import commands, tasks
from aiohttp import web

MAX_CHUNK_SIZE = 8 * 1024 * 1024  # 8 MB

class API(commands.Cog):
    """HTTP web service to interact with the bot."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.host = os.environ.get("DISCORD_BOT_HOST") or "localhost"
        self.port = int(os.environ.get("DISCORD_BOT_PORT") or "8000")
        self.guild_id = int(os.environ.get(
            "DISCORD_BOT_GUILD_ID"
        ) or "550332212340326428")
        self.contexts: typing.Dict[str, commands.Context] = {}
        self.channel_id = int(os.environ.get("CHANNEL_ID_NOTIF", "0"))
        self.app = web.Application()
        self._setup_routes()
        self.runner = None
        self.site = None

    async def _delayed_start_server(self):
        """Attend que le bot soit prêt puis démarre le serveur."""
        print("DEBUG: Waiting for bot to be ready...")
        await self.bot.wait_until_ready()
        print("DEBUG: Bot ready, starting server...")
        await self._start_server()

    def _setup_routes(self):
        """Setup all HTTP routes."""
        self.app.router.add_post("/send/user", self.send_user)
        self.app.router.add_post("/send/channel", self.send_channel)
        self.app.router.add_post("/command/channel", self.command_channel)
        self.app.router.add_get("/debug/bot", self.debug_bot)
        self.app.router.add_get("/live", self.live)

    @commands.Cog.listener()
    async def on_ready(self):
        """Démarre le serveur HTTP quand le bot est prêt."""
        if not self._server_started:
            await self._start_server()
            self._server_started = True

    async def _start_server(self):
        """Task to run the HTTP server."""
        try:
            print(f"DEBUG: Starting HTTP server on {self.host}:{self.port}")
            self.runner = web.AppRunner(self.app)
            await self.runner.setup()
            self.site = web.TCPSite(self.runner, self.host, self.port)
            await self.site.start()
            print(f"HTTP SERVER STARTED, LISTENING ON {self.host}:{self.port}")
        except Exception as e:
            print(f"ERROR starting HTTP server: {e}")
            import traceback
            traceback.print_exc()

    async def send_user(self, request: web.Request):
        """API home path."""
        body = await request.json()
        user: discord.User = await self.bot.fetch_user(body["id"])
        await user.send(body["message"])
        return web.json_response(
            data={"text": "Successfully sent message."}, status=200
        )

    async def send_channel(self, request: web.Request):
        """API home path."""
        body = await request.json()
        channel: discord.TextChannel = await self.bot.fetch_channel(body["id"])
        await channel.send(body["message"])
        self.bot.commands
        return web.json_response(
            data={"text": "Successfully sent message."}, status=200
        )

    async def command_channel(self, request: web.Request):
        """API home path."""
        body = await request.json()
        ctx_id = body["ctx"]
        cmd = body["cmd"]
        if "args" in body:
            args = body["args"]
        else:
            args = []
        if "kwargs" in body:
            kwargs = body["kwargs"]
        else:
            kwargs = {}
        channel: discord.TextChannel = await self.bot.fetch_channel(body["id"])
        command_list = []
        for command in self.bot.commands:
            command_list.append(dict(name=command.name, doc=command.short_doc))
            print(command.name)
            if command.name == cmd:
                # context = self.build_context(channel, args)
                ctx = self.contexts[ctx_id]
                try:
                    print(ctx.args)
                    print(ctx.kwargs)
                    ctx.args = args
                    ctx.kwargs = kwargs
                    # command.clean_params
                    # for param in command.params:

                    # print(command._parse_arguments(ctx))
                    # await command.prepare(ctx)
                    # await converter._construct_default(ctx)
                    # await command.callback(context, __p1=command.clean_params)
                    # print(command.clean_params)
                    # print(command.params)
                    # print(command.invoke())
                    # ctx.args = args
                    result = await command.invoke(ctx)
                    return web.json_response(data={"text": str(result)}, status=200)
                except Exception as exception:
                    traceback.print_exc()
                    return web.json_response(
                        data={"error": str(exception), "doc": command.short_doc},
                        status=500,
                    )
        return web.json_response(
            data={"error": "No match found.", "commands": command_list}, status=404
        )

    async def debug_bot(self, request: web.Request):
        """API home path."""
        body = await request.json()
        return web.json_response(data=self.bot, status=200)

    async def live(self, request: web.Request):
        """API home path."""
        return web.json_response(text="OK", status=200)

    @commands.command(name="save-context")
    async def save_context(self, ctx: commands.Context, context_id: str or None):
        """Save a context since it is really hard to build one from scratch."""
        context_id = context_id or str(uuid.uuid1())
        self.contexts[context_id] = ctx
        await ctx.send(f"> Saved context as **{context_id}**")

    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message):
        """Nettoie les messages des salons innapropriés, dès que
        ceux-ci sont postés."""
        if msg.author.bot:
            return


def setup(bot: commands.Bot):
    api_cog = API(bot)
    bot.add_cog(api_cog)
    print("DEBUG: API cog setup() called")
