#!/bin/env python

# from config.config import masters, access, check
# from config import shops
# from utils import tools

from config.config import access, cluster
from discord.ext import commands

import discord
import os
import psycopg2


class Backup(commands.Cog):
    def __init__(self, bot):
        """Setup postgres logins"""
        self.bot = bot
        self.host = os.environ.get("POSTGRES_HOST")
        self.port = os.environ.get("POSTGRES_PORT")
        self.database = os.environ.get("POSTGRES_DATABASE")
        self.user = os.environ.get("POSTGRES_USER")
        self.password = os.environ.get("POSTGRES_PASSWORD")
        self.color = 0x0064a5
        self.connection: psycopg2.connection
        self.cursor: psycopg2.cursor


    @commands.command(name="postgres-connect")
    @access.admin
    async def connect_postgres(self, ctx: commands.Context):
        """Change les identifiants postgres avec un string user,password,database,host,port."""
        self.connection = psycopg2.connect(
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.database
        )
        self.cursor = self.connection.cursor()
        await ctx.send("Connected to the database")

    @commands.command(name="postgres-set")
    @access.admin
    async def set_postgres_logins(self, ctx: commands.Context, connection: str):
        """Change les identifiants postgres avec un string user,password,database,host,port."""

        try:
            self.user, self.password, self.database, self.host, self.port = connection.split(",")
        except:
            return await ctx.send("> Le format doit être le suivant: user,password,database,host,port")
        embed = discord.Embed(
            title="PostgreSQL logins", color=discord.Color(self.color)
        )
        embed.add_field(name="user", value=self.user)
        embed.add_field(name="password", value=self.password)
        embed.add_field(name="database", value=self.database)
        embed.add_field(name="host", value=self.host)
        embed.add_field(name="port", value=self.port)

        await ctx.send(embed=embed)

    @commands.command(name="postgres")
    @access.admin
    async def get_postgres_logins(self, ctx: commands.Context):
        """Affiche les identifiants postgres uniquement si master"""
        embed = discord.Embed(
            title="PostgreSQL Logins", color=discord.Color(self.color)
        )
        embed.add_field(name="user", value=self.user)
        embed.add_field(name="password", value=self.password)
        embed.add_field(name="database", value=self.database)
        embed.add_field(name="host", value=self.host)
        embed.add_field(name="port", value=self.port)

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Backup(bot))
