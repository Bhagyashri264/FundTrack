import pymongo
client= pymongo.MongoClient("mongodb://Admin:root@localhost:27017/")
mydb = client["fundtracker"]
users = mydb["users"]
tran = mydb["transaction"]