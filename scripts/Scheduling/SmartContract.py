from base64 import decode
from re import sub
from web3 import Web3
from Utils import loadConfig, getContractAddress
import json, time, copy, glob

config = loadConfig()

class Contract:
    def __init__(self, config):
        self.web3 = Web3(Web3.HTTPProvider(config["ethereum_node_address"]))
        #! Load all Contracts in ABIs except Migrations
        self.contracts={}
        for path in glob.glob(config["contract_ABI"]):
            if (file_name:=path.split("/")[2].split(".")[0])!="Migrations":
                self.contracts[file_name]=self.web3.eth.contract(address=getContractAddress(path), abi=json.load(open(path))["abi"])
        
    def decodeOutput(self, contract, function, value):
        decoded = {}
        outputs = self.function_outputs(contract.abi, function)
        return self.decode(decoded, value, copy.deepcopy(outputs))
    
    def decode(self, dictionary, value, formatOutput, pos=0):
        if(len(value) == pos) or formatOutput==[]:
            return dictionary, pos

        var= formatOutput.pop(0)

        if "name" in var.keys() and "components" not in var.keys():
            if type(value[pos])==tuple:
                if(len(value[pos])==1):
                    dictionary[var["name"]] = value[pos][0]
                    pos+=1
                else:
                    dictionary[var["name"]] = value[pos][0]
                    value=list(value)
                    value[pos]=(value[pos][1:])
                    value = tuple(value)
            else:
                dictionary[var["name"]] = value[pos]
                pos+=1

        if "components" in var.keys():
            if "name" in var.keys() and "[]" not in var["internalType"]:
                subkey=var["name"]
                dictionary[subkey]={}
                newDict , pos  = self.decode(dictionary[subkey], value, var["components"],pos)
            else:
                newDict , pos  = self.decode(dictionary, value, var["components"],pos)
            dictionary | newDict
        newDict , pos = self.decode(dictionary, value, formatOutput, pos)
        return dictionary | newDict , pos
    
    def function_outputs(self, abi, function):
        for fun in abi:
            if fun.get("name",None)==function:
                return fun["outputs"]
    
    def getMakers(self):
        addr,userInfo, makerInfo= self.contracts["User"].functions.getMakersInfo(int(time.time()*1000)).call()
        makers = zip(addr,userInfo,makerInfo)
        makersData = {}
        for i in makers:
            values=(i[0],)+i[1]+i[2]
            maker, _ = self.decodeOutput(self.contracts["User"],"getMakersInfo",values)
            makersData[maker["addr"]]= {"info":maker}
            del makersData[maker["addr"]]["info"]["addr"]
        return makersData
    
    def getPrinters(self,makers):
            
        printers = self.contracts["OnBoarding"].functions.getMakerPrintersBeforeTimestamp(int(time.time()*1000)).call()
        for p in printers:
            p, _ = self.decodeOutput(self.contracts["OnBoarding"],"getMakerPrintersBeforeTimestamp", p)
            makers[p["maker"]]["printers"].append(p["printer"])
        return makers
    
    def getMaterials(self,makers):
        materials = self.contracts["OnBoarding"].functions.getMaterialsBeforeTimestamp(int(time.time()*1000)).call()
        for m in materials:
            m , _ = self.decodeOutput(self.contracts["OnBoarding"],"getMaterialsBeforeTimestamp", m)
            makers[m["maker"]]["materials"].append(m["material"])
        return makers

    def getPlayer(self, address):
        p = self.contracts["User"].functions.getPlayerInfoWithAddress(address).call()
        p, _ = self.decodeOutput(self.contracts["User"],"getPlayerInfoWithAddress", p)
        return p
    
    def getDesign(hash):
        pass
    """          
    enum MaterialColor {
        0 - NONE,      
        1 - BLACK,      
        2 - WHITE, 
        3 - BROWN, 
        4 - GRAY, 
        5 - YELLOW, 
        6 - ORANGE, 
        7 - RED, 
        8 - PINK,
        9 - PURPLE, 
        10 - BLU, 
        11 - GREEN     
    } 
    """
    
def getMakersData():
    Scheduling = Contract(config)

    makers = Scheduling.getMakers()
    for addr in makers.keys():
        makers[addr]["printers"] = []
        makers[addr]["materials"] = []
    print(makers)
    Scheduling.getPrinters(makers)
    Scheduling.getMaterials(makers)
    printMakers(makers)
    return makers

def getPlayer(address):
    Scheduling = Contract(config)
    return Scheduling.getPlayer(address)["airPlayer"]

def getDesign(hash_design):
    Scheduling = Contract(config)
    return Scheduling.getDesign(hash_design)

def printMakers(makers):
    for addr in makers.keys():
        print("\n\n\nmaker: ", addr, "\n-------------\n")
        print("maker's printers:\n")
        for p in makers[addr]["printers"]:
            print(p,"\n+++++++++++++++++++++\n")
        print("maker's materials:\n")
        for m in makers[addr]["materials"]:
            print(m,"\n.-.-.-.-.-.-.-.-.-.-.\n")
        print("##################\n\n")






if __name__ == "__main__":
    getMakersData()
    #print(getPlayer("0x74Aa06fC43dAEAe70e9aADbFaeB8B0EEE2ECfE06"))


