import json
import websocket
import sys
sys.path.append("../../")

def getRecipeComposition(device_ip, recipe_number):
    WS_IP = f'ws://{device_ip}:25000/'
    ws = websocket.create_connection(WS_IP, timeout=5)
    request = (json.dumps({"function": "getRecipeComposition", "RecipeNumber": recipe_number}))
    ws.send(request)
    received_data = ws.recv()
    return received_data