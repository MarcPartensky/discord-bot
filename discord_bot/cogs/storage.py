#!/usr/bin/env python
"""HTTP web service to interact with the bot."""
__author__ = "Marc Partensky"

# from config.config import cluster, access, check
# from utils.check import check
# from utils import tools

import os, time, subprocess
import discord
import aiofiles
# from discord.errors import NotFound
from discord.ext.commands import MessageNotFound
from discord.ext import commands

import server
from aiohttp import web

MAX_CHUNK_SIZE = 8 * 1024 * 1024  # 8 MB

class Storage(commands.Cog):
    """Store files on discord using HTTP web service to interact with the bot."""
    tmp_directory = os.environ.get("TMP_DIRECTORY") or "/tmp"

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.channel_id = int(os.environ["CHANNEL_ID_NOTIF"])
        self.password = "password"
        # self.tmp_directory = "/tmp"

    def get_timestamp(self):
        """Return a human readable timestamp."""
        current_time = time.localtime()
        milliseconds = int((time.time() % 1) * 1000)
        timestamp = time.strftime(f"%Y-%m-%d_%H-%M-%S_{milliseconds:03d}", current_time)
        return timestamp

    def sign(self, filepath: str) -> str:
        """Sign a file using its file path and return the signed file path."""
        signed_filepath = f"{filepath}.sig"
        cmd = f"gpg --output {signed_filepath} --sign {filepath}"
        subprocess.run(cmd.split(" "))
        return signed_filepath

    def encrypt_and_compress(self, filepath: str) -> str:
        """Encrypt and compress a file using its file path
        and return the encrypted and compressed file path."""
        compressed_filepath = f"{filepath}.7z"
        cmd = f"7z a -p{self.password} {compressed_filepath} {filepath}"
        subprocess.run(cmd.split(" "))
        return compressed_filepath

    def compress(self, filepath: str) -> str:
        """Compress a file using its file path and return the compressed file path."""
        compressed_filepath = f"{filepath}.7z"
        cmd = f"7z -y a {compressed_filepath} {filepath}"
        subprocess.run(cmd.split(" "))
        return  compressed_filepath

    async def split_file(self, filepath: str, chunk_size: int = MAX_CHUNK_SIZE):
        """
        Split a file into chunks of specified size.
        """
        chunk_paths = []
        filepath = self.encrypt_and_compress(filepath)
        # filepath = self.sign(filepath)
        with open(filepath, 'rb') as file:
            part_number = 1
            while True:
                chunk = file.read(chunk_size)
                if not chunk:
                    break
                tmp = self.get_timestamp()
                chunk_path = f"{Storage.tmp_directory}/{os.path.basename(filepath)}.{tmp}.{part_number}"
                async with aiofiles.open(chunk_path, 'wb') as chunk_file:
                    await chunk_file.write(chunk)
                chunk_paths.append(chunk_path)
                part_number += 1
        return chunk_paths

    async def send_file_in_chunks(self, filepath: str, file_name: str, channel_id: int = 0, timestamp: str=""):
        """
        Send a file to Discord in chunks using filepath, file_name and optional channel_id.
        """
        channel_id = channel_id or self.channel_id
        chunk_paths = await self.split_file(filepath)

        channel = self.bot.get_channel(int(channel_id))
        if not channel:
            raise ValueError("Discord channel not found")

        if not timestamp:
            timestamp = self.get_timestamp()
        
        for i, chunk_path in enumerate(chunk_paths, start=1):
            chunk_file_name = f"{file_name}.{timestamp}.{i}"
            with open(chunk_path, 'rb') as f:
                await channel.send(file=discord.File(f, filename=chunk_file_name))
        
        return chunk_paths

    async def clean_files(self, filepaths: list):
        """Remove the specified files."""
        for filepath in filepaths:
            os.remove(filepath)

    def generate_url(self, filename: str, channel_id: int, timestamp: str):
        """Generate an url to retrieve a file already sent."""
        PUBLIC_API_URL = os.environ["PUBLIC_API_URL"]
        return f"{PUBLIC_API_URL}/retrieve?filename={filename}&channel_id={channel_id}&timestamp={timestamp}"

    @server.add_route(path="/send", method="POST", cog="API")
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
            filepath = f"{Storage.tmp_directory}/{filename}"

            # Save the file temporarily
            async with aiofiles.open(filepath, 'wb') as f:
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

        # await channel.send(file=discord.File(filepath))
        storage = Storage(self.bot)
        timestamp = storage.get_timestamp()
        await storage.send_file_in_chunks(filepath, filename, channel_id, timestamp)
        url = storage.generate_url(filename, channel_id, timestamp)

        # Optionally, delete the temp file after sending it
        os.remove(filepath)
        message = f"Uploaded {filename}"
        print(message)
        print(url)
        return web.json_response({"message": message, "url": url}, status=200)


    @server.add_route(path="/retrieve", method="GET", cog="API")
    async def retrieve_file_from_channel_request(self, request: web.Request):
        """
        Endpoint to retrieve, reassemble, and download the original file from a channel
        based on its filename, the timestamp and potentially channel_id.
        """
        # Extract the JSON data from the request
        body = request.query

        # Extract the required information: channel ID and original filename
        channel_id = body.get("channel_id") or self.channel_id
        filename = body.get("filename")
        timestamp = body.get("timestamp")
        limit = body.get("limit")
        print('body:', body)
        print("channel_id:", channel_id)
        print("filename:", filename)
        print("timestamp:", timestamp)
        print("limit:", limit)

        if not channel_id:
            return web.json_response({"error": "channel_id missing"}, status=400)
        if not filename:
            return web.json_response({"error": "filename missing"}, status=400)
        if limit:
            try:
                limit = int(limit)
            except:
                return web.json_response({"error": "limit is not a number"}, status=400)

        channel: discord.TextChannel = await self.bot.fetch_channel(channel_id)
        if not channel:
            return web.json_response({"error": "channel not found"}, status=404)
        print("channel:", channel)

        try:
            reassembled_filepath = await Storage(self.bot).retrieve_file_from_channel(
                filename,
                channel,
                timestamp,
                limit
            )
            headers = {'Content-Disposition': f'attachment; filename="{filename}"'}
            return web.FileResponse(reassembled_filepath, headers=headers)
        except MessageNotFound as e:
            return web.json_response({"error": str(e)}, status=404)


    async def retrieve_file_from_channel(
        self,
        filename: str,
        channel: discord.TextChannel,
        timestamp: str,
        limit: int = 1000,
    ):
        """Retrieve a file from a channel using:
            - filename
            - channel
            - timestamp
            - limit [1000] (number of messages checked)
        """
        # Prepare the path to save the reassembled file
        reassembled_filepath = f"{Storage.tmp_directory}/{filename}"
        print("reassembled_filepath:", reassembled_filepath)

        # Initialize list to collect all file chunks
        file_chunks = []

        stop = False
        found = False

        def is_well_formed(dfilename: str):
            if not dfilename.startswith(filename):
                return False
            dextension = dfilename[len(filename)+1:]
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
            dextension = dfilename[len(filename)+1:]
            dtimestamp, dpart = dextension.split(".")
            return dextension, dtimestamp, dpart


        # Iterate through the channel's message history to find the file chunks
        i = 0
        async for message in channel.history(limit=limit, oldest_first=False):  # Adjust limit as needed
            i+=1
            if i%100==0: print(i, "messages")
            if stop and found: break
            for attachment in message.attachments:
                print(f"attachement found: {attachment.filename}")
                dfilename = attachment.filename
                if not is_well_formed(dfilename):
                    # print(f"skip and delete {dfilename} because malformed")
                    await message.delete()
                    continue
                if dfilename.startswith(filename):
                    dextension = dfilename[len(filename)+1:]
                    # print(filename, dfilename, dextension)
                    if dextension.count(".") != 1:
                        break
                    dtimestamp, dpart = dextension.split(".")
                    # print("dfilename", dfilename)
                    # print("dextension", dextension)
                    # print("dtimestamp", dtimestamp)
                    # print("dpart", dpart)
                    # print("timestamp", timestamp)
                    if not timestamp:
                        timestamp = dtimestamp
                    if timestamp == dtimestamp:
                        # print("found", dtimestamp)
                        found = True
                    elif found:
                        # print("stop", timestamp, "!=", dtimestamp)
                        stop = True
                        break

                    chunk_path = f"{Storage.tmp_directory}/{dfilename}"
                    await attachment.save(chunk_path)
                    file_chunks.append(chunk_path)

        if not file_chunks:
            raise MessageNotFound("No file chunks found in the channel.")

        # Sort the chunks by part number
        print("sorting chunks", file_chunks)
        file_chunks.sort(key=lambda filepath: int(deconstruct(filepath)[-1]))

        # Reassemble the file
        async with aiofiles.open(reassembled_filepath, 'wb') as reassembled_file:
            for chunk_path in file_chunks:
                async with aiofiles.open(chunk_path, 'rb') as chunk_file:
                    data = await chunk_file.read()
                    await reassembled_file.write(data)

        # Optionally clean up the chunk files after reassembly
        for chunk_path in file_chunks:
            os.remove(chunk_path)

        # Serve the reassembled file as a download response
        return reassembled_filepath

async def setup(bot: commands.Bot):
    await bot.add_cog(Storage(bot))
