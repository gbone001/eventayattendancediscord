import psycopg2
from config import DB_CONFIG

def get_conn():
    return psycopg2.connect(**DB_CONFIG)

def log_event(event_id, name, message_id, timestamp):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO events (event_id, name, message_id, timestamp)
        VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING;
    """, (event_id, name, message_id, timestamp))
    conn.commit()
    cur.close()
    conn.close()

def log_response(event_id, username, user_id, status, responded_at):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO responses (event_id, username, user_id, status, responded_at)
        VALUES (%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING;
    """, (event_id, username, user_id, status, responded_at))
    conn.commit()
    cur.close()
    conn.close()
