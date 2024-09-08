import os

token = os.environ["DISCORD_TOKEN"]
client_id = os.environ["DISCORD_CLIENT_ID"]

mongo_username = os.environ["DISCORD_MONGO_USERNAME"]
mongo_password = os.environ["DISCORD_MONGO_PASSWORD"]
mongo_cluster = os.environ["DISCORD_MONGO_CLUSTER"]
wolfram_alpha_id = os.environ["WOLFRAM_ALPHA_ID"]

mongo_url = f"mongodb+srv://{mongo_username}:{mongo_password}@{mongo_cluster}"
