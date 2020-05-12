from config.config import access, status, delete_after_time, masters
from utils import tools

from discord.ext import commands
import discord
import os


class Test(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    @access.admin
    async def number(self, ctx, amount:int):
        """Testing missing amount argument for error."""
        await ctx.send(amount)

    @commands.command(hidden=True)
    @access.limit(*masters)
    async def test_limit(self, ctx):
        """Test the access.limit decorator."""
        await ctx.send("all good")

    @commands.command(hidden=True)
    @commands.has_permissions(manage_messages=True)
    async def test_permissions(self, ctx):
        """Test the commands.has_permissions decorator."""
        await ctx.send("all good")


    # @commands.Cog.listener()
    # async def on_command_error(self, ctx, error):
    #     if isinstance(error, commands.errors.MissingRequiredArgument):
    #         await ctx.send(f"Veuillez insérez tous les arguments."
    #             "Tapez '.help [commande]' pour voir les arguments d'une commande.")
    #     else:
    #         raise error


    @commands.command(name="dl-music", hidden=True)
    @access.admin
    async def download_music(self, ctx, url:str):
        """Download a music on my computer."""
        d = os.getcwd()
        os.chdir("/Volumes/$/Youtube/Discord/")
        await ctx.send("Musics downloading.")
        cmd = "youtube-dl -ciw -x --audio-format 'mp3' --audio-quality 0 -f bestaudio --embed-thumbnail -o '%(title)s.%(ext)s' --rm-cache-dir"
        os.system(cmd+' '+url)
        os.chdir(d)
        await ctx.send("Musics downloaded.")

    @commands.command(name='user-test', hidden=True)
    @access.admin
    async def user_test(self, ctx, user:discord.User):
        """Return the user."""
        await ctx.send(user)

    @commands.command(name='member-test', hidden=True)
    @access.admin
    async def member_test(self, ctx, member:discord.Member):
        """Return the member."""
        await ctx.send(member)

    @commands.command(name='fetch-user', hidden=True)
    @access.admin
    async def fetch_user(self, ctx, id:int):
        """Send the username with its id."""
        user = await self.bot.fetch_user(id)
        await ctx.send(user)

    @commands.command(name='get-user', hidden=True)
    @access.admin
    async def get_user(self, ctx, user):
        """Send the username whatever argument is given."""
        try:
            user = discord.User(state=user)
        except:
            user = await self.bot.fetch_user(id)
        await ctx.send(user)

    @commands.command(name='user-id', hidden=True)
    @access.admin
    async def user_id(self, ctx, user:discord.User):
        """Return the id of the given user."""
        await ctx.send(user.id)



def setup(bot):
    bot.add_cog(Test(bot))
    

