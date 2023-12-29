import logging
from flask import jsonify, request
from flask_cors import cross_origin
import repository
from service.ai import getResults, setAiRequest, shortAiTaktor, shortAiTrailer
import service


@cross_origin()
def ai():
    try:
        if request.headers.get('Authorization') != "Bearer a5ZTI2LWUxOTMtNDU4Yy04Y2Fh":
            res = jsonify({"message": "Invalid token."})
            res.status = 401
            return res
        try:
            content = request.get_json(silent=True)
            logging.info(f"/api/ai content: {content}")
            work_type = int(content["workType"])
            if 10 <= work_type <= 13:
                soil_background = 0
            else:
                soil_background = int(content["soilBackground"])
            plot_size = float(content["plotSize"]) * 10000 
            location = content["location"].split(",")
            lat = float(location[0])
            lon = float(location[1])
            if "message" in content:
                is_message_required = content["message"]
            else:
                is_message_required = True
            if "additionalParams" in content:
                additionalParams = content["additionalParams"]
            else:
                additionalParams = {}

            if "pushHistory" in content:
                pushHistory = content["pushHistory"]
            else:
                pushHistory = []
        except:
            res = jsonify(
                {"success": False, "error": "Неверный формат параметров запроса."})
            res.status = 400
            return res
        request_id = setAiRequest(
            soil_background, work_type, plot_size, lat, lon, additionalParams, pushHistory=pushHistory, is_message_required=is_message_required)
        service.run_response_subprocess(request_id)
        return jsonify({"success": True, "id": request_id})
    except Exception as e:
        logging.warning(f"{content} 500 error {e}")
        res = jsonify(
            {"success": False, "error": "Внутренняя ошибка сервера."})
        res.status = 500
        return res


@cross_origin()
def results():
    try:
        if request.headers.get('Authorization') != "Bearer a5ZTI2LWUxOTMtNDU4Yy04Y2Fh":
            res = jsonify({"message": "Invalid token."})
            res.status = 401
            return res
        try:
            content = request.get_json(silent=True)
            logging.info(f"/api/results content: {content}")
            try:
                id = int(content["id"])
                try:
                    trailer_amount = int(content["trailer_amount"])
                    if not 1 <= trailer_amount <= 4:
                        trailer_amount = 4
                except:
                    trailer_amount = 4
            except:
                id = request.args.get('id')
                if id == None:
                    raise
        except:
            res = jsonify(
                {"success": False, "error": "Неверный формат параметров запроса."})
            res.status = 400
            return res
        data_res = repository.get_response(id)
        return jsonify({"success": True, "items": data_res["ans"], "status": data_res["status"]})
    except Exception as e:
        logging.warning(f"{content} 500 error {e}")
        res = jsonify(
            {"success": False, "error": "Внутренняя ошибка сервера."})
        res.status = 500
        return res


SHORTAI_tractor = 0
SHORTAI_TRAILER = 1


@cross_origin()
def shortai():
    try:
        if request.headers.get('Authorization') != "Bearer a5ZTI2LWUxOTMtNDU4Yy04Y2Fh":
            res = jsonify({"message": "Invalid token."})
            res.status = 401
            return res
        try:
            content = request.get_json(silent=True)
            logging.info(f"/api/shortai content: {content}")
            if "tractor_id" in content:
                id = content["tractor_id"]
                req_type = SHORTAI_tractor
            else:
                id = content["trailer_id"]
                req_type = SHORTAI_TRAILER
            location = content["location"].split(",")
            lat = float(location[0])
            lon = float(location[1])
        except:
            res = jsonify(
                {"success": False, "error": "Неверный формат параметров запроса."})
            res.status = 400
            return res
        if req_type == 0:
            ans = shortAiTaktor(id, lat, lon)
            return jsonify({"success": True, "trailers": ans, "status": "done"})
        elif req_type == 1:
            ans = shortAiTrailer(id, lat, lon)
            return jsonify({"success": True, "tractor": ans, "status": "done"})
    except Exception as e:
        logging.warning(f"{content} 500 error {e}")
        res = jsonify(
            {"success": False, "error": "Внутренняя ошибка сервера."})
        res.status = 500
        return res
