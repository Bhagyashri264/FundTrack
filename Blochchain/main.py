from fastapi import FastAPI
from schemas import block_struct
from Blockchain import Block,Blockchain
import datetime


app = FastAPI()

@app.post("/create_genesis_block")
def create_genesis_block(request:block_struct):
    Block_obj = Block()
    Block_obj.sender_id = request.sender_id
    Block_obj.receiver_id = request.receiver_id
    Block_obj.amount = request.amount
    Block_obj.desp = request.desp
    Block_obj.tags = request.tags
    Block_obj.time = str(datetime.datetime.now())
    obj = Blockchain()
    res = obj.create_genesis_block(Block_obj)
    return res

@app.post("/add_transaction")
def Add_transaction(request:block_struct):
    Block_obj = Block()
    Block_obj.sender_id = request.sender_id
    Block_obj.receiver_id = request.receiver_id
    Block_obj.amount = request.amount
    Block_obj.desp = request.desp
    Block_obj.tags = request.tags
    Block_obj.time = str(datetime.datetime.now())
    obj = Blockchain()
    res = obj.add_transaction(Block_obj,request.tags)
    return {"body":res}