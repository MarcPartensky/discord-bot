#!/usr/bin/env python
"""HTTP web service to interact with the bot."""
__author__ = "Marc Partensky"

# from config.config import cluster, access, check
# from utils.check import check
# from utils import tools

import os
import typing
import uuid
import traceback
import discord
import aiofiles
import subprocess
import psycopg2
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
        self.bot.loop.create_task(self._start_server())
        self.contexts: typing.Dict[str, commands.Context] = {}

    async def _start_server(self):
        """Task to run the HTTP server."""
        await self.bot.wait_until_ready()
        await self.server.start()

    # async def checker(self, a, request):
    #     print(a)
    #     print(request)
    #     # return request.headers.get("authorization") == "password"
    #     return True

    async def fail_handler(self, request):
        return web.json_response(data={"message": "you are not authorized"}, status=401)

    async def split_file(self, file_path: str, chunk_size: int = 8 * 1024 * 1024):
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
                chunk_path = f"/tmp/{os.path.basename(file_path)}.part{part_number}"
                async with aiofiles.open(chunk_path, 'wb') as chunk_file:
                    await chunk_file.write(chunk)
                chunk_paths.append(chunk_path)
                part_number += 1
        return chunk_paths

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
        await self._send_file_in_chunks(channel, file_path, filename)

        # Optionally, delete the temp file after sending it
        os.remove(file_path)
        message = f"Uploaded {filename} channel: {channel_id}"
        print(message)
        return web.json_response({"message": message}, status=200)

    async def _send_file_in_chunks(self, channel: discord.TextChannel, file_path: str, filename: str):
        """Split file into chunks and send each chunk as a separate message."""
        print(f"splitting: {filename}")
        file_size = os.path.getsize(file_path)

        # If the file size is smaller than the max chunk size, send it directly
        if file_size <= MAX_CHUNK_SIZE:
            await channel.send(file=discord.File(file_path, filename=filename))
            return

        # Split file into chunks and send each chunk separately
        part_number = 1
        async with aiofiles.open(file_path, 'rb') as f:
            while file_size > 0:
                # Read a chunk of the file
                chunk_data = await f.read(min(MAX_CHUNK_SIZE, file_size))

                # Create a temporary file for this chunk
                chunk_filename = f"{filename}.part{part_number}"
                chunk_file_path = f"/tmp/{chunk_filename}"
                async with aiofiles.open(chunk_file_path, 'wb') as chunk_file:
                    await chunk_file.write(chunk_data)

                # Send the chunk as a message
                await channel.send(file=discord.File(chunk_file_path, filename=chunk_filename))
                print(f"sent: {chunk_filename}")

                # Delete the chunk after sending
                os.remove(chunk_file_path)

                # Move to the next part
                file_size -= len(chunk_data)
                part_number += 1

    @server.add_route(path="/retrieve/file", method="POST", cog="API")
    async def retrieve_file_from_channel(self, request: web.Request):
        """
        Endpoint to retrieve, reassemble, and download the original file from a channel
        based on its name and the channel ID.
        """
        # Extract the JSON data from the request
        body = await request.json()

        # Extract the required information: channel ID and original filename
        channel_id = body.get("channel_id")
        original_filename = body.get("filename")

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

        # Iterate through the channel's message history to find the file chunks
        async for message in channel.history(limit=1000):  # Adjust limit as needed
            for attachment in message.attachments:
                print(f"attachement found: {attachment.filename}")
                if original_filename in attachment.filename and ".part" in attachment.filename:
                    # Download the part of the file
                    chunk_path = f"/tmp/{attachment.filename}"
                    await attachment.save(chunk_path)
                    file_chunks.append(chunk_path)

        if not file_chunks:
            return web.json_response({"error": "No file chunks found in the channel."}, status=404)

        # Sort the chunks by part number
        file_chunks.sort(key=lambda x: int(x.split(".part")[-1]))

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
        headers = {
            'Content-Disposition': f'attachment; filename="{original_filename}"'
        }
        return web.FileResponse(reassembled_file_path, headers=headers)

    # def build_context(self, channel: discord.TextChannel, args: list) -> commands.Context:
    #     """Build a fake context to run bot commands."""
    #     # state = discord
    #     data = {}
    #     state = discord.message.ConnectionState({}, {}, {}, http, loop)
    #     message = discord.Message(state, channel, data)
    #     view = discord.channel.TextChannel
    #     return commands.Context(message, self.bot, view, args=args))

    @server.add_route(path="/backup", method="POST", cog="API")
    async def backup_postgres(self, request: web.Request):
        """
        Endpoint to create a backup (dump) of a PostgreSQL database
        and return the dump file as a downloadable response.
        """
        body = await request.json()
        db_name = body.get("db_name")

        if not db_name:
            return web.json_response({"error": "Database name is missing"}, status=400)

        # Get PostgreSQL credentials from environment variables
        pg_user = os.getenv("POSTGRES_USER")
        pg_password = os.getenv("POSTGRES_PASSWORD")
        pg_host = os.getenv("POSTGRES_HOST", "localhost")
        pg_port = os.getenv("POSTGRES_PORT", "5432")

        if not pg_user or not pg_password:
            return web.json_response({"error": "PostgreSQL credentials are missing"}, status=500)

        # Construct the dump file path (stored temporarily)
        dump_file_path = f"/tmp/{db_name}_backup.sql"

        # Set up environment variables for `pg_dump` command
        env = os.environ.copy()
        env["PGPASSWORD"] = pg_password  # Set the password for `pg_dump`

        # Command to run the PostgreSQL dump
        pg_dump_command = [
            "pg_dump",
            "--dbname", f"postgresql://{pg_user}@{pg_host}:{pg_port}/{db_name}",
            "--file", dump_file_path
        ]

        try:
            # Execute the pg_dump command
            result = subprocess.run(pg_dump_command, env=env, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            return web.json_response({"error": "Backup failed", "details": e.stderr.decode()}, status=500)

        await self._send_file_in_chunks(channel, file_path, filename)

        # Serve the dump file as a download response
        headers = {
            'Content-Disposition': f'attachment; filename="{db_name}_backup.sql"'
        }
        return web.FileResponse(dump_file_path, headers=headers)

    @server.add_route(path="/backup/all", method="GET", cog="API")
    async def backup_all_postgres(self, request: web.Request):
        """
        Endpoint to create a backup (dump) of all PostgreSQL databases
        and return the dump file as a downloadable response.
        """
        # Get PostgreSQL credentials from environment variables

        pg_user = os.getenv("POSTGRES_USER")
        pg_password = os.getenv("POSTGRES_PASSWORD")
        pg_host = os.getenv("POSTGRES_HOST", "localhost")
        pg_port = os.getenv("POSTGRES_PORT", "5432")

        if not pg_user or not pg_password:
            return web.json_response({"error": "PostgreSQL credentials are missing"}, status=500)

        # Construct the dump file path (stored temporarily)
        dump_file_path = "/tmp/dumpall.sql"

        # Set up environment variables for `pg_dumpall` command
        env = os.environ.copy()
        env["PGPASSWORD"] = pg_password  # Set the password for `pg_dumpall`

        # Command to run the PostgreSQL dumpall
        pg_dumpall_command = [
            "pg_dumpall",
            "--username", pg_user,
            "--host", pg_host,
            "--port", pg_port,
            "--file", dump_file_path
        ]
        command = ' '.join(pg_dumpall_command)
        print(f"running: {command}")

        try:
            # Execute the pg_dumpall command
            result = subprocess.run(pg_dumpall_command, env=env, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            return web.json_response({"error": "Backup failed", "details": e.stderr.decode()}, status=500)


        # Serve the dump file as a download response
        headers = {
            'Content-Disposition': 'attachment; filename="dumpall.sql"'
        }

        return web.FileResponse(dump_file_path, headers=headers)

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
    # @server.check(predicate=checker, fail_handler="fail_handler")
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
    bot.add_cog(API(bot))
