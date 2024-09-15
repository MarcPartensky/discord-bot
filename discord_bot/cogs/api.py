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
import discord
import aiofiles
from discord.ext import commands

import server
from aiohttp import web

MAX_CHUNK_SIZE = 8 * 1024 * 1024  # 8 MB

class API(commands.Cog):
    """HTTP web service to interact with the bot."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.server = server.HTTPServer(
            bot=self.bot,
            host=os.environ.get("DISCORD_BOT_HOST") or "localhost",
            port=int(os.environ.get("DISCORD_BOT_PORT") or "8000"),
        )
        self.guild_id = int(os.environ.get(
            "DISCORD_BOT_GUILD_ID"
        ) or "550332212340326428")
        self.contexts: typing.Dict[str, commands.Context] = {}
        self.channel_id = int(os.environ["CHANNEL_ID_NOTIF"])
        self.bot.loop.create_task(self._start_server())

    async def _start_server(self):
        """Task to run the HTTP server."""
        await self.bot.wait_until_ready()
        await self.server.start()

    @server.add_route(path="/send/user", method="POST", cog="API")
    async def send_user(self, request: web.Request):
        """API home path."""
        body = await request.json()
        user: discord.User = await self.bot.fetch_user(body["id"])
        await user.send(body["message"])
        return web.json_response(
            data={"text": "Successfully sent message."}, status=200
        )

    @server.add_route(path="/send/channel", method="POST", cog="API")
    async def send_channel(self, request: web.Request):
        """API home path."""
        body = await request.json()
        channel: discord.TextChannel = await self.bot.fetch_channel(body["id"])
        await channel.send(body["message"])
        self.bot.commands
        return web.json_response(
            data={"text": "Successfully sent message."}, status=200
        )

    @server.add_route(path="/command/channel", method="POST", cog="API")
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

    @server.add_route(path="/debug/bot", method="GET", cog="API")
    async def debug_bot(self, request: web.Request):
        """API home path."""
        body = await request.json()
        return web.json_response(data=self.bot, status=200)

    @server.add_route(path="/live", method="GET", cog="API")
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


async def setup(bot: commands.Bot):
    await bot.add_cog(API(bot))
