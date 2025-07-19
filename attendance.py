import csv
from collections import defaultdict
from discord import Embed
from db import get_conn

def setup(bot):
    @bot.command()
    async def attendance(ctx, event_id: str):
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT username, status FROM responses WHERE event_id = %s;
        """, (event_id,))
        rows = cur.fetchall()
        cur.execute("SELECT name FROM events WHERE event_id = %s;", (event_id,))
        event = cur.fetchone()
        conn.close()

        if not event:
            await ctx.send("❗ Event not found.")
            return

        stats = defaultdict(list)
        for user, status in rows:
            stats[status].append(user)

        all_members = [m.name for m in ctx.guild.members if not m.bot]
        responded = {user for user, _ in rows}
        not_responded = [u for u in all_members if u not in responded]

        embed = Embed(title=f"📋 {event[0]} Attendance", color=0x00b2ff)
        embed.add_field(name="✅ Going", value="\n".join(stats["Going"]) or "None", inline=False)
        embed.add_field(name="❌ Not Going", value="\n".join(stats["Not Going"]) or "None", inline=False)
        embed.add_field(name="🤔 Tentative", value="\n".join(stats["Tentative"]) or "None", inline=False)
        embed.add_field(name="🤷 No Response", value="\n".join(not_responded) or "None", inline=False)
        await ctx.send(embed=embed)

    @bot.command()
    async def who_is_going(ctx, event_id: str):
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT username FROM responses WHERE event_id = %s AND status = 'Going';
        """, (event_id,))
        users = [row[0] for row in cur.fetchall()]
        cur.execute("SELECT name FROM events WHERE event_id = %s;", (event_id,))
        event = cur.fetchone()
        conn.close()

        if not event:
            await ctx.send("❗ Event not found.")
            return

        embed = Embed(
            title=f"✅ Attendees for {event[0]}",
            description="\n".join(users) or "No confirmed attendees yet.",
            color=0x43b581
        )
        await ctx.send(embed=embed)
