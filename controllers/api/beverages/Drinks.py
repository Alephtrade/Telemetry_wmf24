import sys
import websocket
import logging
import requests
import json
import time
from collections import deque
import ast
import socket
import sys
sys.path.append('./')
sys.path.append('/var/www/Telemetry_wmf24/')
from controllers.core.utils import initialize_logger, print_exception
from controllers.wmf.models import WMFMachineErrorConnector
from controllers.settings import prod as settings
from controllers.db.models import WMFSQLDriver

db_conn = WMFSQLDriver()
devices = db_conn.get_devices()

def updateDrinks():
    for device in devices:
        try:
            ws = websocket.create_connection(f'ws://{device[2]}:25000/', timeout=5)
            status = 1
        except Exception:
            return False
        request_drinks = json.dumps({"function": "getDrinkList"})
        print(request_drinks)
        ws.send(request_drinks)
        received_drinks = ws.recv()
        received_drinks_deque = deque(json.loads(received_drinks))
        formatted_drinks = {}
        for var_drinks in list(received_drinks_deque):
            for i_drinks in var_drinks:
                formatted_drinks[i_drinks] = var_drinks[i_drinks]
        for drink in formatted_drinks["DrinkList"]:
            print(drink["Name"])
            available_recipe = db_conn.getRecipe(device[2], drink["RecipeNumber"])
            print(available_recipe)
            if available_recipe is None:
                columns = {
                    "water": {"count": 0, "weight": 0},
                    "coffee": {"count": 0, "weight": 0},
                    "milk": {"count": 0, "weight": 0},
                    "powder": {"count": 0, "weight": 0},
                    "foam": {"count": 0, "weight": 0},
                }
                request_recipes = json.dumps({"function": "getRecipeComposition", "RecipeNumber": drink["RecipeNumber"]})
                print(request_recipes)
                ws.send(request_recipes)
                received_recipes = ws.recv()
                received_recipes_deque = deque(json.loads(received_recipes))
                formatted_recipes = {}
                for var_recipes in list(received_recipes_deque):
                    for i_recipes in var_recipes:
                        formatted_recipes[i_recipes] = var_recipes[i_recipes]
                for vat_recipes in formatted_recipes["Parts"]:
                    print(formatted_recipes["Parts"])
                    if vat_recipes["Type"] == "coffee":
                        columns["coffee"]["weight"] = columns["coffee"]["weight"] + vat_recipes['QtyPowder']
                        columns["coffee"]["count"] = columns["coffee"]["count"] + 1
                    if vat_recipes["Type"] == "coldmilk" or vat_recipes["Type"] == "milk":
                        columns["milk"]["weight"] = columns["milk"]["weight"] + vat_recipes['QtyMilk']
                        columns["milk"]["count"] = columns["milk"]["count"] + 1
                    if vat_recipes["Type"] == "milkfoam" or vat_recipes["Type"] == "coldfoam":
                        columns["foam"]["weight"] = columns["foam"]["weight"] + vat_recipes['QtyFoam']
                        columns["foam"]["count"] = columns["foam"]["count"] + 1
                    if vat_recipes["Type"] == "hotwater" or vat_recipes["Type"] == "water":
                        columns["water"]["weight"] = columns["water"]["weight"] + vat_recipes['QtyWater']
                        columns["water"]["count"] = columns["water"]["count"] + 1
            db_conn.initRecipe(device[1], drink["RecipeNumber"], columns["coffee"]["count"], columns["coffee"]["weight"],columns["water"]["count"],columns["water"]["weight"],columns["milk"]["count"],columns["milk"]["weight"],columns["powder"]["count"],columns["powder"]["weight"],columns["foam"]["count"],columns["foam"]["weight"])
        print(columns)



updateDrinks()