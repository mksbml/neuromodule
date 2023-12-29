import json
from pkg.db.db import ConnectDB

def create_response(req_id):
    conn = ConnectDB()
    cur = conn.cursor()
    cur.execute(
        f"INSERT INTO response (id, status) VALUES ({req_id}, 'data processing')")
    conn.commit()
    cur.close()
    conn.close()
    return

def update_response(status, req_id, ans=[]):
    conn = ConnectDB()
    cur = conn.cursor()
    cur.execute(
        f"UPDATE response SET status = %s, ans = %s WHERE id = %s", (status, json.dumps(ans), req_id))
    conn.commit()
    cur.close()
    conn.close()
    return

def get_response(req_id):
    conn = ConnectDB()
    cur = conn.cursor()
    cur.execute(
        f"select * from response where id = %s", (req_id,))
    data = cur.fetchone()
    cur.close()
    conn.close()
    return data