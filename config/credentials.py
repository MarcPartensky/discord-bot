token = "Your token"
client_id = "Your id (integer)"
mongo_url = "mongodb+srv://<username>:<password><your mongo cluseter>/test"
mongo_password = "mongo_password"
mongo_username = "mongo_username"
mongo_url = mongo_url.replace('<username>', mongo_username)
mongo_url = mongo_url.replace('<password>', mongo_password)
# mongo_url = mongo_url.replace('mongodb+srv://', 'mongodb://')

# https://discordapp.com/oauth2/authorize?&client_id=703347349623144549&scope=bot&permissions=8
