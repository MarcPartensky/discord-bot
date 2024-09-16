#!/bin/env python

# from config.config import masters, access, check
# from config import shops
# from utils import tools

from config.config import access, cluster
from discord.ext import commands, tasks

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

import discord
import os
import logging

import psycopg2, subprocess
import aiofiles

SECONDS = 3600
ROLE = "Backup"

class Backup(commands.Cog):
    def __init__(self, bot):
        """Setup postgres logins"""
        self.bot = bot
        self.host = os.environ.get("POSTGRES_HOST")
        self.port = os.environ.get("POSTGRES_PORT")
        self.database = os.environ.get("POSTGRES_DATABASE")
        self.user = os.environ.get("POSTGRES_USER")
        self.password = os.environ.get("POSTGRES_PASSWORD")
        self.backup_filename = os.environ.get("POSTGRES_DUMP_FILENAME") or "backup.sql"
        self.channel_id = int(os.environ.get("BACKUP_CHANNEL_ID") or 0)
        self.default_cron_expression = os.environ.get("BACKUP_DEFAULT_CRON_EXPRESSION") or "0 5 * * *"
        self.default_jobname = os.environ.get("BACKUP_DEFAULT_JOBNAME") or "daily"
        self.jobs = {}
        self.tmp_directory = "/tmp"
        self.color = 0x0064a5

        self.scheduler = AsyncIOScheduler()  # Le scheduler APScheduler
        self.scheduler.start()  # Démarrer le scheduler
        self.setup_default_backup()

        # self.connection: psycopg2.connection
        # self.cursor: psycopg2.cursor
        # self.backup_job.start()

    def setup_default_backup(self):
        """Ajoute un job par défaut tous les jours à 5h du matin.""" 
        job_name = self.default_jobname
        cron_expression = self.default_cron_expression
        trigger = CronTrigger.from_crontab(cron_expression)
        job = self.scheduler.add_job(self._backup_postgres, trigger, name=job_name)
        self.jobs[job_name] = job
        logging.info("Job de backup quotidien à 5h du matin ajouté.")

    @property
    def storage(self):
        return self.bot.get_cog("Storage")

    # def setup_jobs(self):
    #     """Configurer les jobs récurrents avec APScheduler."""
    #     # Planifier le job quotidien à 5h du matin
    #     self.scheduler.add_job(
    #         self._backup_postgres,  # La fonction à exécuter
    #         CronTrigger(hour=5, minute=0),  # CronTrigger à 5h00 chaque jour
    #         name="backup",  # Nom du job
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
            dump_file_path = f"{self.tmp_directory}/{filename}"
            
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
            dump_file_path = f"{self.tmp_directory}/{filename}"
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

        chunks = await self.storage.send_file_in_chunks(dump_file_path, filename, channel_id=self.channel_id)
        await self.storage.clean_files(chunks)
        os.remove(dump_file_path)
            
        return dump_file_path

    # @tasks.loop(seconds=SECONDS)
    # async def backup_job(self):
    #     """La tâche qui sera exécutée tous les jours à 5h."""
    #     try:
    #         # Effectuer un backup de toutes les bases
    #         dump_file_paths = await self._backup_postgres()
    #         logging.info(f"Backup quotidien réussi : {dump_file_paths}")
    #     except Exception as e:
    #         logging.error(f"Erreur lors du backup quotidien : {e}")

    def build_embed(self):
        """Return the embed that contains all the infos of the backup cog."""
        embed = discord.Embed(
            title="PostgreSQL Logins", color=discord.Color(self.color)
        )
        embed.add_field(name="user", value=str(self.user))
        embed.add_field(name="password", value="*"*len(str(self.password)))
        embed.add_field(name="database", value=str(self.database))
        embed.add_field(name="host", value=str(self.host))
        embed.add_field(name="port", value=str(self.port))
        embed.add_field(name="channel", value=str(self.channel_id))
        return embed


    @commands.group(aliases=["bk"])
    async def backup(self, ctx: commands.Context):
        """Groupe de commandes du cog 'Backup'."""
        if not ctx.invoked_subcommand:
            await self.backup_dump(ctx)
            # await ctx.send("> No command invoked")

    @backup.group(name="role")
    @commands.is_owner() 
    async def role(self, ctx: commands.Context):
        """Groupe de commandes pour controller le role 'Backup'."""
        if not ctx.invoked_subcommand:
            await ctx.send("> Aucune sous-commande invoquée.")

    @role.command(name="create")
    async def create_backup_role(self, ctx: commands.Context):
        """Crée un rôle nommé 'Backup' si l'utilisateur est le propriétaire du bot."""
        guild = ctx.guild  # Obtenir le serveur actuel
        role_name = ROLE

        # Vérifier si le rôle existe déjà
        existing_role = discord.utils.get(guild.roles, name=role_name)
        if existing_role:
            await ctx.send(f"> Le rôle `{role_name}` existe déjà.")
            return
        try:
            # Créer le nouveau rôle
            existing_role = await guild.create_role(name=role_name, color=self.color)
            await ctx.author.add_roles(existing_role)
            await ctx.send(f"> Le rôle `{role_name}` a été créé et ajouté à **{ctx.author}** avec succès.")
        except discord.Forbidden:
            await ctx.send("> Je n'ai pas la permission de créer des rôles.")
        except discord.HTTPException as e:
            await ctx.send(f"> Une erreur est survenue : {e}")

    @role.command(name="delete")
    async def delete_backup_role(self, ctx: commands.Context):
        """Supprime le rôle nommé 'Backup'."""
        role_name = ROLE

        # Vérifier si le rôle existe
        existing_role = discord.utils.get(ctx.guild.roles, name=role_name)
        if not existing_role:
            await ctx.send(f"> Le rôle `{role_name}` n'existe pas.")
            return
        
        try:
            # Supprimer le rôle
            await existing_role.delete()
            await ctx.send(f"> Le rôle `{role_name}` a été supprimé avec succès.")
        except discord.Forbidden:
            await ctx.send("> Je n'ai pas la permission de supprimer des rôles.")
        except discord.HTTPException as e:
            await ctx.send(f"> Une erreur est survenue : {e}")

    @backup.group(name="job")
    @commands.has_role(ROLE)
    async def job(self, ctx: commands.Context):
        """Groupe de commandes pour gérer les jobs de backup."""
        if not ctx.invoked_subcommand:
            await ctx.send("> Aucune sous-commande invoquée.")

    @job.command(name="add")
    async def add_job(self, ctx: commands.Context, job_name: str, cron_expression: str):
        """Ajoute un job de backup avec un nom et une expression cron."""
        try:
            trigger = CronTrigger.from_crontab(cron_expression)
            job = self.scheduler.add_job(self._backup_postgres, trigger, name=job_name)
            self.jobs[job_name] = job
            await ctx.send(f"> Job `{job_name}` ajouté avec succès.")
            await ctx.send(embed=await self.build_job_embed())
        except Exception as e:
            await ctx.send(f"> Erreur lors de l'ajout du job : {e}")

    @job.command(name="list")
    async def list_jobs(self, ctx: commands.Context):
        """Liste tous les jobs de backup configurés."""
        if not self.jobs:
            await ctx.send("> Aucun job de backup configuré.")
            return

        # await ctx.send(f"> Jobs configurés :\n{job_list}")
        await ctx.send(embed=await self.build_job_embed())

    @job.command(name="delete")
    async def delete_job(self, ctx: commands.Context, job_name: str):
        """Supprime un job de backup par son nom."""
        job = self.jobs.pop(job_name, None)
        if job:
            job.remove()
            await ctx.send(f"> Job `{job_name}` supprimé avec succès.")
            await ctx.send(embed=await self.build_job_embed())
        else:
            await ctx.send("> Job non trouvé.")

    def get_cron_expression(self, trigger: CronTrigger) -> str:
        """Retourne une représentation de l'expression Cron sous forme de chaîne de caractères."""
        return str(trigger)

    async def build_job_embed(self) -> discord.Embed:
        """Affiche les jobs configurés."""
        embed = discord.Embed(
            title="Jobs de Backup Configurés",
            description="Liste de tous les jobs de sauvegarde actuellement configurés.",
            color=self.color
        )
        for job_name, job in self.jobs.items():
            embed.add_field(
                name=job_name,
                value=self.get_cron_expression(job.trigger),
                inline=True
            )
        return embed

    @backup.command(name="connect")
    @commands.has_role(ROLE)
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

    @backup.command(name="set")
    @commands.has_role(ROLE)
    async def set_backup(
        self,
        ctx: commands.Context,
        *,
        args: str = ""
    ):
        """
        Change les identifiants postgres avec une chaîne de format key=value.
        Exemple: ?backup set host=localhost user=postgres
        """
        # Analyse des arguments
        params = {}
        for pair in args.split():
            if '=' in pair:
                key, value = pair.split('=', 1)
                params[key.strip()] = value.strip()
        
        # Mise à jour des attributs
        if 'user' in params:
            self.user = params['user']
        if 'password' in params:
            self.password = params['password']
        if 'host' in params:
            self.host = params['host']
        if 'port' in params:
            self.port = params['port']
        if 'database' in params:
            self.database = params['database']
        if 'channel_id' in params:
            self.channel_id = int(params['channel_id'])
        
        embed = self.build_embed()
        await ctx.send(embed=embed)

    @backup.command(name="get")
    @commands.has_role(ROLE)
    async def get_postgres_logins(self, ctx: commands.Context):
        """Affiche les identifiants postgres uniquement si master"""
        embed = self.build_embed()
        await ctx.send(embed=embed)

    @backup.command(name="claim")
    @commands.has_role(ROLE)
    async def claim_channel(self, ctx: commands.Context):
        """Déclare le salon textuel qui fait office de stockage de backup."""
        self.channel_id = ctx.channel.id
        embed = self.build_embed()
        await ctx.send(embed=embed)

    @backup.command(name="dump")
    @commands.has_role(ROLE)
    async def backup_dump(self, ctx: commands.Context, *db_names: str):
        """
        Commande Discord pour créer une sauvegarde (dump) de bases de données PostgreSQL spécifiques
        ou de toutes les bases de données si aucun nom n'est fourni.
        """
        try:
            await self._backup_postgres(*db_names)
            await ctx.send("> Backup done")
        except Exception as e:
            await ctx.send(f"Erreur: {str(e)}")

async def setup(bot):
    await bot.add_cog(Backup(bot))
