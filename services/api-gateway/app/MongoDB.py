import pymongo

from config import *


class MongoDB:
    RECIPE_COLLECTION = None

    def __init__(self):
        if MONGO_URL is None:
            MongoDB.initialize_mongo()

    @staticmethod
    def initialize_mongo():
        client = pymongo.MongoClient(MONGO_URL)
        db = client['recipe_db']
        MongoDB.RECIPE_COLLECTION = db['recipes']
