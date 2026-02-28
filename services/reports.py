import json
import datetime
import os
from sys import path

path.append(os.path.dirname(__file__))

from database.db import get_connection

def save_report(user_id, query_text, res):
    # save query history to db so we can trace it later
    conn = get_connection()
    c = conn.cursor()
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    s_str = json.dumps(res)
    
    c.execute("INSERT INTO reports (user_id, query_text, result_summary, timestamp) VALUES (?, ?, ?, ?)", 
        (user_id, query_text, s_str, timestamp))
    
    conn.commit()
    conn.close()

def get_user_reports(user_id, is_admin=False):
    # get reports, admins see all
    conn = get_connection()
    c = conn.cursor()
    
    if is_admin:
        c.execute("SELECT * FROM reports ORDER BY timestamp DESC")
    else:
        c.execute("SELECT * FROM reports WHERE user_id = ? ORDER BY timestamp DESC", (user_id,))
        
    rows = c.fetchall()
    conn.close()
    
    reports = []
    for row in rows:
        reports.append({
            "id": row['id'],
            "user_id": row['user_id'],
            "query_text": row['query_text'],
            "result_summary": json.loads(row['result_summary']),
            "timestamp": row['timestamp']
        })
        
    return reports
