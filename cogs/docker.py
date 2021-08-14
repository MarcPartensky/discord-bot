"""
Control over my docker containers.
"""

import os

import requests
import discord

from discord.ext import commands, tasks
from config.config import docker_role, masters

from rich import print


class Docker(commands.Cog):
    """Manage my docker containers."""

    def __init__(self, bot: commands.Bot, **kwargs):
        """Initialize the ialab cog."""
        super().__init__(**kwargs)
        self.bot: commands.Bot = bot
        self.url: str = os.environ["DOCKER_API_URL"]
        self.color = discord.Colour(0x4EB3F2)
        self.states = dict(
            exited=discord.Color.red(),
            running=discord.Color.green(),
            restarting=discord.Color.orange(),
        )

    @commands.group(aliases=["d"])
    async def docker(self, ctx: commands.Context):
        """Main command group of docker.
        Only members with the docker role can run those commands."""
        print(masters)
        print(ctx.guild.members)
        if not docker_role in [role.name for role in ctx.guild.roles]:
            role = await ctx.guild.create_role(name=docker_role, colour=self.color)
            await ctx.send(f"> Created `{docker_role}` role.")
            members = []
            for master in masters:
                if member := await ctx.guild.fetch_member(master):
                    print(member, member.id, master)
                    await member.add_roles(role)
                    members.append(member)
            if members:
                members = "\n".join(map(lambda m: f"+ {member}", members))
                await ctx.send(
                    '```diff\nAdded "' + docker_role + '" role to:\n' + members + "```"
                )
                return
        if not ctx.invoked_subcommand:
            await ctx.send(os.path.join(self.url, "docs"))

    @commands.has_role(docker_role)
    @docker.group()
    async def ps(self, ctx: commands.Context, *container_ids: str):
        """Group of command about one container."""
        if len(list(container_ids)) == 0:
            return await self.ps_all(ctx)
        for container_id in container_ids:
            container = requests.get(f"{self.url}/ps/{container_id}").json()
            print(container)

            title = container["Name"][1:]
            color = self.states[container["State"]["Status"]]
            description = (
                f"Image: **{container['Config']['Image']}**"
                + f"\nPorts: {', '.join(container['NetworkSettings']['Ports'].keys())}"
                + f"\nNetworks: {', '.join(container['NetworkSettings']['Networks'].keys())}"
                + f"\nState: {container['State']['Status']}"
                + f"\nPause: {container['State']['Paused']}"
                + f"\nRestart Count: {container['RestartCount']}"
                + f"\nPid: {container['State']['Pid']}"
            )
            print(title)
            print(color)
            print(description)

            embed = discord.Embed(title=title, color=color, description=description)
            if "Entrypoint" in container["Config"]:
                embed.add_field(
                    name="Entrypoint", value=" ".join(container["Config"]["Entrypoint"])
                )

            if "Args" in container:
                embed.add_field(name="Args", value=" ".join(container["Args"]))

            if "Binds" in container["HostConfig"]:
                embed.add_field(
                    name="Volumes", value="\n".join(container["HostConfig"]["Binds"])
                )

            # icon_url=f"https://hub.docker.com/u/{container['Config']['Image']}",

            embed.set_footer(
                text="id: " + container["Id"],
                icon_url="https://blog.knoldus.com/wp-content/uploads/2017/12/docker_facebook_share.png",
            )
            await ctx.send(embed=embed)

    @commands.has_role(docker_role)
    @docker.command()
    async def restart(self, ctx: commands.Context, *names: str):
        """Restart some containers."""
        for name in names:
            async with ctx.typing():
                response = requests.post(f"{self.url}/restart/{name}")
            print(response)
            if response.status_code == 200:
                return await ctx.send(f"> Restarted **{name}** successfully!")
            else:
                return await ctx.send(f"> Failed restarting **{name}**!")

    @commands.has_role(docker_role)
    @docker.command()
    async def exec(self, ctx: commands.Context, name: str, cmd: str):
        """Run a command in a container."""
        async with ctx.typing():
            response = requests.post(f"{self.url}/exec/{name}/{cmd}")
        print(response)
        if response.status_code == 200:
            return await ctx.send("> {response.content}")
        else:
            return await ctx.send(f"> Failed to run **{cmd}**!")

    @commands.has_role(docker_role)
    @docker.command()
    async def kill(self, ctx: commands.Context, *names: str):
        """Kill some containers."""
        for name in names:
            async with ctx.typing():
                response = requests.post(f"{self.url}/kill/{name}")
            print(response)
            if response.status_code == 200:
                return await ctx.send(f"> Killed **{name}** successfully!")
            else:
                return await ctx.send(f"> Failed killing **{name}**!")

    @commands.has_role(docker_role)
    @docker.command()
    async def stop(self, ctx: commands.Context, *names: str):
        """Stop some containers."""
        for name in names:
            async with ctx.typing():
                response = requests.post(f"{self.url}/stop/{name}")
            print(response)
            if response.status_code == 200:
                return await ctx.send(f"> Stopped **{name}** successfully!")
            else:
                return await ctx.send(f"> Failed stopping **{name}**!")

    @commands.has_role(docker_role)
    @docker.command(aliases=["rm"])
    async def remove(self, ctx: commands.Context, *names: str):
        """Remove some containers."""
        for name in names:
            async with ctx.typing():
                response = requests.post(f"{self.url}/remove/{name}")
            print(response)
            if response.status_code == 200:
                return await ctx.send(f"> Removed **{name}** successfully!")
            else:
                return await ctx.send(f"> Failed removing **{name}**!")

    @commands.has_role(docker_role)
    @docker.command(aliases=["p"])
    async def pause(self, ctx: commands.Context, *names: str):
        """Pause some containers."""
        for name in names:
            async with ctx.typing():
                response = requests.post(f"{self.url}/pause/{name}")
            print(response)
            if response.status_code == 200:
                return await ctx.send(f"> Paused **{name}** successfully!")
            else:
                return await ctx.send(f"> Failed pausing **{name}**!")

    @commands.has_role(docker_role)
    @docker.command(aliases=["unp"])
    async def unpause(self, ctx: commands.Context, *names: str):
        """Un pause some containers."""
        for name in names:
            async with ctx.typing():
                response = requests.post(f"{self.url}/unpause/{name}")
            print(response)
            if response.status_code == 200:
                return await ctx.send(f"> Paused **{name}** successfully!")
            else:
                return await ctx.send(f"> Failed pausing **{name}**!")

    @commands.has_role(docker_role)
    @docker.command(aliases=["rn"])
    async def rename(self, ctx: commands.Context, name: str, to: str):
        """Remove a container."""
        async with ctx.typing():
            response = requests.post(f"{self.url}/rename/{name}/{to}")
        print(response)
        if response.status_code == 200:
            return await ctx.send(f"> Renamed **{name}** to **{to}** successfully!")
        else:
            return await ctx.send(f"> Failed renaming **{name}** to **{to}**!")

    @commands.has_role(docker_role)
    @docker.command()
    async def top(self, ctx: commands.Context, *names: str):
        """Return the top proccesses of some containers."""
        for name in names:
            async with ctx.typing():
                response = requests.post(f"{self.url}/top/{name}")
            print(response)
            if response.status_code == 200:
                return await ctx.send(f"> Top processes:\n" + response.content)
            else:
                return await ctx.send(f"> {response.reason}")

    @commands.has_role(docker_role)
    @docker.command()
    async def logs(self, ctx: commands.Context, name: str, since: int):
        """Return the logs of a container."""
        async with ctx.typing():
            response = requests.post(f"{self.url}/logs/{name}/{since}")
        print(response)
        if response.status_code == 200:
            return await ctx.send(f"> {response.content}")
        else:
            return await ctx.send(f"> {response.reason}")

    async def ps_all(self, ctx: commands.Context):
        """List all containers."""
        if ctx.invoked_subcommand:
            return
        containers = requests.get(f"{self.url}/ps").json()
        # print(containers)
        # max_name = 0
        # max_image = 0
        infos = []
        for container in containers:
            info = dict(
                name=container["Name"][1:].replace("_", " 𛲖 "),
                image=container["Config"]["Image"].replace("_", "𛲖"),
                ports=",".join(container["NetworkSettings"]["Ports"].keys()).replace(
                    "/tcp", ""
                ),
            )
            # max_name = max(max_name, len(info["name"]))
            # max_image = max(max_image, len(info["image"]))
            infos.append(info)
        text = "```md\n"
        n = 23
        for info in infos:
            if len(info["name"]) < n:
                line = info["name"] + " " * (n - len(info["name"]))
            else:
                line = info["name"][: n - 1] + "…"
            if len(info["image"]) < n:
                line += " " + info["image"] + " " * (n - len(info["image"]))
            else:
                line += " " + info["image"][: n - 1] + "…"
            line += " " + info["ports"]
            new_text = text + "\n" + line
            if len(new_text + "\n```") > 2000:
                await ctx.send(text + "\n```")
                print(text)
                text = "```md\n* " + line
            else:
                text += "\n* " + line
        print(text)
        await ctx.send(text + "\n```")

    @commands.has_role(docker_role)
    @docker.command(aliases=["ids"])
    async def containers_ids(self, ctx: commands.Context):
        """List all containers."""
        lines = requests.get(f"{self.url}/ps/ids").json()
        print(lines)
        text = ""
        for line in lines:
            new_text = text + "\n" + line
            if len(new_text) > 2000:
                await ctx.send(text)
                print(text)
                text = "\n" + line
            else:
                text += "\n" + line
        print(text)
        await ctx.send(text + "\n")

    @commands.has_role(docker_role)
    @docker.command(aliases=["is"])
    async def images(self, ctx: commands.Context):
        """List all images."""
        images = requests.get(f"{self.url}/images").json()
        lines = ["".join(image["RepoTags"]) for image in images]
        text = "".join(
            [f"\n* {line.replace('_', '𛲖')}" for line in lines if line.replace(" ", "")]
        )
        print(text)
        return await ctx.send(f"```md\n{text}\n```")


def setup(bot: commands.Bot):
    """Setup the ialab cog."""
    bot.add_cog(Docker(bot))
