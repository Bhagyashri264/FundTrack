import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4
import pymongo

class Block:
    def toJSON(self):
        return json.dumps(self,default=lambda o: o.__dict__,sort_keys=True,indent=4)

    def __init__(self) -> None:
        self.sender_id = None
        self.receiver_id = None
        self.amount = None
        self.desp = None
        self.time = None
        self.tags = None
        self.prev_hash = None

class Blockchain:
    def __init__(self) -> None:
        self.client= pymongo.MongoClient("mongodb://Admin:root@localhost:27017/")
        self.mydb = self.client["fundtracker"]
        self.transactions = self.mydb["transaction"]

    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def create_genesis_block(self,block_obj):
        block_obj.prev_hash = "-1"
        data_dict = block_obj.__dict__
        res = self.transactions.insert_one(data_dict)
        return "success"
    
    def add_transaction(self,block_obj,tag):
        blocks=[]
        for block in self.transactions.find({"tags":{"$in":tag}}).sort("time"):
            block["id"]=str(block["_id"])
            del block["_id"]
            blocks.append(block)
        print(blocks)
        prev_hash=blocks[-1]["prev_hash"]
        block_obj.prev_hash=prev_hash
        block_obj.prev_hash = self.hash(block_obj.toJSON())
        data_dict = block_obj.__dict__
        res = self.transactions.insert_one(data_dict)
        return "success"
        
        