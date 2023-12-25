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
from controllers.db.models import WMFSQLDriver

db_conn = WMFSQLDriver()
devices = db_conn.get_devices()

def updateDrinks(decice_ip):
        try:
            ws = websocket.create_connection(f'ws://{decice_ip}:25000/', timeout=5)
            status = 1
        except Exception:
            return 0
        request_drinks = json.dumps({"function": "getDrinkList"})
        #print(request_drinks)
        ws.send(request_drinks)
        received_drinks = ws.recv()
        received_drinks_deque = deque(json.loads(received_drinks))
        formatted_drinks = {}
        for var_drinks in list(received_drinks_deque):
            for i_drinks in var_drinks:
                formatted_drinks[i_drinks] = var_drinks[i_drinks]
        for drink in formatted_drinks["DrinkList"]:
            #print(drink["Name"])
            columns = {
                "water": {"count": 0, "weight": 0},
                "coffee": {"count": 0, "weight": 0},
                "milk": {"count": 0, "weight": 0},
                "powder": {"count": 0, "weight": 0},
                "foam": {"count": 0, "weight": 0},
            }
            request_recipes = json.dumps({"function": "getRecipeComposition", "RecipeNumber": drink["RecipeNumber"]})
           # print(request_recipes)
            ws.send(request_recipes)
            received_recipes = ws.recv()
            received_recipes_deque = deque(json.loads(received_recipes))
            formatted_recipes = {}
            for var_recipes in list(received_recipes_deque):
                for i_recipes in var_recipes:
                    formatted_recipes[i_recipes] = var_recipes[i_recipes]
            for vat_recipes in formatted_recipes["Parts"]:
                #print(formatted_recipes["Parts"])
                if vat_recipes["Type"] == "coffee":
                    columns["coffee"]["weight"] = int(columns["coffee"]["weight"] + vat_recipes['QtyPowder'])
                    columns["coffee"]["count"] = columns["coffee"]["count"] + 1
                if vat_recipes["Type"] == "coldmilk" or vat_recipes["Type"] == "milk":
                    columns["milk"]["weight"] = int(columns["milk"]["weight"] + vat_recipes['QtyMilk'])
                    columns["milk"]["count"] = columns["milk"]["count"] + 1
                if vat_recipes["Type"] == "milkfoam" or vat_recipes["Type"] == "coldfoam":
                    columns["foam"]["weight"] = int(columns["foam"]["weight"] + vat_recipes['QtyFoam'])
                    columns["foam"]["count"] = columns["foam"]["count"] + 1
                if vat_recipes["Type"] == "hotwater" or vat_recipes["Type"] == "water":
                    columns["water"]["weight"] = int(columns["water"]["weight"] + vat_recipes['QtyWater'])
                    columns["water"]["count"] = columns["water"]["count"] + 1
            available_recipe = db_conn.getRecipe(device[1], drink["RecipeNumber"])
            #print(available_recipe)
            if available_recipe is None:
                db_conn.initRecipe(device[1], drink["RecipeNumber"], drink["Name"], received_recipes, columns["coffee"]["count"], columns["coffee"]["weight"],columns["water"]["count"],columns["water"]["weight"],columns["milk"]["count"],columns["milk"]["weight"],columns["powder"]["count"],columns["powder"]["weight"],columns["foam"]["count"],columns["foam"]["weight"])
            else:
                if received_recipes != available_recipe[4]:
                    if available_recipe[2] == drink["RecipeNumber"] and available_recipe[3] == drink["Name"] and available_recipe[5] == columns["coffee"]["count"] and available_recipe[6] == columns["coffee"]["weight"] and available_recipe[7] == columns["water"]["count"] and available_recipe[8] == columns["water"]["weight"] and available_recipe[9] == columns["milk"]["count"] and available_recipe[10] == columns["milk"]["weight"] and available_recipe[11] == columns["powder"]["count"] and available_recipe[12] == columns["powder"]["weight"] and available_recipe[13] == columns["foam"]["count"] and available_recipe[14] == columns["foam"]["weight"]:
                        db_conn.updateRecipe(device[1], drink["RecipeNumber"], drink["Name"], received_recipes, columns["coffee"]["count"], columns["coffee"]["weight"],columns["water"]["count"],columns["water"]["weight"],columns["milk"]["count"],columns["milk"]["weight"],columns["powder"]["count"],columns["powder"]["weight"],columns["foam"]["count"],columns["foam"]["weight"])
                        return True
                    else:
                        edited = {"device": device[1], "recipe_id": available_recipe[2], "edited_parts": {}}
                        if str(available_recipe[3]) != str(drink["Name"]):
                            edited["edited_parts"]["recipe_alias"] = {"been": available_recipe[3], "now": drink["Name"]}
                        if int(available_recipe[5]) != int(columns["coffee"]["count"]):
                            edited["edited_parts"]["coffee_count"] = {"been": available_recipe[5], "now": columns["coffee"]["count"]}
                        if int(available_recipe[6]) != int(columns["coffee"]["weight"]):
                            edited["edited_parts"]["coffee_weight"] = {"been": available_recipe[6], "now": columns["coffee"]["weight"]}
                        if int(available_recipe[7]) != int(columns["water"]["count"]):
                            edited["edited_parts"]["water_count"] = {"been": available_recipe[7], "now": columns["water"]["count"]}
                        if int(available_recipe[8]) != int(columns["water"]["weight"]):
                            edited["edited_parts"]["water_weight"] = {"been": available_recipe[8], "now": columns["water"]["weight"]}
                        if int(available_recipe[9]) != int(columns["milk"]["count"]):
                            edited["edited_parts"]["milk_count"] = {"been": available_recipe[9], "now": columns["milk"]["count"]}
                        if int(available_recipe[10]) != int(columns["milk"]["weight"]):
                            edited["edited_parts"]["milk_weight"] = {"been": available_recipe[10], "now": columns["milk"]["weight"]}
                        if int(available_recipe[11]) != int(columns["powder"]["count"]):
                            edited["edited_parts"]["powder_count"] = {"been": available_recipe[11], "now": columns["powder"]["count"]}
                        if int(available_recipe[12]) != int(columns["powder"]["weight"]):
                            edited["edited_parts"]["powder_weight"] = {"been": available_recipe[12], "now": columns["powder"]["weight"]}
                        if int(available_recipe[13]) != int(columns["foam"]["count"]):
                            edited["edited_parts"]["foam_count"] = {"been": available_recipe[13], "now": columns["foam"]["count"]}
                        if int(available_recipe[14]) != int(columns["foam"]["weight"]):
                            edited["edited_parts"]["foam_weight"] = {"been": available_recipe[14], "now": columns["foam"]["weight"]}
                        db_conn.updateRecipe(device[1], drink["RecipeNumber"], drink["Name"], received_recipes, columns["coffee"]["count"], columns["coffee"]["weight"],columns["water"]["count"],columns["water"]["weight"],columns["milk"]["count"],columns["milk"]["weight"],columns["powder"]["count"],columns["powder"]["weight"],columns["foam"]["count"],columns["foam"]["weight"])
                        url = "https://backend.wmf24.ru/api/recipe_edited"

                        headers = {
                            'Content-Type': 'application/json',
                            'Serverkey': db_conn.get_encrpt_key()[0]
                        }
                        response = requests.request("POST", url, headers=headers, data=json.dumps(edited))
                        db_conn.create_error_record(device[1], '-2')
                        db_conn.close_error_code(device[1], '-2')
                        print(edited)
        #print(columns)


for device in devices:
    updateDrinks(device[2])
