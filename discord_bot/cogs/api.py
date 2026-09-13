#!/usr/bin/env python
"""HTTP web service to interact with the bot."""
__author__ = "Marc Partensky"

import asyncio
import functools
import os
import traceback
import typing
import uuid

import discord
from aiohttp import web
from discord.ext import commands


def json_errors(handler):
    """Mappe les exceptions Discord vers des réponses JSON."""
    @functools.wraps(handler)
    async def wrapper(self, request: web.Request):
        try:
            return await handler(self, request)
        except KeyError as e:
            return web.json_response({"error": f"Missing required field: {e}"}, status=400)
        except discord.NotFound:
            return web.json_response({"error": "Not found"}, status=404)
        except discord.Forbidden:
            return web.json_response({"error": "Forbidden"}, status=403)
        except Exception as e:
            traceback.print_exc()
            return web.json_response({"error": str(e)}, status=500)
    return wrapper


class API(commands.Cog):
    """HTTP web service to interact with the bot."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.host = os.environ.get("DISCORD_BOT_HOST", "0.0.0.0")
        self.port = int(os.environ.get("DISCORD_BOT_PORT", "8050"))
        self.token = os.environ.get("DISCORD_BOT_API_TOKEN")
        self.contexts: typing.Dict[str, commands.Context] = {}
        self.runner: typing.Optional[web.AppRunner] = None
        self.site: typing.Optional[web.TCPSite] = None
        self._lock = asyncio.Lock()

        self.app = web.Application(middlewares=[self._auth])
        self.app.router.add_post("/send/user", self.send_user)
        self.app.router.add_post("/send/channel", self.send_channel)
        self.app.router.add_post("/command/channel", self.command_channel)
        self.app.router.add_get("/debug/bot", self.debug_bot)
        self.app.router.add_get("/live", self.live)

    @web.middleware
    async def _auth(self, request: web.Request, handler):
        if self.token and request.path != "/live":
            if request.headers.get("Authorization") != f"Bearer {self.token}":
                return web.json_response({"error": "Unauthorized"}, status=401)
        return await handler(request)

    @commands.Cog.listener()
    async def on_ready(self):
        """on_ready peut se redéclencher à chaque reconnexion: idempotent."""
        async with self._lock:
            if self.site is not None:
                return
            self.runner = web.AppRunner(self.app)
            await self.runner.setup()
            self.site = web.TCPSite(self.runner, self.host, self.port)
            try:
                await self.site.start()
            except OSError:
                self.site = None
                await self.runner.cleanup()
                self.runner = None
                raise
            print(f"HTTP server listening on {self.host}:{self.port}")

    def cog_unload(self):
        if self.runner:
            asyncio.create_task(self.runner.cleanup())

    async def _send(self, request: web.Request, fetch):
        body = await request.json()
        target = await fetch(int(body["id"]))
        await target.send(body["message"])
        return web.json_response({"text": "Successfully sent message."})

    @json_errors
    async def send_user(self, request: web.Request):
        """Send a DM to a Discord user."""
        return await self._send(request, self.bot.fetch_user)

    @json_errors
    async def send_channel(self, request: web.Request):
        """Send a message to a Discord channel."""
        return await self._send(request, self.bot.fetch_channel)

    @json_errors
    async def command_channel(self, request: web.Request):
        """Invoke a bot command on a saved context."""
        body = await request.json()
        command = self.bot.get_command(body["cmd"])
        if command is None:
            return web.json_response({
                "error": "No match found.",
                "commands": [
                    {"name": c.name, "doc": c.short_doc} for c in self.bot.commands
                ],
            }, status=404)

        ctx = self.contexts.get(body["ctx"])
        if ctx is None:
            return web.json_response(
                {"error": f"Unknown context: {body['ctx']}"}, status=404
            )

        ctx.args = body.get("args", [])
        ctx.kwargs = body.get("kwargs", {})
        result = await command.invoke(ctx)
        return web.json_response({"text": str(result)})

    async def debug_bot(self, request: web.Request):
        """Return bot debug information."""
        return web.json_response({
            "id": str(self.bot.user.id) if self.bot.user else None,
            "name": str(self.bot.user) if self.bot.user else None,
            "guilds": len(self.bot.guilds),
            "cogs": list(self.bot.cogs.keys()),
        })

    async def live(self, request: web.Request):
        """Healthcheck."""
        return web.Response(text="OK")

    @commands.command(name="save-context")
    async def save_context(self, ctx: commands.Context, context_id: typing.Optional[str] = None):
        """Save a context since it is really hard to build one from scratch."""
        context_id = context_id or str(uuid.uuid1())
        self.contexts[context_id] = ctx
        await ctx.send(f"> Saved context as **{context_id}**")


def setup(bot: commands.Bot):
    bot.add_cog(API(bot))
