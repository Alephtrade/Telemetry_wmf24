import json
import logging
import websocket
import requests
from core.utils import initialize_logger
from settings import prod as settings

def getServiceStatistics():
    WMF_URL = settings.WMF_DATA_URL
    WS_URL = settings.WS_URL
    DEFAULT_WMF_PARAMS = settings.DEFAULT_WMF_PARAMS
    WMF_URL = settings.WMF_DATA_URL
    DEFAULT_WMF_PARAMS = settings.DEFAULT_WMF_PARAMS
    initialize_logger('response.txt')
    ws = websocket.create_connection(WS_URL)
    request = json.dumps({'function': 'getServiceStatistics'})
    logging.info(f"COFFEE_MACHINE: Sending {request}")
    ws.send(request)
    received_data = ws.recv()
    logging.info(f"COFFEE_MACHINE: Received {received_data}")
    text_file = open("response.txt", "a")
    text_file.write(received_data)
    #r = requests.post('https://wmf24.ru/api/servicestatistics', json=received_data)
    url = "https://wmf24.ru/api/servicestatistics"
    payload = json.dumps([
        {
            "function": "getServiceStatistics"
        },
        {
            "device_id": 111
        },
        {
            "returnvalue": 0
        },
        {
            "TotalCyclesBrewer1": 225367
        },
        {
            "ExchangeBrewer1": 0
        },
        {
            "TotalCyclesBrewer2": -1
        },
        {
            "ExchangeBrewer2": 0
        },
        {
            "TotalCyclesMixer1": -1
        },
        {
            "TotalCyclesMixer2": -1
        },
        {
            "BrewingsSinceCustomerMaintainance": 11667
        },
        {
            "BrewingsSinceMaintainance1": 40127
        },
        {
            "BrewingsSinceMaintainance2": 59079
        },
        {
            "BrewingsSinceDriveExchange": 225367
        },
        {
            "BrewingsSinceRevision": -1
        },
        {
            "TotalOfHotWaterDosages": 77004
        },
        {
            "TotalSteamDosages": 506334
        },
        {
            "TotalChocDosages": -1
        },
        {
            "TotalWaterBoilerSupply": 18867
        },
        {
            "TotalSteamBoilerSupply": 0
        },
        {
            "TotalWaterBoilerSupplySinceDescaling": -1
        },
        {
            "TotalFlowTypeHeaterSupplySinceDescaling": -1
        },
        {
            "NumberOfCleanings": 4
        },
        {
            "NumberOfCleaningsToDo": 5
        },
        {
            "NumberOfMixerCleanings": 0
        },
        {
            "NumberOfMilkCleanings": 4
        },
        {
            "NumberOfDescalings": 0
        },
        {
            "ScoopGrindingDisc1": 230927
        },
        {
            "ScoopGrinder1": 230927
        },
        {
            "ScoopGrindingDisc2": -1
        },
        {
            "ScoopGrinder2": -1
        },
        {
            "ScoopGrindingDisc3": -1
        },
        {
            "ScoopGrinder3": -1
        },
        {
            "ScoopGrindingDisc4": -1
        },
        {
            "ScoopGrinder4": -1
        },
        {
            "ScoopPowder1": -1
        },
        {
            "ScoopPowder2": -1
        }
    ])
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    logging.info(f"WMFMachineStatConnector: GET response: {response.text}")
    ws.close()
    return True

#def recipes():
#    WMF_URL = settings.WMF_DATA_URL
#    WS_URL = settings.WS_URL
#    DEFAULT_WMF_PARAMS = settings.DEFAULT_WMF_PARAMS
#    WMF_URL = settings.WMF_DATA_URL
#    DEFAULT_WMF_PARAMS = settings.DEFAULT_WMF_PARAMS
#    initialize_logger('response.txt')
#    ws = websocket.create_connection(WS_URL)
#    request = json.dumps({'function': 'getDrinkList'})
#    logging.info(f"COFFEE_MACHINE: Sending {request}")
#    ws.send(request)
#    received_data = ws.recv()
#    logging.info(f"COFFEE_MACHINE: Received {received_data}")
#    text_file = open("response.txt", "a")
#    text_file.write(received_data)
#    request = json.dumps({'function': 'getRecipeComposition'})
#    logging.info(f"COFFEE_MACHINE: Sending {request}")
#    ws.send(request)
#    received_data = ws.recv()
#    logging.info(f"COFFEE_MACHINE: Received {received_data}")
#    text_file = open("response.txt", "a")
#    text_file.write(received_data)
#    request = json.dumps({'function': 'RecipeNumber'})
#    logging.info(f"COFFEE_MACHINE: Sending {request}")
#    ws.send(request)
#    received_data = ws.recv()
#    logging.info(f"COFFEE_MACHINE: Received {received_data}")
#    text_file = open("response.txt", "a")
#    text_file.write(received_data)
#    request = json.dumps({'function': 'RecipeBaseNumber'})
#    logging.info(f"COFFEE_MACHINE: Sending {request}")
#    ws.send(request)
#    received_data = ws.recv()
#    logging.info(f"COFFEE_MACHINE: Received {received_data}")
#    text_file = open("response.txt", "a")
#    text_file.write(received_data)
#    ws.close()
#    return True

#def getbeveragestatistics():
#    WMF_URL = settings.WMF_DATA_URL
#    WS_URL = settings.WS_URL
#    DEFAULT_WMF_PARAMS = settings.DEFAULT_WMF_PARAMS
#    WMF_URL = settings.WMF_DATA_URL
#    DEFAULT_WMF_PARAMS = settings.DEFAULT_WMF_PARAMS
#    initialize_logger('response.txt')
#    ws = websocket.create_connection(WS_URL)
#    request = json.dumps({'function': 'getBeverageStatistics'})
#    logging.info(f"COFFEE_MACHINE: Sending {request}")
#    ws.send(request)
#    received_data = ws.recv()
#    logging.info(f"COFFEE_MACHINE: Received {received_data}")
#    text_file = open("response.txt", "a")
#    text_file.write(received_data)
#    ws.close()
#    return True

