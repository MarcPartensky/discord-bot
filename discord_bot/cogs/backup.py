#!/bin/env python

# from config.config import masters, access, check
# from config import shops
# from utils import tools

from config.config import access, cluster
from discord.ext import commands, tasks

import discord
import os
import logging

import psycopg2, subprocess
import aiofiles

SECONDS = 3600

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
        self.backup_filename = 'backup.sql'
        self.connection: psycopg2.connection
        self.cursor: psycopg2.cursor
        self.backup_job.start()
        # self.scheduler = AsyncIOScheduler()  # Le scheduler APScheduler
        # self.scheduler.start()  # Démarrer le scheduler
        # self.setup_jobs()  # Configurer les jobs récurrents

    @property
    def storage(self):
        return self.bot.get_cog("Storage")

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
        
    async def _execute_pg_command(self, command: list, dump_file_path: str, env: dict):
        """
        Execute a PostgreSQL dump command.
        """
        try:
            _ = subprocess.run(command + ["--file", dump_file_path], env=env, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Backup failed: {e.stderr.decode()}")

    async def _backup_postgres(self, *db_names: str) -> str:
        """
        Backup specified PostgreSQL databases or all databases if no arguments are provided.
        Concatenate the backups into a single file if multiple databases are specified.
        """
        if not self.user or not self.password:
            raise RuntimeError("PostgreSQL credentials are missing")

        env = os.environ.copy()
        env["PGPASSWORD"] = self.password

        filename = self.backup_filename

        if db_names:
            # Création d'un fichier de dump unique pour plusieurs bases
            dump_file_path = f"/tmp/{filename}"
            
            # Ouvre le fichier pour concaténer les résultats des dumps
            async with aiofiles.open(dump_file_path, 'w') as dump_file:
                for db_name in db_names:
                    pg_dump_command = [
                        "pg_dump",
                        "--username", self.user,
                        "--host", self.host,
                        "--port", self.port,
                        "--dbname", f"postgresql://{self.user}@{self.host}:{self.port}/{self.database}"
                    ]
                    
                    try:
                        # Exécute pg_dump et capture la sortie
                        result = subprocess.run(pg_dump_command, env=env, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        await dump_file.write(result.stdout.decode())  # Ajoute le dump au fichier
                    except subprocess.CalledProcessError as e:
                        raise RuntimeError(f"Backup failed for {db_name}: {e.stderr.decode()}")
            
        else:
            # Si aucune base de données spécifiée, on sauvegarde toutes les bases
            dump_file_path = f"/tmp/{filename}"
            pg_dumpall_command = [
                "pg_dumpall",
                "--username", self.user,
                "--host", self.host,
                "--port", self.port
            ]
            
            try:
                await self._execute_pg_command(pg_dumpall_command, dump_file_path, env)
            except Exception as e:
                raise RuntimeError(f"Backup all databases failed: {str(e)}")

        chunks = await self.storage.send_file_in_chunks(dump_file_path, filename)
        await self.storage.clean_files(chunks)
        os.remove(dump_file_path)
            
        return dump_file_path

    @tasks.loop(seconds=SECONDS)
    async def backup_job(self):
        """La tâche qui sera exécutée tous les jours à 5h."""
        try:
            # Effectuer un backup de toutes les bases
            dump_file_paths = await self._backup_postgres()
            logging.info(f"Backup quotidien réussi : {dump_file_paths}")
        except Exception as e:
            logging.error(f"Erreur lors du backup quotidien : {e}")

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
        embed.add_field(name="user", value=str(self.user))
        embed.add_field(name="password", value=str(self.password))
        embed.add_field(name="database", value=str(self.database))
        embed.add_field(name="host", value=str(self.host))
        embed.add_field(name="port", value=str(self.port))

        await ctx.send(embed=embed)


    @commands.command(name="backup")
    async def backup_postgres_command(self, ctx: commands.Context, *db_names: str):
        """
        Commande Discord pour créer une sauvegarde (dump) de bases de données PostgreSQL spécifiques
        ou de toutes les bases de données si aucun nom n'est fourni.
        """
        try:
            await self._backup_postgres(*db_names)
        except Exception as e:
            await ctx.send(f"Erreur: {str(e)}")

async def setup(bot):
    await bot.add_cog(Backup(bot))