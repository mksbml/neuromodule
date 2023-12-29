import logging
from flask import jsonify, request
from flask_cors import cross_origin
from repository.request_impl import getStats


@cross_origin()
def stats():
    try:
        if request.headers.get('Authorization') != "Bearer a5ZTI2LWUxOTMtNDU4Yy04Y2Fh":
            res = jsonify({"message": "Invalid token."})
            res.status = 401
            return res
        try:
            content = request.get_json(silent=True)
            logging.info(f"/api/stats content: {content}")
            start = content["start"]
            end = content["end"]
        except:
            res = jsonify(
                {"success": False, "error": "Неверный формат параметров запроса."})
            res.status = 400
            return res

        count = getStats(start, end)["count"]

        return jsonify({"success": True, "count": count})
    except:
        res = jsonify(
            {"success": False, "error": "Внутренняя ошибка сервера."})
        res.status = 500
        return res
