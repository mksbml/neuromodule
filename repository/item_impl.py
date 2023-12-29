import json
from pkg.db.db import ConnectDB


def get_items():
    conn = ConnectDB()
    cur = conn.cursor()
    cur.execute("SELECT * FROM item")
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

def get_item(id):
    conn = ConnectDB()
    cur = conn.cursor()
    cur.execute(f"SELECT data FROM item WHERE id = {id}")
    data = cur.fetchone()
    data = data["data"]
    cur.close()
    conn.close()
    return data

def write_item(data):
    conn = ConnectDB()
    cur = conn.cursor()
    id = data["ID"]
    cur.execute(f"SELECT COUNT(*) FROM item WHERE id = {id}")
    cnt = cur.fetchone()["count"]
    if cnt == 0:
        cur.execute(f"INSERT INTO item (id, data) VALUES ({id}, '{json.dumps(data)}'::json)")
    else:
        cur.execute(f"UPDATE item SET id = {id}, data = '{json.dumps(data)}'::json WHERE id = {id}")
    cur.close()
    conn.commit()
    conn.close()
    return data

def remove_item(id):
    conn = ConnectDB()
    cur = conn.cursor()
    cur.execute(f"DELETE FROM item WHERE id={id} RETURNING *")
    if cur.fetchone() == None:
        cur.close()
        conn.close()
        raise
    conn.commit()
    cur.close()
    conn.close()
