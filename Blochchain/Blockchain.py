import hashlib
import os
class Block():
    
    def __init__(self,sender,receiver,amount,desc,prev_hash) -> None:
        self._sender=sender
        self._receiver=receiver
        self._amount=amount
        self._desc=desc
        self._prev_hash=prev_hash
    
    def return_hsah(self):
        hash_string=self._sender+"-"+self._receiver+"-"+str(self._amount)+"-"+self._desc+"-"+self._prev_hash
        return hashlib.sha256(hash_string.encode()).hexdigest()

obj=Block("rushi","bhagya",100,"something","dsh4rjf8476r7")
print(obj.return_hsah())

class Blockchain():
    pass