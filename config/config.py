import os
import itertools
import wolframalpha

from utils.access import Access
from utils.check import Check
from models.mongo import MongoCluster
from .credentials import mongo_url, wolfram_alpha_id


cluster = MongoCluster(mongo_url)
db = cluster.esclave

link = "https://discordapp.com/oauth2/authorize?&client_id=703347349623144549&scope=bot&permissions=8"
prefix = os.environ.get("DISCORD_PREFIX") or "."
masters = [478552571510915072]  # , 219949869220102147]
wolfram = wolframalpha.Client(wolfram_alpha_id)

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
access = Access(masters)  # Create access for commands
check = Check()
