import signal
from contextlib import contextmanager
from io import StringIO
import sys
from discord.ext import commands
import discord


def parse(cmd, *args, key="$"):
    """Ajoute des arguments dans une commande."""
    i = 0
    while key in cmd and i < len(args):
        cmd = cmd.replace(key, args[i].strip(), 1)
        i += 1
    return cmd


class Capturing(list):
    """Capture print output and store it."""

    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self

    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio  # free up some memory
        sys.stdout = self._stdout


def name_to_id(ctx: commands.Context, name: str):
    """Convert a name to id."""
    member = discord.utils.get(ctx.guild.members, name=name)
    return member.id


def id_to_name(bot, id):
    """Convert an id to a name."""
    user = bot.get_user(id)
    return user.name


def tag_to_id(tag):
    """Convert a discord tag to a discord id."""
    return int(tag.replace("<@!", "").replace(">", ""))


def id_to_tag(id):
    """Convert a discord id to a discord tag."""
    return f"<@!{id}>"


class DictObject(dict):
    """Tricky way to make a dictionary usable as a python object."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__dict__ = self


def post_passer(func, *passed_args, **passed_kwargs):
    """Decorator that passes additionnal arguments (after its own) to a function."""

    def decorated(*args, **kwargs):
        args = list(args)
        args.extend(passed_args)
        args = tuple(args)
        kwargs.update(passed_kwargs)
        return func(*args, **kwargs)

    return decorated


def for_all_cog_methods(decorator_method):
    def decorate(cls):
        def decorator__new__(new):
            def decorated__new__(cls, *args, **kwargs):
                o = new(cls, *args, **kwargs)
                decorated_cog_commands = []
                for command in o.__cog_commands__:
                    decorated = decorator_method(command)
                    decorated_cog_commands.append(decorated)
                o.__cog_commands__ = tuple(decorated_cog_commands)
                return o

            return decorated__new__

        cls.__new__ = decorator__new__(cls.__new__)
        return cls

    return decorate


def keep(t: dict, l: list):
    """Return the list of items of a dictionary whose keys are in a given list."""
    nt = t.copy()
    results = []
    for k, v in t.items():
        if isinstance(v, dict):
            results.extend(keep(v, l))
        elif isinstance(v, list):
            for e in v:
                results.extend(keep(e, l))
        elif k in l:
            results.append((k, v))
    return results


@contextmanager
def time_limit(seconds):
    """Decorator that gives a time limit to execute a function."""

    def signal_handler(signum, frame):
        raise TimeoutError("Timed out!")

    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)


async def not_invoked_command(ctx: commands.Context, group: str):
    return await ctx.send(
        f"> **Erreur**: La commande `{ctx.message.content.replace(ctx.bot.command_prefix, '', 1).strip()}` est inexistante."
        f"\n> Tapez `{ctx.bot.command_prefix}help {group}` pour voir la liste des commandes disponibles."
    )


def lazy_embed(
    fields: dict,
    title: str = None,
    description: str = None,
    color: bytes = None,
    footer: str = None,
    url: str = None,
    thumbnail: str = None,
    image: str = None,
):
    """Lazy way to make an embed."""
    embed = discord.Embed(title=title, description=description, color=color, url=url)
    if thumbnail:
        embed.set_thumbnail(url=thumbnail)
    if image:
        embed.set_image(url=image)
    for k, v in fields.items():
        embed.add_field(name=k, value=v)
    if footer:
        embed.set_footer(text=footer)
    return embed
