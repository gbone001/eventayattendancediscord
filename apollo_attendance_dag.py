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

import requests

DISCORD_WEBHOOK = "https://discord.com/api/webhooks/XXXX/XXXX"

def send_discord_alert(context):
    task_name = context.get("task_instance").task_id
    dag_name = context.get("dag").dag_id
    error_msg = context.get("exception")

    message = {
        "username": "Apollo Bot Monitor",
        "content": f"🚨 Task **{task_name}** in DAG **{dag_name}** failed!\n```\n{error_msg}\n```"
    }

    requests.post(DISCORD_WEBHOOK, json=message)
from alerts import send_discord_alert

export_attendance = PythonOperator(
    task_id="export_attendance",
    python_callable=run_export,
    on_failure_callback=send_discord_alert
)

backup_csv = BashOperator(
    task_id="backup_csv",
    bash_command=f"elastio backup {EXPORT_PATH} --tag apollo-{EVENT_ID}",
    on_failure_callback=send_discord_alert
)
with DAG(
    dag_id="apollo_attendance_export_dag",
    start_date=datetime(2025,7,20),
    schedule_interval="30 23 * * *",
    catchup=False,
    default_args={
        "on_failure_callback": send_discord_alert
    }
) as dag:
