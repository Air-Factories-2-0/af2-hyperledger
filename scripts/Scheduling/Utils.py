
import json, base58


def loadConfig(file="config.json"):
    return json.load(open(file))

def setConfig(config,key,value):
    config[key]=value
    json.dump(config, open("config.json","w"))
    
def getContractAddress(path):
    f = json.load(open(path))
    return f["networks"][list(f["networks"])[-1]]["address"]


def hash_to_bytes32(hash_string):
    b58val=base58.b58decode(hash_string)
    #salvo i 2 bytes
    remby = b58val[:2]
    b58val=b58val[2:]
    res=b58val.hex()
    return remby,res

def bytes32_to_hash(firsttwo,bytehash):
    
    begin=list(firsttwo)
    byteshash=list(bytehash)
    res=begin+byteshash
    res=bytes(res)
    res=base58.b58encode(res)
    return res

