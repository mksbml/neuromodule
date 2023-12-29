import json
import logging
import os
from flask import jsonify, request
from flask_cors import cross_origin
from pkg.config.config import PATH
from repository.models_impl import getModels
from service.models import createModel


@cross_origin()
def save_model():
    try:
        if request.headers.get('Authorization') != "Bearer a5ZTI2LWUxOTMtNDU4Yy04Y2Fh":
            res = jsonify({"message": "Invalid token."})
            res.status = 401
            return res
        try:
            content = request.get_json(silent=True)
            logging.info(f"/api/save_model content: {content}")
        except:
            res = jsonify(
                {"success": False, "error": "Неверный формат параметров запроса."})
            res.status = 400
            return res
        exceptions = []
        for data in content:
            _data = [{}]
            for key in data:
                if len(data[key]) == 1:
                    for _data_index in range(len(_data)):
                        _data[_data_index][key] = data[key][0]
                else:
                    temp_data = []
                    for data_key_index in range(len(data[key])):
                        for copy_data in _data:
                            copy_data[key] = data[key][data_key_index]
                            temp_data.append(copy_data)

                    _data = temp_data
            for copy_data in _data:
                print(copy_data["Марка"], copy_data["Модель"])
                if createModel(copy_data):
                    exceptions.append([copy_data["Марка"], copy_data["Модель"]])
        return jsonify({"success": True, "exceptions": exceptions})
    except Exception as e:
        logging.warning(f"{content} 500 error {e}")
        res = jsonify(
            {"success": False, "error": "Внутренняя ошибка сервера."})
        res.status = 500
        return res


@cross_origin()
def model_view():
    try:
        if request.headers.get('Authorization') != "Bearer a5ZTI2LWUxOTMtNDU4Yy04Y2Fh":
            res = jsonify({"message": "Invalid token."})
            res.status = 401
            return res
        try:
            req = []
            content = request.get_json(silent=True)
            logging.info(f"/api/model_view content: {content}")
            for i in content:
                r = {}
                if "Раздел" in i:
                    r["Раздел"] = i["Раздел"]
                else:
                    raise
                if "Марка" in i:
                    r["Марка"] = i["Марка"]
                else:
                    r["Марка"] = ""
                if "Модель" in i:
                    r["Модель"] = i["Модель"]
                else:
                    r["Модель"] = ""

                req.append(r)
        except:
            res = jsonify(
                {"success": False, "error": "Неверный формат параметров запроса."})
            res.status = 400
            return res
        ans = []
        for r in req:
            models = getModels(
                mark=r["Марка"],
                model=r["Модель"],
                section=r["Раздел"],
            )
            for model_index in range(len(models)):
                models[model_index] = models[model_index]["data"]
            # logging.log(f"{models}")
            # print(models)
            ans.append(models)
        return jsonify({"success": True, "models": ans})
    except Exception as e:
        logging.warning(f"{content} 500 error {e}")
        res = jsonify(
            {"success": False, "error": "Внутренняя ошибка сервера."})
        res.status = 500
        return res
