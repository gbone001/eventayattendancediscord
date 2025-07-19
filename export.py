import csv
from db import get_conn

def export_attendance_csv(event_id: str, output_file: str = "attendance_export.csv"):
    conn = get_conn()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT e.name, r.username, r.status, r.responded_at
        FROM responses r
        JOIN events e ON r.event_id = e.event_id
        WHERE r.event_id = %s
    """, (event_id,))
    rows = cur.fetchall()
    conn.close()

    with open(output_file, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["event_name", "username", "response", "responded_at"])
        for row in rows:
            writer.writerow(row)

    print(f"✅ Attendance CSV exported to {output_file}")
