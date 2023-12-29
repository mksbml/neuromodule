
from pkg.elevation.elevation import haversine
from repository.item_impl import get_items, write_item, remove_item
from pkg.config.config import EXCHANGE_RATE
import logging
from service.models import createModel
from pkg.cache import *

tractor_jsons = {}
harvester_jsons = {}
categorized_tractors = [[], [], [], [], []]
categorized_harvesters = [[], [], [], []]


tractor_section = ["Тракторы"]

harvester_section = ["Комбайны"]


def is_tractor(section):
    return section in tractor_section

def is_harvester(section):
    return section in harvester_section


def calculate_tyagovoe(power):
    if 8.7 <= power < 90:
        return 0
    elif 90 <= power < 100:
        return 1
    elif 100 <= power < 156:
        return 2
    elif 156 <= power <= 219:
        return 3
    elif power > 219:
        return 4


def addtractorToCashe(data):
    tractor_id = data["ID"]
    try:
        try:
            power = int(data["Мощность двигателя, кВт"])
        except:
            power = int(data["Мощность двигателя, л.с."])/1.36
        currency = data["Валюта"]
        if currency in EXCHANGE_RATE:
            data["Цена"] = float(data["Цена"]) * EXCHANGE_RATE[currency]
        else:
            print(currency)
        tyagovoe_type = calculate_tyagovoe(power)
        categorized_tractors[tyagovoe_type].append(tractor_id)
        tractor_jsons[tractor_id] = data
    except: pass


harvester_categories = {"Зерноуборочные комбайны": 0,
                        "Кормоуборочные комбайны": 1,
                        "Картофелеуборочные комбайны": 2,
                        "Свеклоуборочные комбайны": 3, }


def addHarvesterToCashe(data):
    try:
        harvester_category = data["Категория"]
        categorized_harvesters[harvester_categories[harvester_category]].append(
            data["ID"])
    except:
        pass
    currency = data["Валюта"]
    if currency in EXCHANGE_RATE:
        data["Цена"] = float(data["Цена"]) * EXCHANGE_RATE[currency]
    harvester_jsons[data["ID"]] = data

for item in get_items():
    if not "Раздел" in item["data"]:
        continue
    if is_trailer(item["data"]["Раздел"]):
        addTrailerToCashe(item["data"])
    elif is_tractor(item["data"]["Раздел"]):
        # createModel(item["data"])
        addtractorToCashe(item["data"])
    elif is_harvester(item["data"]["Раздел"]):
        addHarvesterToCashe(item["data"])
    else:
        logging.info(f"uncotigarized item with id: {item['id']}")

def save_machinery(data):
    if "ID" in data:
        id = data["ID"]
        try:
            remove_item(id)
            logging.info(f"removed {id}")
        except: pass
        logging.info(f"saving {id} with data {data}")
        write_item(data)
        if "Раздел" in data:
            createModel(item["data"])
            if is_trailer(data["Раздел"]):
                addTrailerToCashe(data)
            elif is_tractor(data["Раздел"]):
                addtractorToCashe(data)
            elif is_harvester(data["Раздел"]):
                addHarvesterToCashe(data)


def remove_machinery(id):
    remove_item(id)
    logging.info(f"removed {id} from db")
    if id in tractor_jsons:
        logging.info(f"removed {id} from tractor_jsons")
        for category_index in range(len(categorized_tractors)):
            try:
                categorized_tractors[category_index].remove(id)
                logging.info(f"removed {id} from categorized_tractors[{category_index}]")
            except: pass
        del tractor_jsons[id]
    if id in trailer_jsons:
        logging.info(f"removed {id} from trailer_jsons")
        for category_index in categorized_trailers:
            try:
                categorized_trailers[category_index].remove(id)
                logging.info(f"removed {id} from categorized_trailers[{category_index}]")
            except: pass
        del trailer_jsons[id]
    if id in harvester_jsons:
        logging.info(f"removed {id} from harvester_jsons")
        for category_index in range(len(categorized_harvesters)):
            try:
                logging.info(f"removed {id} from categorized_harvesters[{category_index}]")
                categorized_harvesters[category_index].remove(id)
            except: pass
        del harvester_jsons[id]