import os
import random
from datetime import datetime
import pytz
import discord
from discord.ext import tasks

# ================= CONFIG =================

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
ALLOWED_ROLE_ID = int(os.getenv("ALLOWED_ROLE_ID"))
EXCLUDED_ROLE_IDS = list(map(int, os.getenv("EXCLUDED_ROLE_IDS", "").split(",")))

TIMEZONE = pytz.timezone("Asia/Kolkata")

POST_HOUR = 12     # 🔁 change to 12 for testing
POST_MINUTE = 0     # 🔁 change to current minute for testing
WINDOW_MINUTES = 5  # safe window

# =========================================

intents = discord.Intents.default()
intents.members = True

client = discord.Client(intents=intents)

last_posted_date = None  # memory-safe daily lock


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    daily_couple.start()


@tasks.loop(minutes=1)
async def daily_couple():
    global last_posted_date

    now = datetime.now(TIMEZONE)

    # Time window check
    if not (
        now.hour == POST_HOUR
        and POST_MINUTE <= now.minute < POST_MINUTE + WINDOW_MINUTES
    ):
        return

    today = now.strftime("%Y-%m-%d")
    if last_posted_date == today:
        return  # already posted today

    guild = client.get_guild(GUILD_ID)
    channel = guild.get_channel(CHANNEL_ID)

    allowed_role = guild.get_role(ALLOWED_ROLE_ID)
    excluded_roles = {guild.get_role(rid) for rid in EXCLUDED_ROLE_IDS}

    members = []
    for m in allowed_role.members:
        if m.bot:
            continue
        if any(r in excluded_roles for r in m.roles):
            continue
        members.append(m)

    if len(members) < 2:
        print("Not enough members to pair")
        return

    pair = random.sample(members, 2)

    message = (
        "💖 **Today's Couple Alert!** 💖\n\n"
        f"{pair[0].mention} × {pair[1].mention}\n\n"
        "✨ Destiny has spoken. Be nice to each other today ✨\n\n"
        "⏰ *New couple drops tomorrow at 10 AM IST*"
    )

    await channel.send(message)
    last_posted_date = today
    print("Couple posted successfully")


client.run(TOKEN)

