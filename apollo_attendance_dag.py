from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime
import os

EVENT_ID = "your_event_id"  # You can update dynamically later
EXPORT_PATH = f"/apollo_bot/exports/attendance_{EVENT_ID}.csv"

def run_export():
    import asyncio
    from discord.ext import commands
    from export import export_full_attendance_csv

    intents = commands.Intents.default()
    intents.members = True
    bot = commands.Bot(command_prefix="!", intents=intents)

    @bot.event
    async def on_ready():
        guild = discord.utils.get(bot.guilds)  # Assumes bot is in one guild
        await export_full_attendance_csv(bot, guild, event_id=EVENT_ID, output_file=EXPORT_PATH)
        await bot.close()

    asyncio.run(bot.start("your_bot_token"))

with DAG("apollo_attendance_export_dag", start_date=datetime(2025,7,20), schedule_interval="30 23 * * *", catchup=False) as dag:

    export_attendance = PythonOperator(
        task_id="export_attendance",
        python_callable=run_export
    )

    backup_csv = BashOperator(
        task_id="backup_csv",
        bash_command=f"elastio backup {EXPORT_PATH} --tag apollo-{EVENT_ID}"
    )

    export_attendance >> backup_csv
