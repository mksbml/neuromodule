import json
import logging
from pkg.db.db import ConnectDB

def getModels(mark, model, section):
    conn = ConnectDB()
    cur = conn.cursor()
    query = f"SELECT * FROM models WHERE"
    if mark:
        query += f" mark LIKE '%{mark}%' AND"
    if model:
        query += f" model LIKE '%{model}%' AND"
    query += f" section = '{section}'"
    cur.execute(query)
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

def getModel(mark, model, section):
    conn = ConnectDB()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM models WHERE mark = '{mark}' AND model = '{model}' AND section = '{section}'")
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

def createModel(mark, model, section, data):
    new_data = {
        "Производитель": [mark],
        "Модель": [model],
        "Категория": [section],
    }
    if "Страна" in data and data["Страна"] != "":
        new_data["Страна"] = [data["Страна"]]
    if "Мощность двигателя, л.с." in data and data["Мощность двигателя, л.с."] != "":
        new_data["Мощность двигателя, л.с."] = [data["Мощность двигателя, л.с."]]
    if "Мощность двигателя, кВт" in data and data["Мощность двигателя, кВт"] != "":
        new_data["Мощность двигателя, кВт"] = [data["Мощность двигателя, кВт"]]
    if "Объем двигателя, л" in data and data["Объем двигателя, л"] != "":
        new_data["Объем двигателя, л"] = [data["Объем двигателя, л"]]
    if "Цилиндры, шт" in data and data["Цилиндры, шт"] != "":
        new_data["Цилиндры, шт"] = [data["Цилиндры, шт"]]
    if "Габариты: Длина, мм" in data and data["Габариты: Длина, мм"] != "":
        new_data["Габариты: Длина, мм"] = [data["Габариты: Длина, мм"]]
    if "Габариты: Ширина, мм" in data and data["Габариты: Ширина, мм"] != "":
        new_data["Габариты: Ширина, мм"] = [data["Габариты: Ширина, мм"]]
    if "Габариты: Высота, мм" in data and data["Габариты: Высота, мм"] != "":
        new_data["Габариты: Высота, мм"] = [data["Габариты: Высота, мм"]]
    if "Вес, кг" in data and data["Вес, кг"] != "":
        new_data["Вес, кг"] = [data["Вес, кг"]]
    if "Коробка передач" in data and data["Коробка передач"] != "":
        new_data["Коробка передач"] = [data["Коробка передач"]]
    if "Число передач заднего хода" in data and data["Число передач заднего хода"] != "":
        new_data["Число передач заднего хода"] = [data["Число передач заднего хода"]]
    if "Число передач переднего хода" in data and data["Число передач переднего хода"] != "":
        new_data["Число передач переднего хода"] = [data["Число передач переднего хода"]]
    if "Колея, мм" in data and data["Колея, мм"] != "":
        new_data["Колея, мм"] = [data["Колея, мм"]]
    if "Тип двигателя" in data and data["Тип двигателя"] != "":
        new_data["Тип двигателя"] = [data["Тип двигателя"]]


    old_data = getModel(mark, model, section)

    if len(old_data) == 0:
        conn = ConnectDB()
        cur = conn.cursor()
        cur.execute(f"INSERT INTO models (mark, model, section, data) VALUES ('{mark}', '{model}', '{section}', '{json.dumps(new_data)}'::json)")
        cur.close()
        conn.commit()
        conn.close()
    elif len(old_data) == 1:
        old_data = old_data[0]["data"]
        
        for key in new_data:
            if not key in old_data:
                old_data[key] = new_data[key]
            elif not new_data[key][0] in old_data[key]:
                old_data[key].append(new_data[key][0])
        conn = ConnectDB()
        cur = conn.cursor()
        cur.execute(f"UPDATE models SET data = '{json.dumps(old_data)}'::json WHERE mark = '{mark}' AND model = '{model}' AND section = '{section}'")
        cur.close()
        conn.commit()
        conn.close()

    return