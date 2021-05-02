"""
Control over my docker cluster.
"""

import os

import requests
import discord

from discord.ext import commands, tasks

from rich import print


class Docker(commands.Cog):
    """Manage my docker containers."""

    def __init__(self, bot: commands.Bot, **kwargs):
        """Initialize the ialab cog."""
        super().__init__(**kwargs)
        self.bot: commands.Bot = bot
        self.url: str = os.environ["DOCKER_API_URL"]
        self.keys = [
            "ExposedPorts",
            "Hostname",
            "Labels",
            "Args",
        ]
        self.states = dict(
            exited=discord.Color.red(),
            running=discord.Color.green(),
            restarting=discord.Color.orange(),
        )

    @commands.group(aliases=["d"])
    async def docker(self, ctx: commands.Context):
        """Main command group of docker."""
        if not ctx.invoked_subcommand:
            await ctx.send(os.path.join(self.url, "docs"))

    @docker.group(aliases=["c"])
    async def container(self, ctx: commands.Context, container_id: str):
        """Group of command about one container."""
        container = requests.get(f"{self.url}/container/{container_id}").json()
        print(container)

        embed = discord.Embed(
            title=container["Name"][1:],
            color=self.states[container["State"]["Status"]],
            description=f"Image: **{container['Config']['Image']}**"
            + f"\nState: {container['State']['Status']}"
            + f"\nRestart Count: {container['RestartCount']}"
            + f"\nPause: {container['State']['Paused']}"
            + f"\nPid: {container['State']['Pid']}"
            + f"\nPorts: {', '.join(container['NetworkSettings']['Ports'].keys())}",
        )
        # embed.add_field(name="Ports", value=container["NetworkSettings"]["Ports"])
        embed.add_field(
            name="Networks",
            value=" ".join(container["NetworkSettings"]["Networks"].keys()),
        )
        embed.add_field(
            name="Entrypoint", value=" ".join(container["Config"]["Entrypoint"])
        )
        embed.add_field(name="Args", value=" ".join(container["Args"]))
        embed.add_field(name="Mounts", value="\n".join(map(str, container["Mounts"])))
        # embed.set_thumbnail(
        #     url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR1VTGChfJWev0H4oLu4CqZpMRWMEG4p9wLQwSlVH72X-HYRXB1kGy8Fg5IsRn3TD5Cdlg&usqp=CAU"
        # )
        embed.set_footer(
            text="id: " + container["Id"],
            icon_url=f"https://hub.docker.com/u/{container['Config']['Image']}",
        )
        await ctx.send(embed=embed)

    @docker.group(aliases=["ps"])
    async def containers(self, ctx: commands.Context):
        """List all containers."""
        if ctx.invoked_subcommand:
            return
        containers = requests.get(f"{self.url}/containers").json()
        # print(containers)
        # max_name = 0
        # max_image = 0
        infos = []
        for container in containers:
            info = dict(
                name=container["Name"][1:].replace("_", "‗"),
                image=container["Config"]["Image"].replace("_", "‗"),
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

    @containers.command(aliases=["ids"])
    async def containers_ids(self, ctx: commands.Context):
        """List all containers."""
        lines = requests.get(f"{self.url}/containers/ids").json()
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

    @docker.command(aliases=["is"])
    async def images(self, ctx: commands.Context):
        """List all images."""
        images = requests.get(f"{self.url}/images").json()
        lines = ["".join(image["RepoTags"]) for image in images]
        text = "".join([f"\n* {line.replace('_', '‗')}" for line in lines if line.replace(" ", "")])
        return await ctx.send(f"```md\n{text}\n```")


def setup(bot: commands.Bot):
    """Setup the ialab cog."""
    bot.add_cog(Docker(bot))
