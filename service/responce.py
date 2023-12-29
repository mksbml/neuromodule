import threading
import repository
from service.ai import * 

def run_response_subprocess(req_id):
    t1 = threading.Thread(target=response_subprocess, args=(req_id,), daemon=True)
    t1.start()

def response_subprocess(req_id):
    repository.create_response(req_id=req_id)
    try:
        ans = getResults(req_id=req_id, trailer_amount=1)
        repository.update_response(status="done", ans=ans, req_id=req_id)
    except Exception as e:
        logging.exception(f'responce_sub error {e}')
        repository.update_response(status="failed", req_id=req_id)