from web.handlers.ai import ai, results, shortai
from web.handlers.stats import stats
from web.handlers.notify import notify
from web.handlers.json_db import updatedb, deleteFromDb, getFromDb
from web.handlers.model import model_view, save_model
def startProdRouting(app):
    app.add_url_rule('/api/ai', view_func=ai, methods=['POST'])
    app.add_url_rule('/api/shortai', view_func=shortai, methods=['POST'])
    app.add_url_rule('/api/results', view_func=results,
                     methods=['GET', 'POST'])
    
    app.add_url_rule('/api/stats', view_func=stats, methods=['GET', 'POST'])

    app.add_url_rule('/api/notify',
                     view_func=notify, methods=['POST'])

    app.add_url_rule('/api/updatedb', view_func=updatedb, methods=['POST'])
    app.add_url_rule('/api/deleteFromDb',
                     view_func=deleteFromDb, methods=['POST'])
    app.add_url_rule('/api/getFromDb',
                     view_func=getFromDb, methods=['POST'])
    
    app.add_url_rule('/api/models', view_func=model_view, methods=['POST'])
    
    app.add_url_rule('/api/save_model', view_func=save_model, methods=['POST'])