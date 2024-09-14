from config.config import cluster
from models.playlist import Playlist

# print(Playlist)
from discord.ext import commands
import discord
import string


class PlayList(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.playlists: MongoDatabase = cluster.playlists
        self.user_playlists = {}
        self.user_playlist_messages = {}

    @commands.group(aliases=["pl"])
    async def playlist(self, ctx: commands.Context):
        """Commande de base pour gérer les playlistes."""
        if not ctx.invoked_subcommand:
            print("Vous n'avez pas invoké de sous-commande.")

    @commands.group()
    async def playlists(self, ctx: commands.Context):
        if not ctx.invoked_subcommand:
            await self.list_playlists(ctx)

    @playlist.command(name="afficher", aliases=["show"])
    async def show(self, ctx: commands.Context, title: str = None):
        """Affiche une playliste."""
        playlist_id, playlist = self.select(ctx, title)
        await ctx.send(embed=playlist.embed(ctx))

    @playlist.command(name="brute", aliases=["raw"])
    async def raw(self, ctx: commands.Context, title: str = None):
        """Affiche une playliste brute."""
        playlist_id, playlist = self.select(ctx, title)
        await ctx.send(list(playlist.collection))

    @playlist.command(name="items")
    async def items(self, ctx: commands.Context, title: str = None):
        """Affiche les items d'une collection."""
        playilst_id, playlist = self.select(ctx, title)
        items = list(playlist.collection.items())
        await ctx.send("\n".join(map(lambda t: f"{t[0]}: {t[1]}", items)))

    @playlist.command(name="indexes")
    async def indexes(self, ctx: commands.Context, title: str = None):
        """Affiche les indexes d'une playliste."""
        playlist_id, playlist = self.select(ctx, title)
        indexes = list(playlist.collection.list_indexes())
        indexes = [index["_id"] for index in indexes]
        await ctx.send("\n".join(indexes))

    @playlists.command(name="liste")
    async def list_playlists(self, ctx: commands.Context):
        """Liste les noms de playlistes enregistrées."""
        names = self.playlists.collection_names()
        msg = "> **Playlistes enregistrées:**"
        for name in names:
            msg += f"\n> {name}"
        return await ctx.send(msg)

    def is_valid_title(self, title: str):
        """Determine whether a title is valid or not."""
        punctuation = string.punctuation.replace("|", "")
        for c in title:
            if c in string.ascii_letters:
                continue
            elif c in string.digits:
                continue
            elif c in punctuation:
                continue
            else:
                return False
        return True

    def check_title(self, title: str):
        """Check whether a title is valid or not."""
        if not title:
            raise Exception("La playliste doit avoir un nom.")
        if not self.is_valid_title(title):
            raise Exception(
                f"Le titre n'est pas valide.\n \
                Celui doit être composé des caractères suivants: \n \
                    {string.ascii_letters} \
                    {string.digits} \
                    {string.punctuation.replace('|', '')}"
            )

    def get_playlist(self, ctx: commands.Context, title: str = None):
        """Return a playlist with an id."""
        if not ctx.author.id in self.user_playlists:
            raise Exception(
                "Utilisez 'playlist select [title]' pour sélectionner une playliste."
            )
        playlist_id = self.user_playlists[ctx.author.id]
        if not playlist_id in self.playlists:
            raise Exception(f"La playliste d'id {playlist_id} n'existe pas.")
        return Playlist(self.playlists[playlist_id])

    def get_playlist_from_id(self, playlist_id: str):
        """Return a playlist given its id."""
        if playlist_id in self.playlists:
            return Playlist(self.playlists[playlist_id])
        else:
            raise Exception(f"La playliste d'id {playlist_id} n'existe pas.")

    def get_playlist_id(self, ctx: commands.Context, title: str = None):
        """Return the playlist id given the context and title."""
        if title:
            return title  # +"|"+ctx.author.id
        elif ctx.author.id in self.user_playlists:
            return self.user_playlists[ctx.author.id]
        else:
            raise Exception(f"Playliste d'id {title} inexistante.")

    def select(self, ctx: commands.Context, title: str):
        """Select a playlist."""
        if title:
            self.check_title(title)
        playlist_id = self.get_playlist_id(ctx, title)
        playlist = self.get_playlist_from_id(playlist_id)
        self.user_playlists[ctx.author.id] = playlist_id
        return (playlist_id, playlist)

    def get_playlist_and_id(self, ctx: commands.Context, title: str = None):
        pass

    @playlist.command(name="sauvegarder", aliases=["save"])
    async def save(self, ctx: commands.Context, *, title: str = None):
        """Sauvegarde une playliste."""
        if not title:
            raise Exception("Vous devez préciser un nom pour votre playliste.")
        playlist_id = title
        music = self.bot.get_cog("Music")
        Playlist.create(ctx, self.playlists[playlist_id], title, music)
        self.user_playlists[ctx.author.id] = playlist_id
        msg = "La playliste a été sauvegardée."
        return await ctx.send(msg)

    @playlist.command()
    async def create(self, ctx: commands.Context, *, title: str = None):
        """Crée une nouvelle playliste."""

    @playlist.command()
    async def new(self, ctx: commands.Context, *, title: str = None):
        """Crée une nouvelle playliste vide."""

    @playlist.command(name="get")
    async def get_(self, ctx: commands.Context, path: str, *, title: str = None):
        """Affiche des informations sur une playliste."""
        playlist, playlist_id = self.select(ctx, title)
        if not playlist.has_right(ctx.author.id, "r"):
            msg = "Vous n'avez pas le droit de lire cette playliste."
            raise Exception(msg)
        e = playlist
        for key in path.split("/"):
            e = e[key]
        return await ctx.send(e)

    @playlist.command(name="set")
    async def set_(self, ctx: commands.Context, path, value, title: str = None):
        """Modifie les informations sur une playliste."""
        playlist, playlist_id = self.select(ctx, title)
        if not playlist.has_right(ctx.author.id, "e"):
            msg = "Vous n'avez pas le droit d'éditer cette playliste."
            raise Exception(msg)
        e = playlist
        for key in path.split("/"):
            e = e[key]

    @playlist.command(name="sélectionner", aliases=["select"])
    async def select_(self, ctx: commands.Context, title: str = None):
        """Sélectionne une playliste."""
        self.select(ctx, title)

    @playlist.command(name="sélection", aliases=["selection"])
    async def selection(self, ctx: commands.Context):
        """Affiche la playliste sélectionnée."""
        playlist_id, playlist = self.select(ctx)
        await ctx.send(playlist_id)

    @playlist.command(aliases=["supprimer"])
    async def delete(self, ctx: commands.Context, *, title: str = None):
        """Supprime une playliste."""
        playlist_id, playlist = self.select(ctx, title)
        if not playlist.has_right(ctx.author.id, "d"):
            msg = "Vous n'avez pas le droit de supprimer cette playliste."
            raise Exception(msg)
        del self.playlists[playlist_id]
        return await ctx.send("La playliste est supprimée")

    @playlist.command()
    async def listen(self, ctx: commands.Context, *, title: str = None):
        """Écoute une playliste."""
        playlist_id, playlist = self.select(ctx, title)
        if not playlist.has_right(ctx.author.id, "l"):
            msg = "Vous n'avez pas le droit d'écouter cette playliste."
            raise Exception(msg)
        music_cog = self.bot.get_cog("Music")
        await music_cog.cog_before_invoke(ctx)
        # music.ctx.voice_state = music.get_voice_state(ctx)
        await music_cog.ensure_voice_state(ctx)
        await music_cog._join(ctx)
        for url in playlist.collection.musics.musics:
            await music_cog._play(ctx, search=url)

    @playlist.group(name="ajouter", aliases=["add"])
    async def add(self, ctx: commands.Context, *args):
        """Ajoute des musiques, des rôles, ..."""

    @add.command(name="musique", aliases=["music"])
    async def add_music(self, ctx: commands.Context, *, title: str = None):
        """Ajoute une musique à une playliste."""
        playlist_id, playlist = self.select(ctx, title)
        user_rights = playlist.get_user_rights(ctx.author.id)
        if not playlist.has_right(ctx.author.id, "a"):
            msg = "Vous n'avez pas le droit d'ajouter de musique \
                à cette playliste."
            raise Exception(msg)

    @add.command(name="rôle", aliases=["role"])
    async def role(
        self, ctx: commands.Context, role: str, permissions: str, title: str = None
    ):
        """Ajoute un rôle."""
        playlist_id, playlist = self.select(ctx, title)
        if playlist.has_right(ctx.author.id, "m"):
            playlist.config.roles.append(role, permission)
        else:
            msg = "Vous n'avez pas le droit d'ajouter de roles à cette playliste."
            raise Exception(msg)

    @playlist.command(name="rôles", aliases=["roles"])
    async def roles(self, ctx: commands.Context, title: str = None):
        """Liste tous les rôles."""
        playlist_id, playlist = self.select(ctx, title)
        msg = ""
        for role, members in playlist.config.roles:
            msg += f"> {role}: {', '.join(members)}"
        await ctx.send(msg)

    @playlist.command(name="droits", aliases=["rights"])
    async def rights(self, ctx: commands.Context, title: str = None):
        """Liste tous les droits."""
        playlist_id, playlist = self.select(ctx, title)
        msg = ""
        for role, rights in playlist.config.rights:
            msg += f"> {role}: {rights}"
        await ctx.send(msg)

    # @playlist.command(name)


async def setup(bot):
    await bot.add_cog(PlayList(bot))
