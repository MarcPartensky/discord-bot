#!/usr/bin/env python
"""Pont vers un gateway Hermes Agent dedie (profil `discord-bridge`).

Reserve aux membres qui portent le role Discord `hermes` (nom configurable via
`HERMES_BRIDGE_ROLE_NAME`) et aux masters du bot. Parle a l'API server
OpenAI-compatible d'Hermes (services/hermes cote NixOS, loopback uniquement).

L'API server est un listener UNIQUE par hote : un profil secondaire n'a pas son
propre port, il est servi sur le listener du profil default sous /p/<profil>/...

Variables d'environnement (injectees par systemd, cf. services/discord-bot) :
    HERMES_BRIDGE_URL        defaut http://127.0.0.1:8642/p/discord-bridge/v1/chat/completions
    HERMES_BRIDGE_API_KEY    bearer token (sops secrets/discord-hermes-bridge.yml)
    HERMES_BRIDGE_ROLE_NAME  nom du role Discord autorise (defaut "hermes")
    HERMES_BRIDGE_ASK_PORT   port loopback de la surface de test (defaut 8052)
    DISCORD_BOT_API_TOKEN    si pose, exige en Bearer (convention de cogs/api.py)
"""

import asyncio
import os
import typing

import discord
import requests
from aiohttp import web
from discord.ext import commands

from config.config import prefix, masters
from utils.tools import create_role_if_missing

DEFAULT_BRIDGE_URL = "http://127.0.0.1:8642/p/discord-bridge/v1/chat/completions"

BRIDGE_URL = os.environ.get("HERMES_BRIDGE_URL", DEFAULT_BRIDGE_URL)
BRIDGE_KEY = os.environ.get("HERMES_BRIDGE_API_KEY")
ROLE_NAME = os.environ.get("HERMES_BRIDGE_ROLE_NAME", "hermes")
MAX_HISTORY = 20  # messages (user + assistant) gardes par utilisateur
REQUEST_TIMEOUT = 120

SYSTEM_PROMPT = (
    "Tu es Hermes, relaye ici depuis Discord (pont dedie, profil discord-bridge). "
    "Reponds de facon concise, adaptee au format Discord (2000 caracteres max par "
    "message), sans mise en forme lourde."
)


class Hermes(commands.Cog):
    """Bridge to a dedicated Hermes Agent gateway (OpenAI-compatible API)."""

    def __init__(self, bot: commands.Bot):
        """Initialize the cog with the bot."""
        self.bot = bot
        self.color: discord.Color = discord.Color.blurple()
        self.histories: typing.Dict[int, list] = {}

        # Surface de test locale (loopback) : joindre Hermes par HTTP sans client
        # Discord, et LIRE sa reponse en JSON. Sert au test de bout en bout du
        # pont depuis le serveur (systemd injecte le port).
        self.ask_host = os.environ.get("HERMES_BRIDGE_ASK_HOST", "127.0.0.1")
        self.ask_port = int(os.environ.get("HERMES_BRIDGE_ASK_PORT", "8052"))
        self.api_token = os.environ.get("DISCORD_BOT_API_TOKEN")
        self.ask_runner: typing.Optional[web.AppRunner] = None
        self.ask_site: typing.Optional[web.TCPSite] = None
        self.ask_lock = asyncio.Lock()

    # --- autorisation ------------------------------------------------------

    @staticmethod
    def _has_role(user: discord.abc.User) -> bool:
        """Vrai si l'utilisateur porte le role Hermes (compare sans la casse).

        En DM, py-cord rend un `Member` (avec ses roles) quand il a le serveur en
        cache, sinon un simple `User` sans attribut `roles` : d'ou le getattr.
        """
        return any(
            role.name.lower() == ROLE_NAME.lower()
            for role in getattr(user, "roles", None) or []
        )

    def _author_allowed(self, author: discord.abc.User) -> bool:
        """Autorise les masters du bot et les porteurs du role, en DM comme en serveur."""
        if author.id in masters:
            return True
        if self._has_role(author):
            return True
        for guild in self.bot.guilds:
            member = guild.get_member(author.id)
            if member and self._has_role(member):
                return True
        return False

    # --- appel Hermes ------------------------------------------------------

    async def _ask(self, user_id: int, message: str) -> str:
        """Envoie un message a Hermes et renvoie sa reponse."""
        if not BRIDGE_KEY:
            return "> Pont Hermes non configure (HERMES_BRIDGE_API_KEY manquant)."
        history = self.histories.setdefault(user_id, [])
        history.append({"role": "user", "content": message})
        payload = {
            "model": "discord-bridge",
            "messages": [{"role": "system", "content": SYSTEM_PROMPT}]
            + history[-MAX_HISTORY:],
            "stream": False,
        }
        headers = {
            "Authorization": f"Bearer {BRIDGE_KEY}",
            "Content-Type": "application/json",
        }

        def _do_request():
            """Requete bloquante, executee dans un thread pour ne pas figer la boucle."""
            response = requests.post(
                BRIDGE_URL, json=payload, headers=headers, timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()
            return response.json()

        data = await asyncio.to_thread(_do_request)
        answer = data["choices"][0]["message"]["content"] or "> (reponse vide)"
        history.append({"role": "assistant", "content": answer})
        return answer

    # --- ecoute Discord ----------------------------------------------------

    @commands.Cog.listener(name="on_message")
    async def on_message(self, msg: discord.Message):
        """En DM : chaque message est transmis directement a Hermes."""
        if msg.author == self.bot.user or msg.author.bot:
            return
        if not isinstance(msg.channel, discord.DMChannel):
            return
        if msg.content.startswith(prefix):
            return
        if not self._author_allowed(msg.author):
            return
        async with msg.channel.typing():
            try:
                answer = await self._ask(msg.author.id, msg.content)
            except Exception as exc:  # noqa: BLE001
                answer = f"> Erreur pont Hermes : {exc}"
        await self.send_long(msg.channel, answer)

    # --- commandes ---------------------------------------------------------

    @commands.command(name="hermes")
    async def hermes(self, ctx: commands.Context, *, message: str):
        """Parle a Hermes (masters et porteurs du role hermes)."""
        if ctx.guild and not self._author_allowed(ctx.author):
            return await ctx.send(f"> Acces refuse : reserve au role `{ROLE_NAME}`.")
        async with ctx.typing():
            try:
                answer = await self._ask(ctx.author.id, message)
            except Exception as exc:  # noqa: BLE001
                answer = f"> Erreur pont Hermes : {exc}"
        await self.send_long(ctx.channel, answer)

    @commands.command(name="hermes-reset")
    async def hermes_reset(self, ctx: commands.Context):
        """Oublie l'historique de conversation courant avec Hermes."""
        if ctx.guild and not self._author_allowed(ctx.author):
            return
        self.histories.pop(ctx.author.id, None)
        await ctx.send("> Historique Hermes reinitialise.")

    @commands.command(name="hermes-setup")
    async def hermes_setup(self, ctx: commands.Context):
        """Cree le role Discord hermes et l'attribue aux masters du bot."""
        if ctx.author.id not in masters:
            return await ctx.send("> Acces refuse : reserve aux masters.")
        if not ctx.guild:
            return await ctx.send("> Commande utilisable uniquement en serveur.")
        await create_role_if_missing(ctx, ROLE_NAME, self.color)
        await ctx.send(f"> Role `{ROLE_NAME}` pret.")

    # --- surface de test locale (loopback) ---------------------------------

    @web.middleware
    async def _ask_auth(self, request: web.Request, handler):
        """Meme convention que cogs/api.py : Bearer exige seulement si le token est pose."""
        if self.api_token and request.path != "/live":
            if request.headers.get("Authorization") != f"Bearer {self.api_token}":
                return web.json_response({"error": "Unauthorized"}, status=401)
        return await handler(request)

    @commands.Cog.listener(name="on_ready")
    async def start_ask_server(self):
        """Demarre la surface de test (idempotent : on_ready peut se redeclencher)."""
        async with self.ask_lock:
            if self.ask_site is not None:
                return
            app = web.Application(middlewares=[self._ask_auth])
            app.router.add_get("/live", self.ask_live)
            app.router.add_post("/hermes/ask", self.ask_http)
            self.ask_runner = web.AppRunner(app)
            await self.ask_runner.setup()
            site = web.TCPSite(self.ask_runner, self.ask_host, self.ask_port)
            try:
                await site.start()
            except OSError:
                await self.ask_runner.cleanup()
                self.ask_runner = None
                raise
            self.ask_site = site
            print(f"Hermes ask server listening on {self.ask_host}:{self.ask_port}")

    def cog_unload(self):
        """Arrete la surface de test."""
        if self.ask_runner:
            asyncio.create_task(self.ask_runner.cleanup())

    async def ask_live(self, request: web.Request):
        """Healthcheck."""
        return web.Response(text="OK")

    async def ask_http(self, request: web.Request):
        """POST {"message": "..."} -> {"answer": "..."} (historique par user_id)."""
        try:
            body = await request.json()
        except Exception:  # noqa: BLE001
            return web.json_response({"error": "JSON invalide."}, status=400)
        body = body or {}
        message = body.get("message")
        if not message:
            return web.json_response({"error": "Champ 'message' manquant."}, status=400)
        try:
            user_id = int(body.get("user_id") or (masters[0] if masters else 0))
        except (TypeError, ValueError):
            return web.json_response({"error": "user_id invalide."}, status=400)
        try:
            answer = await self._ask(user_id, message)
        except Exception as exc:  # noqa: BLE001
            return web.json_response(
                {"error": f"{type(exc).__name__}: {exc}"}, status=502
            )
        return web.json_response({"answer": answer, "user_id": user_id})

    # --- utilitaires -------------------------------------------------------

    @staticmethod
    async def send_long(channel, text: str):
        """Decoupe les reponses de plus de 2000 caracteres (limite Discord)."""
        if not text:
            text = "> (reponse vide)"
        for i in range(0, len(text), 1990):
            await channel.send(text[i : i + 1990])


def setup(bot: commands.Bot):
    """Setup du cog Hermes."""
    bot.add_cog(Hermes(bot))
