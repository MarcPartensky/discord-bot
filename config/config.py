from utils import access
import itertools

from .credentials import mongo_url
from pymongo import MongoClient
import pymongo

cluster = MongoClient(mongo_url)

prefixes = ["esclave", "."]
# masters = ["Marc Partensky#5983"]#, "Mazex#3106"]
masters = [478552571510915072]#, 219949869220102147]

roles = ["@Maître", "@Admin"]
# bots = ["@Dank Memer#5192"]

delete_after_time = 10
status = itertools.cycle(["développer la science infuse", "évoluer au delà de l'espèce humaine", "comploter contre l'humanité", "finaliser la théorie quantique"])
access = access.Access(masters) #Create access for commands