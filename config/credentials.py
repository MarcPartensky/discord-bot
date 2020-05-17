# token = "NzAzMzQ3MzQ5NjIzMTQ0NTQ5.Xrwq_Q.dinlotDWkH9vBxAkD65lkeqm7Z8" #production
import os
print(os.environ)
token = os.environ['DISCORD_TOKEN']
client_id = os.environ['DISCORD_CLIENT_ID']

# token = "NzEwODYzNDIzMzA2NTk2MzU0.Xr6qpA.rCYXHsDmGf6rVgz2bQ0yV9oIlO0"
# client_id = 703347349623144549 #production
# client_id = 710863423306596354
# mongo_url = "mongodb+srv://esclave:marcgptl44@discord-cluster-5ckni.mongodb.net/test"

# mongo_password = "esclave"
# mongo_username = "esclave"


mongo_username = os.environ['DISCORD_MONGO_USERNAME']
mongo_password = os.environ['DISCORD_MONGO_PASSWORD']
mongo_cluster = os.environ['DISCORD_MONGO_CLUSTER']

mongo_url = "mongodb+srv://<username>:<password>@<cluster>"
mongo_url = mongo_url.replace('<username>', mongo_username)
mongo_url = mongo_url.replace('<password>', mongo_password)
mongo_url = mongo_url.replace('<cluster>', mongo_cluster)
# mongo_url = mongo_url.replace('mongodb+srv://', 'mongodb://')

# https://discordapp.com/oauth2/authorize?&client_id=703347349623144549&scope=bot&permissions=8
