from io import StringIO 
import sys
import discord

def parse(cmd, *args, key="$"):
    """Ajoute des arguments dans une commande."""
    i = 0
    while key in cmd and i<len(args):
        cmd = cmd.replace(key,args[i].strip(), 1)
        i+=1
    return cmd

class Capturing(list):
    """Capture print output and store it."""
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self
    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio    # free up some memory
        sys.stdout = self._stdout

def name_to_id(ctx:discord.ext.commands.Context, name):
    """Convert a name to id."""
    member = discord.utils.get(ctx.guild.members, name=name)
    return member.id

def id_to_name(bot, id):
    """Convert an id to a name."""
    user = bot.get_user(id)
    return user.name

def tag_to_id(tag):
    return int(tag.replace('<@!', '').replace('>',''))
def id_to_tag(id):
    return f"<@!{id}>"

