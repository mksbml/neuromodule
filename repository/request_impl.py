import json
from pkg.db.db import ConnectDB

# Можно хуйнуть нормальный билдер для additionalParams
def addRequest(soil_background, work_type, lat, lon, plot_size, additionalParams, pushHistory, is_message_required):
    conn = ConnectDB()
    cur = conn.cursor()
    if "pmin" in additionalParams:
        pmin = additionalParams["pmin"]
    else:
        pmin = "NULL"

    if "pmax" in additionalParams:
        pmax = additionalParams["pmax"]
    else:
        pmax = "NULL"

    if "limit" in additionalParams:
        ans_limit = additionalParams["limit"]
    else:
        ans_limit = "NULL"

    if "stock" in additionalParams:
        stock = additionalParams["stock"]
    else:
        stock = "NULL"

    if "leasing" in additionalParams:
        leasing = "'"+additionalParams["leasing"]+"'"
    else:
        leasing = "NULL"

    if "fueltype" in additionalParams:
        fueltype = "'"+additionalParams["fueltype"]+"'"
    else:
        fueltype = "NULL"

    if "wmin" in additionalParams:
        wmin = additionalParams["wmin"]
    else:
        wmin = "NULL"

    if "wmax" in additionalParams:
        wmax = additionalParams["wmax"]
    else:
        wmax = "NULL"

    if "condition" in additionalParams:
        condition = "'"+additionalParams["condition"]+"'"
    else:
        condition = "NULL"

    if "mdelivery" in additionalParams:
        mdelivery = additionalParams["mdelivery"]
    else:
        mdelivery = "NULL"

    if "drivetype" in additionalParams:
        drivetype = "'"+additionalParams["drivetype"]+"'"
    else:
        drivetype = "NULL"

    cur.execute(
        f"INSERT INTO request (soil_background, work_type, lat, lon, plot_size, pmin, pmax, stock, leasing, fueltype, wmin, wmax, condition, mdelivery, drivetype, ans_limit, push_history, is_message_required) VALUES ({soil_background}, {work_type}, {lat}, {lon}, {plot_size}, {pmin}, {pmax}, {stock}, {leasing}, {fueltype}, {wmin}, {wmax}, {condition}, {mdelivery}, {drivetype}, {ans_limit}, '{json.dumps(pushHistory)}'::json, {is_message_required}) RETURNING id")
    id = cur.fetchone()["id"]
    conn.commit()
    cur.close()
    conn.close()
    return id


def addNotify(req_id, item_id):
    conn = ConnectDB()
    cur = conn.cursor()
    cur.execute(
        f"INSERT INTO notify (request_id, item_id) VALUES ({req_id}, {item_id})")
    conn.commit()
    cur.close()
    conn.close()
    return


def getRequest(id):
    conn = ConnectDB()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM request WHERE id = {id}")
    data = cur.fetchone()
    cur.close()
    conn.close()
    return data


def getStats(start, end):
    conn = ConnectDB()
    cur = conn.cursor()
    cur.execute(
        f"SELECT COUNT(*) FROM request WHERE created_at > to_timestamp({start})::date AND created_at < to_timestamp({end})::date")
    data = cur.fetchone()
    cur.close()
    conn.close()
    return data
