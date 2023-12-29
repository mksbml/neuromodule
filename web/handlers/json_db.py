import logging
import os
from flask import jsonify, request
from flask_cors import cross_origin
from pkg.cache.cache import save_machinery, remove_machinery
from repository.item_impl import get_item

@cross_origin()
def updatedb():
    try:
        if request.headers.get('Authorization') != "Bearer a5ZTI2LWUxOTMtNDU4Yy04Y2Fh":
            res = jsonify({"message": "Invalid token."})
            res.status = 401
            return res
        try:
            content = request.get_json(silent=True)
            logging.info(f"/api/updatedb content: {content}")
            for i in content:
                _ = i["ID"]
        except:
            res = jsonify(
                {"success": False, "error": "Неверный формат параметров запроса."})
            res.status = 400
            return res
        for data in content:
            save_machinery(data)

        return jsonify({"success": True})
    except:
        res = jsonify(
            {"success": False, "error": "Внутренняя ошибка сервера."})
        res.status = 500
        return res

@cross_origin()
def getFromDb():
    try:
        if request.headers.get('Authorization') != "Bearer a5ZTI2LWUxOTMtNDU4Yy04Y2Fh":
            res = jsonify({"message": "Invalid token."})
            res.status = 401
            return res
        try:
            content = request.get_json(silent=True)
            logging.info(f"/api/getFromDb content: {content}")
            for i in content:
                _ = int(i["ID"])
        except:
            res = jsonify(
                {"success": False, "error": "Неверный формат параметров запроса."})
            res.status = 400
            return res
        ans = []
        for row in content:
            try:
                ans.append(get_item(row["ID"]))
            except:
                ans.append({"success":False, "error": "Не найдено"})

        return jsonify({"success": True, "items": ans})
    except Exception as e:
        logging.warning(f"{content} 500 error {e}")
        res = jsonify(
            {"success": False, "error": "Внутренняя ошибка сервера."})
        res.status = 500
        return res


@cross_origin()
def deleteFromDb():
    try:
        if request.headers.get('Authorization') != "Bearer a5ZTI2LWUxOTMtNDU4Yy04Y2Fh":
            res = jsonify({"message": "Invalid token."})
            res.status = 401
            return res
        try:
            content = request.get_json(silent=True)
            logging.info(f"/api/deleteFromDb content: {content}")
            id = content["ID"]
        except:
            res = jsonify(
                {"success": False, "error": "Неверный формат параметров запроса."})
            res.status = 400
            return res


        remove_machinery(id)

            
        return jsonify({"success": True})
    except:
        res = jsonify(
            {"success": False, "error": "Данный id отсутствует"})
        res.status = 422
        return res
