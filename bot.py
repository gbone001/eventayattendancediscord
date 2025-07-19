import discord
from discord.ext import commands
from config import BOT_TOKEN
from db import log_event, log_response
from datetime import datetime
import attendance

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.reactions = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.event
async def on_message(message):
    if message.author.name == "Apollo" and message.embeds:
        embed = message.embeds[0]
        event_id = f"{message.id}"
        event_name = embed.title
        log_event(event_id, event_name, message.id, datetime.utcnow())
    await bot.process_commands(message)

@bot.event
async def on_raw_reaction_add(payload):
    event_id = str(payload.message_id)
    user = bot.get_user(payload.user_id)
    emoji_map = {"✅": "Going", "❌": "Not Going", "🤔": "Tentative"}
    status = emoji_map.get(payload.emoji.name)
    if user and status:
        log_response(event_id, user.name, user.id, status, datetime.utcnow())

# Load attendance commands
attendance.setup(bot)

bot.run(BOT_TOKEN)
