from utils.date import days, months
from discord.ext import commands

import discord
import datetime
import os


class Planning(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot
        self.api:PycloudService = None
        self.event_color = discord.Color.magenta()

    @commands.group(name="planning")
    async def planning(self, ctx:commands.Context):
        """Gère le planning de marc."""
        if not self.api:
            from pyicloud import PyiCloudService
            self.api = PyiCloudService(os.environ['APPLE_MAIL'], os.environ['APPLE_PASSWORD'])

    @planning.command(name="jour")
    async def show_day(self, ctx:commands.Context, day:str="today"):
        """Affiche le planning pour un jour donné."""
        lowercase_days = [d.lower() for d in days]
        day = day.replace('/', '-')
        now = datetime.datetime.now()
        if day in ['yesterday', 'today', 'tommorow', 'hier', 'aujourdhui', 'demain']:
            if day in ['yesterday', 'hier']:
                await self.yesterday(ctx)
            elif day in ['today', 'aujourdhui']:
                await self.today(ctx)
            elif day in ['tommorow', 'demain']:
                await self.tommorow(ctx)
        elif day.startswith(('-', '+')):
            if day.startswith('-'):
                date = now - datetime.timedelta(int(day[1:]))
            elif day.startswith('+'):
                date = now + datetime.timedelta(int(day[1:]))
                await self.show_day_events(ctx, date)
        elif '-' in day:
            date = day.split('-')
            if len(date) == 1:
                date = datetime.datetime(now.year, now.month, int(date[0]))
            elif len(date) == 2:
                date = datetime.datetime(now.year, int(date[1]), int(date[0]))
            elif len(date) == 3:
                date = datetime.datetime(int(date[2]), int(date[1]), int(date[0]))
            else:
                msg = "Il n'existe pas de date avec ce format."
                return await ctx.send(msg)
            await self.show_day_events(ctx, date)
        elif day.lower() in lowercase_days:
            i = lowercase_days.index(day.lower())
            d = now.weekday()
            dt = (7+i-d)%7
            date = now + datetime.timedelta(dt)
            await self.show_day_events(ctx, date)
        else:
            print(day, days)
            msg = "Ce format de date n'est pas accepté."
            return await ctx.send(msg)

    @planning.command(name="lire")
    async def read(self, ctx:commands.Context, from_dt:str, to_dt:str, n:int=None):
        """Lis le planning sur une durée."""
        events = self.api.calendar.events(from_dt, to_dt)
        for event in events:
            embed = self.embed_event(event)
            await ctx.send(embed=embed)

    @planning.command(name="maintenant", aliases=['mtn', 'now'])
    async def now(self, ctx:commands.Context, days:int=1, n:int=float('inf')):
        """Affiche le planning maintenant."""
        now = datetime.datetime.now()
        to_dt = now + datetime.timedelta(days=days)
        from_dt = now - datetime.timedelta(days=days)
        events = self.api.calendar.events(from_dt, to_dt)
        i = 0
        for event in events:
            if i>=n:
                break
            startDate = datetime.datetime(*event['startDate'][1:-1])
            endDate = datetime.datetime(*event['endDate'][1:-1])
            if startDate < now < endDate:
                i+=1
                embed = self.embed_event(event)
                await ctx.send(embed=embed)
        if i==0:
            msg = "Vous êtes libre pour le moment."
            await ctx.send(msg)

    @planning.command(name="hier", aliases=['yesterday'])
    async def yesterday(self, ctx:commands.Context, with_guid=False, embedding=False, n:int=float('inf')):
        """Affiche le planning du jour."""
        date = datetime.datetime.now() - datetime.timedelta(1)
        await self.show_day_events(ctx, date, with_guid, embedding, n)
    
    @planning.command(name="ajourdhui", aliases=['today'])
    async def today(self, ctx:commands.Context, with_guid=False, embedding=False, n:int=float('inf')):
        """Affiche le planning du jour."""
        now = datetime.datetime.now()
        await self.show_day_events(ctx, now, with_guid, embedding, n)

    @planning.command(name="demain", aliases=['tommorow'])
    async def tommorow(self, ctx:commands.Context, with_guid=False, embedding=False, n:int=float('inf')):
        """Affiche le planning du jour."""
        date = datetime.datetime.now() + datetime.timedelta(1)
        await self.show_day_events(ctx, date, with_guid, embedding, n)

    async def show_day_events(self,
            ctx:commands.Context,
            date:datetime.datetime,
            with_guid=False,
            embedding=False,
            n:int=float('inf')
        ):
        """Affiche les évènements d'un jour donné."""
        from_dt = datetime.datetime(date.year, date.month, date.day)
        to_dt = datetime.datetime(date.year, date.month, date.day, 23, 59, 59, 999)
        await self.show_events(ctx, from_dt, to_dt, with_guid, embedding, n)
    
    async def show_events(self,
            ctx:commands.Context,
            from_dt:datetime.datetime,
            to_dt:datetime.datetime,
            with_guid=False,
            embedding=False,
            n:int=float('inf')
        ):
        """Affiche des évènements."""
        events = self.api.calendar.events(from_dt, to_dt)
        events = self.filter_events(events, from_dt, to_dt, n)
        if not embedding:
            msg = self.list_events(events, with_guid)
            await ctx.send(msg)
        else:
            embed = self.embed_events(events)
            await ctx.send(embed=embed)

    def filter_events(self, events, from_dt, to_dt, n):
        """Filtre des évènements."""
        filtered_events = []
        i = 0
        for event in events:
            if i>=n:
                break
            startDate = datetime.datetime(*event['startDate'][1:-1])
            endDate = datetime.datetime(*event['endDate'][1:-1])
            if from_dt < endDate and to_dt > startDate:
                i+=1
                filtered_events.append(event)
        return filtered_events

    @planning.command(name="détail", aliases=['detail'])
    async def detail(self, ctx:commands.Context, guid:str, pguid:str="home"):
        """Affiche les détails d'un évènement donné."""
        guid = guid.replace('.', '_').upper()
        event = self.api.calendar.get_event_detail(pguid, guid)
        embed = self.embed_event(event)
        await ctx.send(embed=embed)

    def embed_events(self, events):
        """Fait une jolie intégration pour plusieurs événements."""
        embed = discord.Embed(title="Aujourd'hui", color=self.event_color)
        events.sort(key = lambda e:e['startDate'])
        for event in events:
            start = f"{event['startDate'][4]}:{event['startDate'][5]}"
            end = f"{event['endDate'][4]}:{event['endDate'][5]}"
            duration = f"{start} => {end}\n{event['guid']}"
            embed.add_field(name=event['title'], value=duration)
        return embed

    def list_events(self, events, with_guid=False):
        """Liste les évènements."""
        events.sort(key = lambda e:e['startDate'])
        f = lambda date: f"{str(date[4]).zfill(2)}:{str(date[5]).zfill(2)}"
        lines = []
        for event in events:
            start = f(event['startDate'])
            end = f(event['endDate'])
            line = f"> {start}|{end} {event['title']}"
            if with_guid: line += f" {event['guid']}"
            line = line.replace('_', '.').lower()
            lines.append(line)
        return '\n'.join(lines)

    def embed_event(self, event):
        """Fait une jolie intégration pour un événement."""
        embed = discord.Embed(title=event['title'], color=self.event_color)
        if event['icon']:
            embed.set_thumbnail(url=event['icon'])
        duration = f"{event['duration']} minutes"
        allDay = ("oui" if event['allDay'] else "non")
        readOnly = ("oui" if event['readOnly'] else "non")
        reccurent = ("oui" if event['recurrenceMaster'] else "non")
        startDate = datetime.datetime(*event['startDate'][1:-1])
        startDate = f'{days[startDate.weekday()]} {startDate.day} {months[startDate.month]} {startDate.year} {str(startDate.hour).zfill(2)}:{str(startDate.minute).zfill(2)}'
        endDate = datetime.datetime(*event['endDate'][1:-1])
        endDate = f'{days[endDate.weekday()]} {endDate.day} {months[endDate.month]} {endDate.year} {str(endDate.hour).zfill(2)}:{str(endDate.minute).zfill(2)}'
        embed.add_field(name="durée", value=duration)
        embed.add_field(name="début", value=startDate)
        embed.add_field(name="fin", value=endDate)
        embed.add_field(name="toute la journée", value=allDay)
        embed.add_field(name="lecture seule", value=readOnly)
        embed.add_field(name="récurrent", value=reccurent)
        embed.set_footer(text=event['pGuid']+"\n"+event['guid'])
        return embed


def setup(bot):
    bot.add_cog(Planning(bot))