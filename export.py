import csv
from db import get_conn

async def export_full_attendance_csv(bot, guild, event_id: str, output_file: str = "attendance_full_export.csv"):
    conn = get_conn()
    cur = conn.cursor()

    # Fetch responses and event name
    cur.execute("""
        SELECT username, status FROM responses WHERE event_id = %s;
    """, (event_id,))
    response_rows = cur.fetchall()

    cur.execute("SELECT name FROM events WHERE event_id = %s;", (event_id,))
    event = cur.fetchone()
    conn.close()

    if not event:
        print(f"❗ Event not found for ID {event_id}")
        return

    responded_users = {username: status for username, status in response_rows}
    all_guild_users = [member.name for member in guild.members if not member.bot]

    # Build combined attendance
    combined_rows = []
    for user in all_guild_users:
        if user in responded_users:
            combined_rows.append({
                "event_name": event[0],
                "username": user,
                "response": responded_users
