from cmath import inf
import operator, sys
from SmartContract import getMakersData, printMakers, getPlayer, getDesign

from math import sin, cos, sqrt, atan2, radians


def pointDistanceKM(point1, point2):
    R = 6373.0
    
    lat1 = radians(point1["latitude"])
    lon1 = radians(point1["longitude"])
    
    lat2 = radians(point2["latitude"])
    lon2 = radians(point2["longitude"])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R*c

def canPrint(nozzle,quality):
    pass

def min_max_normalization(dictionary):
    maxValue = max(dictionary.values())
    minValue = min(dictionary.values())
    for k in list(dictionary.keys()):
        dictionary[k] = 1 - ((dictionary[k] - minValue) / maxValue-minValue)

def chooseMakers(makers, order, design, player):
    
    for addr in list(makers.keys()):
        info = makers[addr]["info"]

        makers[addr]["info"]["max_printable"] = 0
        makers[addr]["info"]["distance"] = inf

        #!Check valid printers
        for p in makers[addr]["printers"]:

            if p["volume"]<design["volume"]:
                makers[addr]["printers"].remove(p)
                continue
            
            if order["material"] not in p["supportedMaterial"]:
                makers[addr]["printers"].remove(p)
                continue 
            
            valid_nozzle = False
            for n in p["nozzles"]:
                if n == order["request_quality"]:
                    valid_nozzle = True
                    
            if order["better_quality"]:
                for n in p["nozzles"]:
                    if n < order["request_quality"]:
                        valid_nozzle = True
                        
            if not valid_nozzle: makers[addr]["printers"].remove(p)

        if len(makers[addr]["printers"]) == 0:
            makers.pop(addr, None)
            continue
        
        #!Check Materials
        materialQuantity = 0
        for m in makers[addr]["materials"]:
            if m["color"] != order["color"]:
                makers[addr]["materials"].remove(m)
                
            if m["mType"] != order["material"]:
                makers[addr]["materials"].remove(m)
                
            materialQuantity += int(m["quantityKG"])
            
        makers[addr]["info"]["max_printable"] = int(materialQuantity//design["quantity"])
                
        if  makers[addr]["info"]["max_printable"]==0:
            makers.pop(addr, None)
            continue
        
        #!check position
        for i in range(50,600,50):
            dist = pointDistanceKM(info["position"],player["position"])
            if dist<i:
                makers[addr]["info"]["distance"] = dist
                break;
        
        if makers[addr]["info"]["distance"]==inf:
            makers.pop(addr, None)
            continue
        
    return makers

def priorityList(makers, order):
    partecipanti = {}
    distance = {}
    reputation = {}

    for addr in makers.keys():
        partecipanti[addr] = {}
        distance[addr] = float(makers[addr]["info"]["distance"])
        reputation[addr] = float(makers[addr]["info"]["reputation"])

        for p in makers[addr]["printers"]:
            partecipanti[addr][p["printerAddress"]]["pieces"]=0

    #!Normalize distance and reputation point
    distance = min_max_normalization(distance)
    reputation = min_max_normalization(reputation)

    for addr in list(makers.keys()):
        info = makers[addr]["info"]
        for p in makers[addr]["printers"]:

            partecipanti[addr][p["printerAddress"]]["pieces"]= partecipanti[addr][p["printerAddress"]]["pieces"]+distance[addr]*2
            partecipanti[addr][p["printerAddress"]]["pieces"]= partecipanti[addr][p["printerAddress"]]["pieces"]+reputation[addr]*2

            if info["avaiableToPrint"]: partecipanti[addr][p["printerAddress"]]["pieces"]= partecipanti[addr][p["printerAddress"]]["pieces"]+2

            if info["avaiabilityRangeFrom"] < order["request_time"] < info["avaiabilityRangeTo"]:
                partecipanti[addr][p["printerAddress"]]["pieces"] = partecipanti[addr][p["printerAddress"]]["pieces"]+1

            if p["mountedMaterial"]["color"] == order["color"] and p["mountedMaterial"]["mType"] == order["type"]:
                partecipanti[addr][p["printerAddress"]]["pieces"] = partecipanti[addr][p["printerAddress"]]["pieces"]+1


            if canPrint(p["mountedNozzles"], order["requested_quality"]):
                partecipanti[addr][p["printerAddress"]]["pieces"] = partecipanti[addr][p["printerAddress"]]["pieces"]+2
    return partecipanti

def repartition(makers,partecipanti, npezzi):
    '''
        @input partecipanti = dict -> { maker : priorità }
        @input npezzi = int -> numero totale di pezzi da stampare
        @return distribuzione = dict -> { maker : pezziAssegnati }
    '''
    distribuzione = {}
    #Se il numero di pezzi è 1 allora si assegna al maker con il punteggio più alto nella 
    #graduatoria
    if npezzi==1:
        primoMaker = max(partecipanti, key=partecipanti.get)
        return { primoMaker : 1 }
    #Se il numero di pezzi è inferiore al numero di partecipanti effettuo la norma min-max
    #per escludere gli ultimi nella graduatoria.
    if npezzi < len(partecipanti):
        minValue = min(list(partecipanti.values()))
        for key, value in partecipanti.items():
            partecipanti[key] = (value - minValue ) / (10 - minValue)

    #Effettuo una ripartizione semplice diretta
    sommaVoti = sum(list(partecipanti.values()))
    np = len(partecipanti)
    pezziRimanenti = npezzi #Pezzi in avanzo dopo la distribuzione

    for key, value in partecipanti.items():
        pezziAssegnati = round((npezzi * value) / sommaVoti)
    #Se il numero dei pezziAssegnati > pezziStampabili (Da definire il valore) allora il 
        #numero dei pezziAssegnati sarà uguale al numero di pezziStampabili
        if pezziAssegnati > makers[key]["info"]["max_printable"]:
            pezziAssegnati = makers[key]["info"]["max_printable"]
        #Se il numero di pezzi rimanenti è 0 o il numero di pezzi assegnati è maggiore
        #del numero di pezzi rimanenti allora assegno solo i pezzi rimanenti
        if pezziRimanenti <= 0 or pezziAssegnati > pezziRimanenti:
            distribuzione[key] = pezziRimanenti
            break
        distribuzione[key] = pezziAssegnati
        pezziRimanenti -= pezziAssegnati

    #Se ci sono pezzi rimanenti li assegno al maker con la priorità più alta
    if pezziRimanenti > 0:
        primoMaker = max(partecipanti, key=partecipanti.get)
        distribuzione[primoMaker] += pezziRimanenti
    return distribuzione

def formatResponse(dictionary = {}):
    '''
    dictionary = {
        "addr1" : {
            "printer1" : 1,
        },
        "addr2" : {
            "printer1" : 3,
            "printer2" : 4,
            "printer3" : 4,
        },
        "addr5" : {
            "printer1" : 3,
            "printer2" : 4,
        }
    }
    '''
    makers = []
    printers = []
    pieces = []
    for k in dictionary:
        for p in dictionary[k].keys():
            makers.append(k)
            printers.append(p)
            pieces.append(dictionary[k][p])
    
    print(makers,",",printers,",",pieces)


def scheduler(order):
    player = getPlayer(order["caller"])
    #design = getDesign(order["hash_design"])
    design = {
        "volume" : 101,
        "quantity" : 3
    }
    makers = getMakersData()
    choosen = chooseMakers(makers, order, design, player)
    priority = priorityList(choosen, order)
    partition = repartition(makers,priority, order["pieces"])
    formatResponse(partition)

if __name__=="__main__":
    order = dict([arg.split('=', maxsplit=1) for arg in sys.argv[1:]])
    order["pieces"] = int(order["pieces"])
    order["color"] = int(order["color"])
    order["material"] = int(order["material"])
    order["requested_quality"] = int(order["requested_quality"])
    order["better_quality"]= int(order["better_quality"])
    order["timestamp_request"] = int(order["timestamp_request"])

    scheduler(order)

    '''
    order = {
        "orderID" : "id",
        "hash_design": "cid",
        "caller": "0x74Aa06fC43dAEAe70e9aADbFaeB8B0EEE2ECfE06",
        "pieces" :"int",
        "color": "1",
        "material":"1",
        "requested_quality":"",
        "better_quality":True
    }
    '''