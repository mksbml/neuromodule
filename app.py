# -*- coding: utf-8 -*-

import logging
from pkg.config.config import KEY_FILENAME, CERT_FILENAME, PATH

logging.basicConfig(level=logging.INFO, filename=PATH + 'log.log',filemode="w",
                    format="%(asctime)s %(levelname)s %(message)s")
logging.info("Starting application")

from flask_cors import CORS
from datetime import timedelta
from flask import session, Flask
# from frontend.router import startFrontRouting
from web.router import startProdRouting
from pkg.cache.cache import categorized_harvesters
from pkg.cache import categorized_trailers
import catboost

app = Flask(__name__)
cors = CORS(app, allow_headers=[
            'Content-Type', 'Authorization'], origins='*', methods='POST, GET')

# startFrontRouting(app)
startProdRouting(app)

logging.info(f"categorized_trailers {categorized_trailers}")
logging.info(f"categorized_harvesters {categorized_harvesters}")
context = (PATH+CERT_FILENAME, PATH+KEY_FILENAME)#certificate and key files

app.config['SECRET_KEY'] = 'hILWLYnNqt554RyU'
@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=5)

app.run(host='0.0.0.0', port=443, ssl_context=context)
# app.run(host='0.0.0.0', port=443, ssl_context=context, threaded=False, processes = 5)