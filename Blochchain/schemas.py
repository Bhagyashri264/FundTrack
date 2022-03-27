from typing import List
from pydantic import BaseModel

class block_struct(BaseModel):
    sender_id:str
    receiver_id:str
    amount:int
    desp:str
    tags:List[str]

class otp_struct(BaseModel):
    otp:int
    email:str