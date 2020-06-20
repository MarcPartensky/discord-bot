from discord.ext import commands
import discord

import os
import requests

class Leekwars(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot
        self.api = "https://leekwars.com/api/"
        self.color = discord.Color.dark_green()
        self.profile:dict = None
        self.leek_id_ = None

    @property
    def farmer(self):
        return self.profile['farmer']

    @property
    def token(self):
        return self.profile['token']

    @property
    def leek_id(self):
        if not self.leek_id_:
            self.leek_id_ = list(self.farmer['leeks'].keys())[0]
        return self.leek_id_

    @leek_id.setter
    def leek_id(self, id):
        self.leek_id_ = id

    @property
    def leek(self):
        return self.farmer['leeks'][self.leek_id]

    def lazy_embed(self, json:dict, title:str="Leekwars"):
        """Fait une intégration paresseuse."""
        embed = discord.Embed(title=title, color=self.color)
        for (k,v) in json.items():
            if isinstance(v, dict):
                continue
            if isinstance(v, list):
                continue
            embed.add_field(name=k, value=str(v)[:1024] or "None")
        return embed


    @commands.command(name="connection")
    async def login(self):
        """pass."""

    @commands.group(name="leekwars", aliases=['lk'])
    async def leekwars(self, ctx:commands.Context):
        """Groupe de commandes pour Leekwars."""
        if not self.profile:
            url = os.path.join(
                self.api,
                "farmer/login-token",
                # "farmer/login",
                os.environ['LEEKWARS_USERNAME'],
                os.environ['LEEKWARS_PASSWORD'],
                # "true",
            )
            # params = dict(
            #     login=os.environ['LEEKWARS_USERNAME'],
            #     password=os.environ['LEEKWARS_PASSWORD'],
            #     keep_connected=True
            # )
            print(url)
            self.profile = requests.get(url=url).json()
            print(self.profile)

    @leekwars.command(name="profil")
    async def profile(self, ctx:commands.Context, id:str=""):
        """Profil leekwars."""
        if not id:
            pf = self.farmer
        else:
            url = os.path.join(
                self.api,
                "farmer/get",
                id,
            )
            print(url)
            pf = requests.get(url).json()['farmer']
        embed = self.lazy_embed(pf, "Profil Leekwars")
        return await ctx.send(embed=embed)

    @leekwars.command(name="placer-dans-potager")
    async def set_in_garden(self, ctx:commands.Context, boolean:str=""):
        """Placer dans le potager."""
        url = os.path.join(
            self.api,
            "farmer/set-in-garden",
            boolean,
        )
        params=dict(token=self.token)
        r = requests.get(url=url,params=params).json()
        embed = self.lazy_embed(r, "Placer dans Potager Leekwars")
        return await ctx.send(embed=embed)

    @leekwars.command(name="potager")
    async def garden(self, ctx:commands.Context):
        """Potager leekwars."""
        url = os.path.join(
            self.api,
            "garden/get",
            self.token,
        )
        print(url)
        r = requests.get(url=url).json()
        embed = self.lazy_embed(r, "Potager Leekwars")
        return await ctx.send(embed=embed)

    @leekwars.command(name="poireaux")
    async def leeks(self, ctx:commands.Context):
        """Affiche les poireaux du profil leekwars."""
        for (id, leek) in self.farmer['leeks'].items():
            embed = self.lazy_embed(leek, f"Poireau {leek['name']}")
            return await ctx.send(embed=embed)

    @leekwars.command(name="ennemis-poireau")
    async def opponents(self, ctx:commands.Context, leek_id:str=""):
        """Affiche les ennemis."""
        leek_id = leek_id or self.leek_id
        url = os.path.join(
            self.api,
            "garden/get-leek-opponents",
            leek_id,
            # self.token
        )
        print(url)
        r = requests.get(url=url).json()
        embed = self.lazy_embed(r, f"Ennemis du poireau {self.leek['name']}")
        return await ctx.send(embed=embed)


        





# {
#    "farmer":{
#       "id":64597,
#       "login":"Mazex",
#       "team":null,
#       "name":"Mazex",
#       "talent":100,
#       "leeks":{
#          "69649":{
#             "id":69649,
#             "name":"Mazex",
#             "color":"#00aa00",
#             "capital":15,
#             "level":21,
#             "talent":125,
#             "skin":1,
#             "hat":null,
#             "ai":318588,
#             "weapon":null,
#             "title":[

#             ]
#          }
#       },
#       "avatar_changed":0,
#       "talent_more":0,
#       "victories":77,
#       "draws":39,
#       "defeats":69,
#       "ratio":"1.12",
#       "connected":true,
#       "last_connection":1592656959,
#       "register_date":1552156428,
#       "fight_history":[
#          {
#             "id":31611328,
#             "date":1592656482,
#             "type":0,
#             "context":2,
#             "status":2,
#             "winner":1,
#             "farmer_team":null,
#             "result":"win",
#             "leeks1":[
#                {
#                   "id":69649,
#                   "name":"Mazex"
#                }
#             ],
#             "leeks2":[
#                {
#                   "id":76290,
#                   "name":"EvilLeeks"
#                }
#             ]
#          },
#          {
#             "id":31611327,
#             "date":1592656466,
#             "type":0,
#             "context":2,
#             "status":2,
#             "winner":1,
#             "farmer_team":null,
#             "result":"win",
#             "leeks1":[
#                {
#                   "id":69649,
#                   "name":"Mazex"
#                }
#             ],
#             "leeks2":[
#                {
#                   "id":76325,
#                   "name":"BleekChain"
#                }
#             ]
#          },
#          {
#             "id":31611326,
#             "date":1592656406,
#             "type":0,
#             "context":2,
#             "status":2,
#             "winner":0,
#             "farmer_team":null,
#             "result":"draw",
#             "leeks1":[
#                {
#                   "id":69649,
#                   "name":"Mazex"
#                }
#             ],
#             "leeks2":[
#                {
#                   "id":76367,
#                   "name":"Lya"
#                }
#             ]
#          },
#          {
#             "id":31611324,
#             "date":1592656388,
#             "type":0,
#             "context":2,
#             "status":2,
#             "winner":0,
#             "farmer_team":null,
#             "result":"draw",
#             "leeks1":[
#                {
#                   "id":69649,
#                   "name":"Mazex"
#                }
#             ],
#             "leeks2":[
#                {
#                   "id":76222,
#                   "name":"Papeleek"
#                }
#             ]
#          },
#          {
#             "id":31611322,
#             "date":1592656366,
#             "type":0,
#             "context":2,
#             "status":2,
#             "winner":0,
#             "farmer_team":null,
#             "result":"draw",
#             "leeks1":[
#                {
#                   "id":69649,
#                   "name":"Mazex"
#                }
#             ],
#             "leeks2":[
#                {
#                   "id":76251,
#                   "name":"ballecMec"
#                }
#             ]
#          },
#          {
#             "id":31611316,
#             "date":1592656303,
#             "type":0,
#             "context":2,
#             "status":2,
#             "winner":0,
#             "farmer_team":null,
#             "result":"draw",
#             "leeks1":[
#                {
#                   "id":69649,
#                   "name":"Mazex"
#                }
#             ],
#             "leeks2":[
#                {
#                   "id":76302,
#                   "name":"Norbertdu22"
#                }
#             ]
#          }
#       ],
#       "tournaments":[

#       ],
#       "admin":false,
#       "moderator":false,
#       "country":"gb",
#       "godfather":null,
#       "godsons":[

#       ],
#       "color":"",
#       "banned":0,
#       "won_solo_tournaments":0,
#       "won_farmer_tournaments":0,
#       "won_team_tournaments":0,
#       "total_level":21,
#       "leek_count":1,
#       "in_garden":1,
#       "fights":47,
#       "github":null,
#       "website":null,
#       "forum_messages":0,
#       "didactitiel_seen":1,
#       "contributor":false,
#       "trophies":20,
#       "language":"en",
#       "title":[

#       ],
#       "show_ai_lines":false,
#       "habs":11240,
#       "crystals":0,
#       "weapons":[
#          {
#             "id":739249,
#             "template":37
#          },
#          {
#             "id":868852,
#             "template":38
#          }
#       ],
#       "chips":[
#          {
#             "id":868859,
#             "template":18
#          }
#       ],
#       "ais":[
#          {
#             "id":291147,
#             "name":"Fuite ou Attaque"
#          },
#          {
#             "id":318588,
#             "name":"Github For The Win"
#          },
#          {
#             "id":291151,
#             "name":"Sans Titre"
#          },
#          {
#             "id":291145,
#             "name":"Sans Titre"
#          },
#          {
#             "id":318587,
#             "name":"Test"
#          },
#          {
#             "id":291118,
#             "name":"Tuto de base"
#          },
#          {
#             "id":318585,
#             "name":"Vive Github"
#          }
#       ],
#       "potions":[
#          {
#             "id":739250,
#             "template":58,
#             "quantity":20
#          },
#          {
#             "id":793442,
#             "template":58,
#             "quantity":10
#          }
#       ],
#       "hats":[

#       ],
#       "tournament":{
#          "registered":false,
#          "current":null
#       },
#       "candidacy":null,
#       "pomps":[

#       ]
#    },
#    "token":"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwOlwvXC9sZWVrd2Fycy5jb20iLCJhdWQiOiJodHRwOlwvXC9sZWVrd2Fycy5jb20iLCJleHAiOjE1OTI2NjQyMDIsImlkIjo2NDU5Nywia2VlcCI6ZmFsc2UsImhhc2giOiIkMnkkMTAkUHkuM1NXRUQ4VUtKMSJ9.u8VKltJVROk_w79ksmwPfXQFY0JhIsOxKmjJcVosNg0"
# }

def setup(bot):
    bot.add_cog(Leekwars(bot))