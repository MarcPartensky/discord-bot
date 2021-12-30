from .credentials import mongo_url, wolfram_alpha_id
from utils import access, check

import itertools

from pymongo import MongoClient
import pymongo
import os
import wolframalpha

from models.mongo import MongoCluster


cluster = MongoCluster(mongo_url)
db = cluster.esclave

link = "https://discordapp.com/oauth2/authorize?&client_id=703347349623144549&scope=bot&permissions=8"
prefix = os.environ.get("DISCORD_PREFIX") or "."
masters = [478552571510915072]  # , 219949869220102147]
wolfram = wolframalpha.Client(wolfram_alpha_id)
ialab_bot_url = "https://ialab.marcpartensky.com"

roles = ["@Maître", "@Admin"]

delete_after_time = 10
status = itertools.cycle(
    [
        "ajoute-moi à ton serv " + link,
        "développer la science infuse",
        "évoluer au delà de l'espèce humaine",
        "comploter contre l'humanité",
        "finaliser la théorie quantique",
    ]
)
access = access.Access(masters)  # Create access for commands
check = check.Check()
