import logging
from pkg.config.config import EXCHANGE_RATE
from pkg.elevation.elevation import haversine
import dto

trailer_jsons = {}

categorized_trailers = {
    1: [],
    2: [],
    3: [],
    4: [],
    5: [],
    6: [],
    7: [],
    8: [],
    9: [],
    14: [],
    15: [],
    16: [],
    17: 2,
    18: 2,
    19: [],
    20: 1,
    21: 2,
    22: [], # clear
    23: [], # clear
    24: [],
    25: 24,
    26: 24,
    27: 24,
    28: 24,
    29: 24,
    30: 24,
    31: 24,
    32: 24,
    33: [],
    34: 33,
    35: 33,
    36: 33,
    37: [],
    38: 37,
    39: 37,
    40: 37,
    41: [],
    42: [],
    43: [], 
    44: [],
    45: [], # clear
    46: [],
    47: [],
    48: [], # clear
    49: [], # clear
    50: [],
    51: [],
    52: [],
    53: [],
    54: [],
    55: [],
    56: [],
    57: [],
}

trailer_section = ["Почвообрабатывающая техника"]

def is_trailer(section):
    return section in trailer_section


def addTrailerToCashe(data):
    trailer_id = data["ID"]
    trailer_category_ids = []
    match data["Категория"]:
        case "Дискаторы":
            if str(data).lower().find("дисков") != -1 or str(data).lower().find("лущ") != -1:
                if data["Глубина вспашки, см"] == "" or 5 <= int(data["Глубина вспашки, см"]) <= 8:
                    trailer_category_ids.append(1)
                if data["Глубина вспашки, см"] == "" or 8 <= int(data["Глубина вспашки, см"]) <= 10:
                    trailer_category_ids.append(2)
                if data["Глубина вспашки, см"] == "" or 10 <= int(data["Глубина вспашки, см"]) <= 12:
                    trailer_category_ids.append(19)
                trailer_category_ids.append(3)
        case "Бороны":
            if str(data).lower().find("дисков") != -1 or str(data).lower().find("лущ") != -1:
                if data["Глубина вспашки, см"] == "" or 5 <= int(data["Глубина вспашки, см"]) <= 8:
                    trailer_category_ids.append(1)
                if data["Глубина вспашки, см"] == "" or 8 <= int(data["Глубина вспашки, см"]) <= 10:
                    trailer_category_ids.append(2)
                if data["Глубина вспашки, см"] == "" or 10 <= int(data["Глубина вспашки, см"]) <= 12:
                    trailer_category_ids.append(19)
                trailer_category_ids.append(3)
            if str(data).lower().find("игольчатая") != -1:
                trailer_category_ids.append(4)
            if str(data).lower().find("зубч") != -1:
                trailer_category_ids.append(5)
            if str(data).lower().find("ножевая") != -1:
                trailer_category_ids.append(6)
            if str(data).lower().find("пружинная") != -1:
                trailer_category_ids.append(7)
        case "Катки":
            trailer_category_ids.append(8)
        case "Сеялки":
            if str(data).lower().find("зернов") != -1:
                trailer_category_ids.append(42)
                trailer_category_ids.append(43)
            trailer_category_ids.append(47)
            trailer_category_ids.append(41)
            trailer_category_ids.append(44)
            trailer_category_ids.append(45)
        case "Культиваторы":
            trailer_category_ids.append(33)
            if str(data).lower().find("подкорм") != -1:
                trailer_category_ids.append(24)
            elif str(data).lower().find("плоскорез") != -1:
                trailer_category_ids.append(37)
            else:
                trailer_category_ids.append(50)
                trailer_category_ids.append(51)
                trailer_category_ids.append(52)
                trailer_category_ids.append(53)
                trailer_category_ids.append(54)
        case "Плуги и глубокорыхлители":
            trailer_category_ids.append(9)
            trailer_category_ids.append(46)
            if str(data).lower().find("плоскорез") != -1:
                trailer_category_ids.append(55)
                trailer_category_ids.append(56)
                trailer_category_ids.append(57)
            if str(data).lower().find("глубокорыхлитель") != -1:
                trailer_category_ids.append(14)
                trailer_category_ids.append(15)
                trailer_category_ids.append(16)

    currency = data["Валюта"]
    data["Цена"] = float(data["Цена"]) * EXCHANGE_RATE[currency]
    for triler_category_id in trailer_category_ids:
        categorized_trailers[triler_category_id].append(trailer_id)
    trailer_jsons[trailer_id] = data

def get_trailers(tractor_power, reqData, trailer_amount=1, trailer_index=-1):
    raw_trailers = categorized_trailers[reqData["work_type"]]
    if isinstance(raw_trailers, int):
        raw_trailers = categorized_trailers[raw_trailers]
    trailers = []
    max_dilivery_time = 0
    min_dilivery_time = 999999999

    max_req_power = 0
    min_req_power = 999999999
    
    max_price = 0
    min_price = 999999999
    for trailer_id in raw_trailers:
        try:
            if reqData["work_type"] == 1 or reqData["work_type"] == 2:
                req_power = float(
                    trailer_jsons[trailer_id]["Рекомендуемая мин. мощность тягача, л.с."])
            else:
                req_power = float(
                    trailer_jsons[trailer_id]["Рекомендуемая мин. мощность тягача, л.с."]) * 1.05
            
        except:
            continue
        try:
            coords = list(map(float, trailer_jsons[trailer_id]["Кординаты"].split(",")))
        except:
            coords = None
        price = trailer_jsons[trailer_id]["Цена"]
        if req_power <= tractor_power:
            if req_power > max_req_power: max_req_power = req_power
            if req_power < min_req_power: min_req_power = req_power
            
            if price > max_price: max_price = price
            if price < min_price: min_price = price

            dilivery_time = None
            if coords:
                dilivery_time = haversine(coords[0], coords[1], reqData["lat"], reqData["lon"])/800000
                if dilivery_time > max_dilivery_time: max_dilivery_time = dilivery_time
                if dilivery_time < min_dilivery_time: min_dilivery_time = dilivery_time
            trailer = dto.Trailer(
                id=trailer_id,
                price=price,
                req_power=req_power,
                dilivery_time=dilivery_time
            )
            trailers.append(trailer)

    for trailer in trailers:
        trailer.SetPriceRating(max_price=max_price, min_price=min_price)
        trailer.SetPowerRating(max_req_power=max_req_power, min_req_power=min_req_power)
        trailer.SetEfficiencyRating()
        trailer.SetDiliveryTimeRating(max_dilivery_time=max_dilivery_time, min_dilivery_time=min_dilivery_time)
        trailer.SetRating()
    
    def sortByRating(val): return val.rating
    trailers.sort(key=sortByRating, reverse=True)    
    # logging.info(f"got trailers: {trailers}; trailer_amount={trailer_amount}, trailer_index={trailer_index}")

    if trailer_index == -1:
        if len(trailers) >= trailer_amount:
            trailers = trailers[:trailer_amount]
    elif trailer_index < len(trailers):
        trailers = [trailers[trailer_index]]
    else:
        trailers = []
    # logging.info(f"returning trailers: {[trailer.id for trailer in trailers]}; trailer_amount={trailer_amount}, trailer_index={trailer_index}")
    return trailers

