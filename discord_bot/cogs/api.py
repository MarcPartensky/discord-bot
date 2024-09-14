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
        self.guild_id = int(
            os.environ.get("DISCORD_BOT_GUILD_ID") or "550332212340326428"
        )
        # self.bot.loop.create_task(self._start_server())
        self.contexts: typing.Dict[str, commands.Context] = {}
        self.channel_id = int(os.environ["CHANNEL_ID_NOTIF"])
        self.bot.loop.create_task(self._start_server())
        # self.scheduler = AsyncIOScheduler()  # Le scheduler APScheduler
        # self.scheduler.start()  # Démarrer le scheduler
        # self.setup_jobs()  # Configurer les jobs récurrents

    def get_timestamp(self):
        current_time = time.localtime()
        milliseconds = int((time.time() % 1) * 1000)
        timestamp = time.strftime(f"%Y-%m-%d_%H-%M-%S_{milliseconds:03d}", current_time)
        return timestamp

    async def _start_server(self):
        """Task to run the HTTP server."""
        await self.bot.wait_until_ready()
        print(f"listening on http://{self.server.host}:{self.server.port}")
        await self.server.start()

    async def split_file(self, file_path: str, chunk_size: int = MAX_CHUNK_SIZE):
        """
        Split a file into chunks of specified size.
        """
        chunk_paths = []
        with open(file_path, 'rb') as file:
            part_number = 1
            while True:
                chunk = file.read(chunk_size)
                if not chunk:
                    break
                tmp = self.get_timestamp()
                chunk_path = f"/tmp/{os.path.basename(file_path)}.{tmp}.{part_number}"
                async with aiofiles.open(chunk_path, 'wb') as chunk_file:
                    await chunk_file.write(chunk)
                chunk_paths.append(chunk_path)
                part_number += 1
        return chunk_paths

    async def send_file_in_chunks(self, file_path: str, file_name: str, channel_id: int = 0):
        """
        Send a file to Discord in chunks.
        """
        channel_id = channel_id or self.channel_id
        chunk_paths = await self.split_file(file_path)

        channel = self.bot.get_channel(int(channel_id))
        if not channel:
            raise ValueError("Discord channel not found")

        tmp = self.get_timestamp()
        
        for i, chunk_path in enumerate(chunk_paths, start=1):
            chunk_file_name = f"{file_name}.{tmp}.{i}"
            with open(chunk_path, 'rb') as f:
                await channel.send(file=discord.File(f, filename=chunk_file_name))
        
        return chunk_paths

    async def clean_files(self, file_paths: list):
        """Remove the specified files."""
        for file_path in file_paths:
            os.remove(file_path)


    # def setup_jobs(self):
    #     """Configurer les jobs récurrents avec APScheduler."""
    #     # Planifier le job quotidien à 5h du matin
    #     self.scheduler.add_job(
    #         self.daily_backup,  # La fonction à exécuter
    #         CronTrigger(hour=5, minute=0),  # CronTrigger à 5h00 chaque jour
    #         name="daily_backup_job",  # Nom du job
    #         replace_existing=True  # Remplacer si le job existe déjà
    #     )
    #     logging.info("Job de backup quotidien à 5h du matin configuré.")



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

    @server.add_route(path="/send/file", method="POST", cog="API")
    async def send_file_to_channel(self, request: web.Request):
        """Endpoint to send a file to a specific channel by ID."""
        filename: str
        channel_id: int

        reader = await request.multipart()
        field = await reader.next()
        if field.name == "channel_id":
            channel_id = await field.text()
        else:
            return web.json_response({"error": "Channel ID missing"}, status=400)


        field = await reader.next()
        if field.name == "file":
            filename = field.filename
            file_path = f"/tmp/{filename}"

            # Save the file temporarily
            async with aiofiles.open(file_path, 'wb') as f:
                while True:
                    chunk = await field.read_chunk()  # 8192 bytes by default
                    if not chunk:
                        break
                    await f.write(chunk)
        else:
            return web.json_response({"error": "File missing"}, status=400)

        channel: discord.TextChannel = await self.bot.fetch_channel(channel_id)
        if not channel:
            return web.json_response({"error": "Channel not found"}, status=404)

        # await channel.send(file=discord.File(file_path))
        await self.send_file_in_chunks(file_path, filename, channel_id)

        # Optionally, delete the temp file after sending it
        os.remove(file_path)
        message = f"Uploaded {filename} channel: {channel_id}"
        print(message)
        return web.json_response({"message": message}, status=200)


    @server.add_route(path="/retrieve/file", method="POST", cog="API")
    async def retrieve_file_from_channel(self, request: web.Request):
        """
        Endpoint to retrieve, reassemble, and download the original file from a channel
        based on its name and the channel ID.
        """
        # Extract the JSON data from the request
        body = await request.json()

        # Extract the required information: channel ID and original filename
        channel_id = body.get("channel_id") or self.channel_id
        original_filename = body.get("filename")
        chosen_timestamp = body.get("timestamp")
        print('timestamp:', chosen_timestamp)

        if not channel_id or not original_filename:
            return web.json_response({"error": "Channel ID or filename missing"}, status=400)

        # Fetch the Discord channel
        channel: discord.TextChannel = await self.bot.fetch_channel(channel_id)
        if not channel:
            return web.json_response({"error": "Channel not found"}, status=404)

        # Prepare the path to save the reassembled file
        reassembled_file_path = f"/tmp/{original_filename}"

        # Initialize list to collect all file chunks
        file_chunks = []

        stop = False
        found = False

        def is_well_formed(dfilename: str):
            if not dfilename.startswith(original_filename):
                return False
            dextension = dfilename[len(original_filename)+1:]
            if dextension.count(".") != 1:
                return False
            dtimestamp, dpart = dextension.split(".")
            # print(f"dtimestamp: {dtimestamp}, {len(dtimestamp)}")
            # print(f"dpart: {dpart}")
            if len(dtimestamp) != 23:
                return False
            if not dpart:
                return False
            # print("passed:", dfilename)
            return True

        def deconstruct(dfilepath: str):
            dfilename = dfilepath.split('/')[-1]
            dextension = dfilename[len(original_filename)+1:]
            dtimestamp, dpart = dextension.split(".")
            return dextension, dtimestamp, dpart


        # Iterate through the channel's message history to find the file chunks
        async for message in channel.history(limit=1000):  # Adjust limit as needed
            if stop and found: break
            for attachment in message.attachments:
                print(f"attachement found: {attachment.filename}")
                dfilename = attachment.filename
                if not is_well_formed(dfilename):
                    # print(f"skip and delete {dfilename} because malformed")
                    await message.delete()
                    continue
                if dfilename.startswith(original_filename):
                    dextension = dfilename[len(original_filename)+1:]
                    if dextension.count(".") != 1:
                        break
                    dtimestamp, dpart = dextension.split(".")
                    # print("dfilename", dfilename)
                    # print("dextension", dextension)
                    # print("dtimestamp", dtimestamp)
                    # print("dpart", dpart)
                    # print("chosen_timestamp", chosen_timestamp)
                    if not chosen_timestamp:
                        chosen_timestamp = dtimestamp
                    if chosen_timestamp == dtimestamp:
                        # print("found", dtimestamp)
                        found = True
                    elif found:
                            # print("stop", chosen_timestamp, "!=", dtimestamp)
                            stop = True
                            break

                    chunk_path = f"/tmp/{dfilename}"
                    await attachment.save(chunk_path)
                    file_chunks.append(chunk_path)

        if not file_chunks:
            return web.json_response({"error": "No file chunks found in the channel."}, status=404)

        # Sort the chunks by part number
        print("sorting chunks", file_chunks)
        file_chunks.sort(key=lambda filepath: int(deconstruct(filepath)[-1]))

        # Reassemble the file
        async with aiofiles.open(reassembled_file_path, 'wb') as reassembled_file:
            for chunk_path in file_chunks:
                async with aiofiles.open(chunk_path, 'rb') as chunk_file:
                    data = await chunk_file.read()
                    await reassembled_file.write(data)

        # Optionally clean up the chunk files after reassembly
        for chunk_path in file_chunks:
            os.remove(chunk_path)

        # Serve the reassembled file as a download response
        headers = {'Content-Disposition': f'attachment; filename="{original_filename}"'}
        return web.FileResponse(reassembled_file_path, headers=headers)

    # def build_context(self, channel: discord.TextChannel, args: list) -> commands.Context:
    #     """Build a fake context to run bot commands."""
    #     # state = discord
    #     data = {}
    #     state = discord.message.ConnectionState({}, {}, {}, http, loop)
    #     message = discord.Message(state, channel, data)
    #     view = discord.channel.TextChannel
    #     return commands.Context(message, self.bot, view, args=args))



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
    print("setup api")
    await bot.add_cog(API(bot))
