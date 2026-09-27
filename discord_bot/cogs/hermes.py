#!/usr/bin/env python
"""Pont vers un gateway Hermes Agent dedie (profil `discord-bridge`).

Reserve aux membres qui portent le role Discord `hermes` (nom configurable via
`HERMES_BRIDGE_ROLE_NAME`) et aux masters du bot. Parle a l'API server
OpenAI-compatible du gateway Hermes dedie (services/discord-hermes-bridge cote
NixOS, loopback uniquement).

Variables d'environnement (injectees par systemd, cf. services/discord-bot) :
    HERMES_BRIDGE_URL        ex. http://127.0.0.1:8642/p/discord-bridge/v1/chat/completions
    HERMES_BRIDGE_API_KEY    bearer token (sops secrets/discord-hermes-bridge.yml)
    HERMES_BRIDGE_ROLE_NAME  nom du role Discord autorise (defaut "hermes")

L'API server Hermes est un listener UNIQUE par hote (profil default) ; un profil
secondaire y est expose sous /p/<profil>/..., d'ou le chemin ci-dessus.
"""

import asyncio
import os
import typing

import discord
import requests
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

    # --- ecoute ------------------------------------------------------------

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
