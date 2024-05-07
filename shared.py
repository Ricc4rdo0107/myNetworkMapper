import json

def getJsonData(filename="common_ports.json"):
    return json.load(open(filename, "r"))