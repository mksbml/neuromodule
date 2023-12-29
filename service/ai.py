import json
import logging
import service
from pkg.cache import cache

import requests
from pkg.elevation.elevation import getElevationAngle, haversine
from pkg.cache.cache import categorized_tractors, tractor_jsons, categorized_harvesters, harvester_jsons
from pkg.cache import get_trailers, trailer_jsons, categorized_trailers
import repository
from repository.request_impl import getRequest, addRequest
from pkg.neuro.neuro import Pf, get_tyagovoe_type
from pkg.neuro.sub_neuro import work_type_ids
from pkg.config.config import MESSAGE_MODULE_URL


def setAiRequest(soil_background, work_type, plot_size, lat, lon, additionalParams, pushHistory, is_message_required):
    request_id = addRequest(
        soil_background, work_type, lat, lon, plot_size, additionalParams, pushHistory=pushHistory, is_message_required=is_message_required)
    return request_id


def get_harvester_results(reqData):
    plot_size = reqData["plot_size"]
    ans = []
    harvester_ids = categorized_harvesters[reqData["work_type"]-10]
    for harvester_id in harvester_ids:
        harvester = harvester_jsons[harvester_id]
        try:
            power = get_power_HP(harvester)
            if filter_by_plot_size_and_power(power, plot_size) and filterAnswer(harvester, reqData):
                ans.append({"tractor": {"id":harvester_id}})
        except:
            pass
    ans = sort_tractor_ans(ans, reqData)
    ans = set_labels(ans)
    messages = {}

    try:
        uklon_polya = getElevationAngle(reqData["lat"], reqData["lon"], plot_size)
    except:
        uklon_polya = 0

    
    if reqData["is_message_required"]:
        try:
            repository.update_response(status="preparation of a description", req_id=reqData["id"])
            messages = get_messages(
                ans=ans,
                work_type=reqData["work_type"],
                soil_background=-1,
                plot_size=plot_size,
                lat=reqData["lat"],
                lon=reqData["lon"],
                uklon_polya=uklon_polya
            )
        except Exception as e:
            logging.info(f"couldn't get messages, exception: {e}")
    ans = crop_answer(ans, reqData["ans_limit"])
    ans = to_ans_view(ans, messages)
    return ans


def get_tractor_results(reqData, trailer_amount, is_push_history = False):
    work_type = reqData["work_type"]
    soil_background = reqData["soil_background"]

    lat = reqData["lat"]
    lon = reqData["lon"]

    plot_size = reqData["plot_size"]
    tip_pochv = "Легкие"
    if plot_size > 10000:
        tip_pochv = "Средние"
        if plot_size > 1000000:
            tip_pochv = "Тяжелые"
    try:
        uklon_polya = getElevationAngle(lat, lon, plot_size)
    except:
        uklon_polya = 0

    ans = GetAnswers(
        reqData=reqData,
        trailer_amount=trailer_amount,
        is_push_history=is_push_history,
        uklon_polya=uklon_polya,
        work_type=work_type,
        soil_background=soil_background,
        tip_pochv=tip_pochv,
    )

    if not ans:
        return []

    messages = {}
    if ans[0]["tractor"]["id"] != 0:
        ans = sort_tractor_ans(ans, reqData)
        logging.info(f"sorted tractor results")
        ans = crop_answer(ans, reqData["ans_limit"])
        logging.info(f"cropped answer")
        ans = set_labels(ans)
        logging.info(f"set labels")
        if reqData["is_message_required"]:
            try:
                logging.info(f"getting message")
                repository.update_response(status="preparation of a description", req_id=reqData["id"])
                messages = get_messages(
                    ans=ans,
                    work_type=work_type,
                    soil_background=soil_background,
                    plot_size=plot_size,
                    lat=lat,
                    lon=lon,
                    uklon_polya=uklon_polya
                )
                logging.info(f"got message")
            except Exception as e:
                logging.info(f"couldn't get messages, exception: {e}")
    ans = to_ans_view(ans, messages)
    logging.info(f"converted to answer view")
    return ans

def get_messages(ans, work_type, soil_background, plot_size, lat, lon, uklon_polya):
    tractors = []
    trailers = []
    if len(ans) > 3:
        ans = ans[:3]
    for _ans in ans:
        tractor_id = _ans["tractor"]["id"]
        tractors.append(tractor_jsons[tractor_id])
        logging.info(f"{_ans}")
        if "trailers" in _ans:
            trailer_id = _ans["trailers"][0]["items"][0].id
            trailers.append(trailer_jsons[trailer_id])
    payload = {
        "tractors": tractors,
        "trailers": trailers,
        "work_type": work_type_ids[work_type],
        "soil_background": "Отсутствует" if soil_background == -1 else Pf[soil_background-1],
        "plot_size": plot_size,
        "coords": f"{lat}, {lon}",
        "uklon_polya": uklon_polya,
    }
    response = requests.post(url=MESSAGE_MODULE_URL, json=payload)
    messages = response.json()
    return messages

def set_labels(ans):
    best = {
        "efficiency_rating": 0,
        "dilivery_time_rating": 0,
        "price_rating": 0,
        "power_rating": 0,
    }
    for i in range(len(ans)):
        logging.info(f"set_label ans[{i}]: {ans[i]}")
        if "trailers" in ans[i]:
            logging.info(f"set_label ans[{i}]['trailers']: {ans[i]['trailers']}")
            for pre_work_type_index in range(len(ans[i]["trailers"])):
                for trailer_index in range(len(ans[i]["trailers"][pre_work_type_index]["items"])):
                    trailer = ans[i]["trailers"][pre_work_type_index]["items"][trailer_index]
                    markers = trailer.getMarkers()
                    if best["efficiency_rating"] < markers["efficiency"]:
                        best["efficiency_rating"] = markers["efficiency"]
                    if best["power_rating"] < markers["power"]:
                        best["power_rating"] = markers["power"]
                    if best["dilivery_time_rating"] < markers["distance"]:
                        best["dilivery_time_rating"] = markers["distance"]
                    if best["price_rating"] < markers["price"]:
                        best["price_rating"] = markers["price"]
        else:
            if best["efficiency_rating"] < ans[i]["tractor"]["efficiency_rating"]:
                best["efficiency_rating"] = ans[i]["tractor"]["efficiency_rating"]
            if best["power_rating"] < ans[i]["tractor"]["power_rating"]:
                best["power_rating"] = ans[i]["tractor"]["power_rating"]
            if best["dilivery_time_rating"] < ans[i]["tractor"]["dilivery_time_rating"]:
                best["dilivery_time_rating"] = ans[i]["tractor"]["dilivery_time_rating"]
            if best["price_rating"] < ans[i]["tractor"]["price_rating"]:
                best["price_rating"] = ans[i]["tractor"]["price_rating"]
    for i in range(len(ans)):
        if "trailers" in ans[i]:
            for pre_work_type_index in range(len(ans[i]["trailers"])):
                for trailer_index in range(len(ans[i]["trailers"][pre_work_type_index]["items"])):
                    trailer = ans[i]["trailers"][pre_work_type_index]["items"][trailer_index]
                    markers = trailer.getMarkers()

                    if best["efficiency_rating"] == markers["efficiency"]:
                        if not "labels" in ans[i]:
                            ans[i]["labels"] = []
                        best["efficiency_rating"] = -1
                        ans[i]["labels"].append({
                            "name": "efficiency",
                            "value": True,
                        })

                    if best["dilivery_time_rating"] == markers["distance"]:
                        if not "labels" in ans[i]:
                            ans[i]["labels"] = []
                        best["dilivery_time_rating"] = -1
                        ans[i]["labels"].append({
                            "name": "distance",
                            "value": True,
                        })

                    if best["price_rating"] == markers["price"]:
                        if not "labels" in ans[i]:
                            ans[i]["labels"] = []
                        best["price_rating"] = -1
                        ans[i]["labels"].append({
                            "name": "price",
                            "value": True,
                        })

                    if best["power_rating"] == markers["power"]:
                        if not "labels" in ans[i]:
                            ans[i]["labels"] = []
                        best["power_rating"] = -1
                        ans[i]["labels"].append({
                            "name": "power",
                            "value": True,
                        })
        else:
            if best["efficiency_rating"] == ans[i]["tractor"]["efficiency_rating"]:
                if not "labels" in ans[i]:
                    ans[i]["labels"] = []
                best["efficiency_rating"] = -1
                ans[i]["labels"].append({
                    "name": "efficiency",
                    "value": True,
                })

            if best["dilivery_time_rating"] == ans[i]["tractor"]["dilivery_time_rating"]:
                if not "labels" in ans[i]:
                    ans[i]["labels"] = []
                best["dilivery_time_rating"] = -1
                ans[i]["labels"].append({
                    "name": "distance",
                    "value": True,
                })

            if best["price_rating"] == ans[i]["tractor"]["price_rating"]:
                if not "labels" in ans[i]:
                    ans[i]["labels"] = []
                best["price_rating"] = -1
                ans[i]["labels"].append({
                    "name": "price",
                    "value": True,
                })

            if best["power_rating"] == ans[i]["tractor"]["power_rating"]:
                if not "labels" in ans[i]:
                    ans[i]["labels"] = []
                best["power_rating"] = -1
                ans[i]["labels"].append({
                    "name": "power",
                    "value": True,
                })

    return ans


def crop_answer(ans, limit):
    if limit != None:
        ans = ans[:limit]
    return ans


def to_ans_view(ans, messages):
    for i in range(len(ans)):
        if "trailers" in ans[i]:
            for pre_work_type_index in range(len(ans[i]["trailers"])):
                for trailer_index in range(len(ans[i]["trailers"][pre_work_type_index]["items"])):
                    trailer = ans[i]["trailers"][pre_work_type_index]["items"][trailer_index]
                    ans_trailer = trailer.ToAnswer()
                    ans[i]["trailers"][pre_work_type_index]["items"][trailer_index] = ans_trailer
        else:
            ans[i]["trailers"] = [
                {
                    "items": [
                        {
                            "id": 0,
                            "markers":[
                                {
                                    "name": "efficiency",
                                    "value": int(100*ans[i]["tractor"]["efficiency_rating"])/10,
                                },
                                {
                                    "name": "power",
                                    "value": int(100*ans[i]["tractor"]["dilivery_time_rating"])/10,
                                },
                                {
                                    "name": "price",
                                    "value": int(100*ans[i]["tractor"]["power_rating"])/10,
                                },
                                {
                                    "name": "distance",
                                    "value": int(100*ans[i]["tractor"]["price_rating"])/10,
                                },
                            ]
                        }
                    ],
                    "workTypeID": 0
                }
            ]
        if str(i) in messages:
            ans[i]["message"] = messages[str(i)]
        if "dilivery_time_rating" in ans[i]["tractor"]:
            del ans[i]["tractor"]["dilivery_time_rating"]
        if "efficiency_rating" in ans[i]["tractor"]:
            del ans[i]["tractor"]["efficiency_rating"]
        if "power_rating" in ans[i]["tractor"]:
            del ans[i]["tractor"]["power_rating"]
        if "price_rating" in ans[i]["tractor"]:
            del ans[i]["tractor"]["price_rating"]
    return ans


def sort_tractor_ans(ans, reqData):
    max_dilivery_time = 0
    min_dilivery_time = 9999999
    max_power_price = 0
    min_power_price = 99999999
    max_power = 0
    min_power = 99999999
    max_price = 0
    min_price = 99999999
    max_year_range = 0
    max_warranty_period = 0
    rate = []
    for i in range(len(ans)):
        tractor_id = ans[i]["tractor"]["id"]
        if tractor_id in tractor_jsons:
            tractor = tractor_jsons[tractor_id]
        elif tractor_id in harvester_jsons:
            tractor = harvester_jsons[tractor_id]
        power = get_power_HP(tractor)
        try:
            year_range = 2023 - int(tractor["Год выпуска"])
        except:
            year_range = None
        try:
            warranty_period = int(tractor["Гарантийный срок, мес"])
        except:
            warranty_period = None

        dilivery_time = None
        if tractor["Кординаты"] != "":
            lat, lon = map(float, tractor["Кординаты"].split(","))
            dilivery_time = haversine(
                lat, lon, reqData["lat"], reqData["lon"])/800000
            if dilivery_time > max_dilivery_time:
                max_dilivery_time = dilivery_time
            if min_dilivery_time > dilivery_time:
                min_dilivery_time = dilivery_time
        price = int(tractor["Цена"])
        if price > max_price:
            max_price = price
        if min_price > price:
            min_price = price
        if price/power > max_power_price:
            max_power_price = price/power
        if min_power_price > price/power:
            min_power_price = price/power

        if power > max_power:
            max_power = power
        if min_power > power:
            min_power = power

        if dilivery_time and dilivery_time > max_year_range:
            max_year_range = dilivery_time
        if warranty_period and warranty_period > max_warranty_period:
            max_warranty_period = int(tractor["Гарантийный срок, мес"])

        rate.append({"power": power,
                     "price": price,
                     "year_range": year_range,
                     "dilivery_time": dilivery_time,
                     "warranty_period": warranty_period,
                     "id": i, })
    power_rate = (reqData["plot_size"] / 1000) ** 0.3 * 0.1
    for i in rate:
        rating = i["power"] * power_rate
        i["price_rating"] = 1
        i["power_rating"] = 1
        i["efficiency_rating"] = 1
        i["dilivery_time_rating"] = 1
        if max_power_price != min_power_price:
            i["efficiency_rating"] = (max_power_price - i["price"] / i["power"])/(max_power_price - min_power_price)
        if max_power != min_power:
            power_rating_flow = 1 - (max_power - i["power"])/(max_power - min_power)
            power_rating_flow = 0.2 + power_rating_flow
            # power_rating_flow = power_rating_flow/0.7
            power_rating_flow = power_rating_flow if power_rating_flow <= 1 else 2-power_rating_flow
            i["power_rating"] = power_rating_flow
        if max_price != min_price:
            i["price_rating"] = (max_price - i["price"]) / \
                (max_price - min_price)
        rating += 2.5 * (max_price - i["price"])/min_price

        if i["dilivery_time"] != None and max_dilivery_time != min_dilivery_time:
            rating += 2.5 * (max_dilivery_time -
                             i["dilivery_time"])/(max_dilivery_time - min_dilivery_time)
            i["dilivery_time_rating"] = (max_dilivery_time -
                                         i["dilivery_time"])/(max_dilivery_time - min_dilivery_time)
        rating += 1.5 * (max_year_range - i["year_range"])/max_year_range
        rating += 1.5 * i["warranty_period"]/max_warranty_period
        i["rating"] = rating

    rate = sorted(rate, key=lambda item: item["rating"], reverse=True)
    for i in rate:
        ans[i["id"]]["tractor"]["dilivery_time_rating"] = i["dilivery_time_rating"]
        ans[i["id"]]["tractor"]["price_rating"] = i["price_rating"]
        ans[i["id"]]["tractor"]["efficiency_rating"] = i["efficiency_rating"]
        ans[i["id"]]["tractor"]["power_rating"] = i["power_rating"]
        if "trailers" in ans[i["id"]]:
            for pre_work_type_index in range(len(ans[i["id"]]["trailers"])):
                for trailer_index in range(len(ans[i["id"]]["trailers"][pre_work_type_index]["items"])):
                    trailer = ans[i["id"]
                                ]["trailers"][pre_work_type_index]["items"][trailer_index]
                    trailer.AddtractorRating(
                        tractor_dilivery_time_rating=i["dilivery_time_rating"],
                        tractor_price_rating=i["price_rating"],
                        tractor_efficiency_rating=i["efficiency_rating"],
                        tractor_power_rating=i["power_rating"]
                    )
                    ans[i["id"]]["trailers"][pre_work_type_index]["items"][trailer_index] = trailer
    return ans


def shortAiTaktor(tractor_id, lat, lon):
    tractor = tractor_jsons[tractor_id]
    power = get_power_HP(tractor)
    ans = {}
    reqData = {
        "lat": lat,
        "lon": lon,
    }
    for work_type in categorized_trailers:
        reqData["work_type"] = work_type
        ans[work_type] = get_trailers(power, reqData, 1)
        for trailer_index in range(len(ans[work_type])):
            ans[work_type][trailer_index] = ans[work_type][trailer_index].ToAnswer()
    return ans


def sort_shorttractor_ans(tractors, reqData):
    max_cost = 0
    max_dilivery_time = 0
    max_year_range = 0
    max_warranty_period = 0
    rate = []
    for tractor in tractors:
        power = get_power_HP(tractor)
        try:
            year_range = 2023 - int(tractor["Год выпуска"])
        except:
            year_range = None
        try:
            costs = int(tractor["Цена"])
        except:
            costs = None
        try:
            warranty_period = int(tractor["Гарантийный срок, мес"])
        except:
            warranty_period = None

        dilivery_time = None
        if tractor["Кординаты"] != "":
            lat, lon = map(float, tractor["Кординаты"].split(","))
            dilivery_time = haversine(
                lat, lon, reqData["lat"], reqData["lon"])/800000
            if dilivery_time > max_dilivery_time:
                max_dilivery_time = dilivery_time

        if costs and costs > max_cost:
            max_cost = costs
        if dilivery_time and dilivery_time > max_year_range:
            max_year_range = dilivery_time
        if warranty_period and warranty_period > max_warranty_period:
            max_warranty_period = int(tractor["Гарантийный срок, мес"])

        rate.append({"power": power,
                     "costs": costs,
                     "year_range": year_range,
                     "dilivery_time": dilivery_time,
                     "warranty_period": warranty_period,
                     "id": tractor["ID"]})
    for i in rate:
        rating = i["power"] * 0.015
        rating += 2.5 * (max_cost - i["costs"])/max_cost
        if i["dilivery_time"] != None:
            rating += 2.5 * (max_dilivery_time -
                             i["dilivery_time"])/max_dilivery_time
        rating += 1.5 * (max_year_range - i["year_range"])/max_year_range
        rating += 1.5 * i["warranty_period"]/max_warranty_period
        i["rating"] = rating

    rate = [sorted(rate, key=lambda item: item["rating"], reverse=True)]
    new_ans = []
    for i in rate[0]:
        new_ans.append(i["id"])
    return new_ans[0]


def shortAiTrailer(trailer_id, lat, lon):
    trailer = trailer_jsons[trailer_id]
    min_power = float(trailer["Рекомендуемая мин. мощность тягача, л.с."])
    ans = []
    for tractor_id in tractor_jsons:
        tractor = tractor_jsons[tractor_id]
        power = get_power_HP(tractor)
        if power >= min_power:
            ans.append(tractor)
    reqData = {"lat": lat, "lon": lon}
    ans = sort_shorttractor_ans(ans, reqData)
    return ans


def getResults(req_id, trailer_amount):
    reqData = getRequest(req_id)
    if 10 <= reqData["work_type"] <= 13:
        return get_harvester_results(reqData)
    else:
        if reqData["push_history"]:
            ans =  get_tractor_results(reqData, trailer_amount=trailer_amount, is_push_history=True)
            if ans:
                return ans
        logging.info(
            f"get_tractor_results({reqData}, trailer_amount={trailer_amount})")
        return get_tractor_results(reqData, trailer_amount=trailer_amount)


def filterAnswer(tractor, reqData):
    if reqData["pmin"] != None and "Цена" in tractor and int(tractor["Цена"]) < reqData["pmin"]:
        return False
    if reqData["pmax"] != None and "Цена" in tractor and int(tractor["Цена"]) > reqData["pmax"]:
        return False
    if reqData["leasing"] != None and "Лизинг" in tractor and tractor["Лизинг"] != reqData["leasing"]:
        return False
    if reqData["fueltype"] != None and "Тип двигателя" in tractor and tractor["Тип двигателя"] != reqData["fueltype"]:
        return False
    if reqData["wmax"] != None and tractor["Вес, кг"] != "" and int(tractor["Вес, кг"]) > reqData["wmax"]:
        return False
    if reqData["wmin"] != None and tractor["Вес, кг"] != "" and int(tractor["Вес, кг"]) < reqData["wmin"]:
        return False
    if reqData["condition"] != None and "Состояние" in tractor and tractor["Состояние"] != reqData["condition"]:
        return False

    if reqData["mdelivery"] != None and "Кординаты" in tractor and tractor["Кординаты"] != "":
        lat, lon = map(float, tractor["Кординаты"].split(","))
        dilivery_range = haversine(lat, lon, reqData["lat"], reqData["lon"])
        if dilivery_range > int(reqData["mdelivery"]) * 800 * 1000:  # *60*24:
            print(dilivery_range / 1000, reqData["mdelivery"])
            return False
    if reqData["drivetype"] != None and "Категория" in tractor and tractor["Категория"] != reqData["drivetype"]:
        return False
    return True


def get_power_HP(data):
    try:
        power = float(data["Мощность двигателя, л.с."])
    except:
        power = 1.36 * float(data["Мощность двигателя, кВт"])
    return power


def filter_by_plot_size_and_power(power, plot_size):
    flag = False
    if plot_size <= 10000 and power <= 30:
        flag = True
    elif 10000 <= plot_size <= 100000 and 30 <= power <= 80:
        flag = True
    elif 100000 <= plot_size <= 500000 and 80 <= power <= 150:
        flag = True
    elif 500000 <= plot_size <= 1000000 and 150 <= power <= 250:
        flag = True
    elif plot_size >= 1000000 and power >= 250:
        flag = True
    return flag


def GetAnswers(reqData, trailer_amount, is_push_history, uklon_polya, work_type, soil_background, tip_pochv):
    tyagovoe_type = get_tyagovoe_type(
        uklon_polya, work_type, soil_background, tip_pochv)
    tractor_ids = categorized_tractors[tyagovoe_type]
    logging.info(
        f"before -- getAnswers({tractor_ids}, {reqData}, trailer_amount={trailer_amount})")
    if is_push_history:
        ans = getPushHistoryAnswers(tractor_ids, tyagovoe_type, reqData)
        logging.info(f"after -- tyagovoe = {tyagovoe_type} getPushAnswers {ans}")
        if ans:
            return ans
        
        pog = 1
        while not ans and pog < 5:
            ans = []
            if tyagovoe_type + pog <= 4:
                tractor_ids = categorized_tractors[tyagovoe_type + pog]
                ans = getPushHistoryAnswers(tractor_ids, tyagovoe_type, reqData)
                logging.info(f"after -- tyagovoe = {tyagovoe_type + pog} getPushAnswers {ans}")
                if ans:
                    return ans
            if tyagovoe_type - pog >= 0:
                tractor_ids = categorized_tractors[tyagovoe_type - pog]
                ans = getPushHistoryAnswers(tractor_ids, tyagovoe_type, reqData)
                logging.info(f"after -- tyagovoe = {tyagovoe_type - pog} getPushAnswers {ans}")
                if ans:
                    return ans
            pog += 1

    ans = getAnswers(tractor_ids, reqData,
                    trailer_amount=trailer_amount)

    pog = 1
    while ans == [] and pog < 5:
        ans = []
        if tyagovoe_type + pog <= 4:
            tractor_ids = categorized_tractors[tyagovoe_type + pog]
            ans = getAnswers(tractor_ids, reqData,
                            trailer_amount=trailer_amount)
        if tyagovoe_type - pog >= 0:
            tractor_ids = categorized_tractors[tyagovoe_type - pog]
            _ans = getAnswers(tractor_ids, reqData,
                            trailer_amount=trailer_amount)
            ans += _ans
        pog += 1
    return ans

def getPushHistoryAnswers(tractor_ids, tyagovoe_type, reqData):
    ans = []
    plot_size = reqData["plot_size"]
    for tractor_id in tractor_ids:
        tractor = tractor_jsons[tractor_id]
        power = get_power_HP(tractor)
        if filter_by_plot_size_and_power(power, plot_size) and filterAnswer(tractor, reqData) and filter_by_push_history(tractor, reqData["push_history"]):
            for i in range(4):
                trailers = get_trailers(power, reqData, trailer_index=i)
            
            
                if trailers != []:
                    
                    last_ans = {"tractor": {"id": 0, "name": tractor["Название"]}, "trailers": [
                        {"workTypeID": reqData["work_type"], "items": trailers}]}
                    ans.append(last_ans)
            if ans:
                return ans
    data_tractors = service.GetTractorModels()
    logging.info(f"got {len(data_tractors)} models")
    for data_tractor in data_tractors:
        tractor = data_tractor["data"]
        for key in tractor:
            tractor[key] = tractor[key][len(tractor[key])//2] 
        tractor["Название"] = data_tractor["mark"] + " " + data_tractor["model"]
        tractor["ID"] = 0
        try:
            power = get_power_HP(tractor)
        except:
            continue
        if tyagovoe_type != cache.calculate_tyagovoe(power):
            continue
        if filter_by_plot_size_and_power(power, plot_size) and filter_by_push_history(tractor, reqData["push_history"]):
            logging.info(f"got expected tractor {tractor}")
            trailers = get_trailers(power, reqData, trailer_amount=1)
            logging.info(f"got trailers for expected tractor {trailers}")
            for i in range(4):
                trailers = get_trailers(power, reqData, trailer_index=i)
            
            
                if trailers != []:
                    
                    last_ans = {"tractor": {"id": 0, "name": tractor["Название"]}, "trailers": [
                        {"workTypeID": reqData["work_type"], "items": trailers}]}
                    ans.append(last_ans)
            if ans:
                return ans

def get_all_trailers(power, reqData):
    ans_trailers = []
    for work_type in range(1,10):
        reqData["work_type"] = work_type
        trailers = get_trailers(
                    power, reqData, trailer_amount=1)
        ans_trailers.append({"workTypeID": reqData["work_type"], "items": trailers})
    return ans_trailers
        



def getAnswers(tractor_ids, reqData, trailer_amount):
    ans = []
    plot_size = reqData["plot_size"]
    # ans_push_history = []
    for tractor_id in tractor_ids:
        tractor = tractor_jsons[tractor_id]
        power = get_power_HP(tractor)
        if filter_by_plot_size_and_power(power, plot_size) and filterAnswer(tractor, reqData):
            trailers = get_trailers(
                power, reqData, trailer_amount=trailer_amount)
            if trailers != []:
                last_ans = {"tractor": {"id": tractor_id}, "trailers": [
                    {"workTypeID": reqData["work_type"], "items": trailers}]}
                # if filter_by_push_history(tractor, reqData["push_history"]):
                #     ans_push_history.append(last_ans)
                ans.append(last_ans)
    # if ans_push_history != []:
    #     return ans_push_history
    return ans


def setFilter(filter):
    for char in " ,-_.:/()":
        filter.replace(char, "")
    filter = filter.lower()
    return filter


def filter_by_push_history(tractor, push_history):
    try:
        for filters in push_history:
            for filter_name in filters:
                if filter_name == "Name":
                    filter_val = setFilter(filters[filter_name])
                    tractor_val = setFilter(tractor["Название"])
                    if not filter_val in tractor_val:
                        return False
    except Exception as e:
        id = tractor["ID"]
        logging.error(f"req {id}: filterByPushHistory error {e}")
        return False
    return True
