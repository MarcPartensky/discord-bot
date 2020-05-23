from .credentials import mongo_url
from utils import access, check, shop

import itertools

from pymongo import MongoClient
import pymongo
import os

from models.mongo import MongoCluster

cluster = MongoCluster(mongo_url)
db = cluster.esclave

link = "https://discordapp.com/oauth2/authorize?&client_id=703347349623144549&scope=bot&permissions=8"
prefix = os.environ['DISCORD_PREFIX']
masters = [478552571510915072]#, 219949869220102147]

roles = ["@Maître", "@Admin"]

delete_after_time = 10
status = itertools.cycle(["développer la science infuse", "évoluer au delà de l'espèce humaine", "comploter contre l'humanité", "finaliser la théorie quantique"])
access = access.Access(masters) #Create access for commands
check = check.Check()
shop = shop.Shop(masters, cluster)