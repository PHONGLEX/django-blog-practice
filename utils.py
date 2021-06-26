import json

import pymongo
from pymongo import MongoClient
client = pymongo.MongoClient('mongodb://localhost:27017/')


def insert_mongo(db, collection):
    def wrapper(fnc):
        def inner(request, *args, **kwargs):
            data = json.dumps(request.POST)
            _db = client[db]
            collection_name = _db[collection]
            collection_name.insert_one(json.loads(data))
            return fnc(request, *args, **kwargs)
        return inner
    return wrapper
        
