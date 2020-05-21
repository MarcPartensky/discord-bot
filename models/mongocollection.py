from config.config import cluster

class MongoCollection:
    currentDate = "$currentDate"
    inc = "$inc"
    min = "$min"
    max = "$max"
    mul = "$mul"
    rename = "$rename"
    set = "$set"
    setOnInsert = "$setOnInsert"
    unsert = "$unset"

    def __init__(self, name):
        """Abstraction over mongodb collection."""
        self.collection = cluster[name]

    def __str__(self):
        """Return the name of the collection."""
        return self.collection.name

    def __len__(self):
        """Return the number of posts."""
        return self.count({})

    def increment_one(self, conditions:dict, values:dict):
        """Increment the value of the first post meeting conditions."""
        self.collection.update_one(conditions, {MongoCollection.set:values})

    def insert_one(self, post:dict, id:int=None):
        """Insert a post with key and value."""
        if id and '_id' not in post:
            post['_id'] = id
        self.collection.insert_one(post)

    def insert_many(self, posts:list):
        """Insert many posts with key and value."""
        self.collection.insert_many(posts)

    def update_one(self, conditions:dict, values:dict):
        """Insert a post with key and value."""
        self.collection.update_one(conditions, values)

    def update_many(self, conditions:dict, values:dict):
        """Insert many posts with key and value."""
        self.collection.update_many(conditions, values)

    def find(self, conditions:dict):
        """Find a list of posts meeting conditions."""
        return list(self.collection.find(conditions))

    def find_one(self, conditions:dict):
        """Find a list of posts meeting conditions."""
        return self.collection.find(conditions)

    def delete_one(self, conditions:dict):
        """Delete the first post meeting conditions."""
        self.collection.delete_one(conditions)

    def delete_many(self, conditions:dict):
        """Delete many posts meeting conditions."""
        self.collection.delete_many(conditions)

    def __getattribute__(self, id):
        """Return a post of the collection using its id."""
        return self.find({'_id':id})

    def __setattr__(self, id, value:dict):
        """Create or modify a post."""
        pass

    def __contains__(self, id):
        """Determine if a collection contains an id."""
        


    def count(self, conditions:dict):
        """Count the number of post meeting conditions."""
        return self.collection.count_documents(conditions)
        
if __name__ == "__main__":
    from pymongo import MongoClient
    mongo_url = "mongodb+srv://<username>:<password>@discord-cluster-5ckni.mongodb.net/test"
    mongo_password = "esclave"
    mongo_username = "esclave"
    mongo_url = mongo_url.replace('<username>', mongo_username)
    mongo_url = mongo_url.replace('<password>', mongo_password)
    cluster = MongoClient(mongo_url)
    c = MongoCollection('test')
    print(len(c))


