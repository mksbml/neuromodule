
import logging
from flask import jsonify, request
from flask_cors import cross_origin
from repository.request_impl import addNotify


@cross_origin()
def notify():
    try:
        if request.headers.get('Authorization') != "Bearer a5ZTI2LWUxOTMtNDU4Yy04Y2Fh":
            res = jsonify({"message": "Invalid token."})
            res.status = 401
            return res
        try:
            content = request.get_json(silent=True)
            logging.info(f"/api/notify content: {content}")
            requestID = int(content["requestID"])
            itemIds = list(map(int, content["itemIds"]))
        except:
            res = jsonify(
                {"success": False, "error": "Неверный формат параметров запроса."})
            res.status = 400
            return res

        for item_id in itemIds:
            addNotify(requestID, item_id)

        return jsonify({"success": True})
    except:
        res = jsonify(
            {"success": False, "error": "Внутренняя ошибка сервера."})
        res.status = 500
        return res
