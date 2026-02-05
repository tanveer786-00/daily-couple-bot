import discord
from discord.ext import tasks
import os
import random
from datetime import datetime
import pytz

# ========== ENV VARIABLES ==========
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
ALLOWED_ROLE_ID = int(os.getenv("ALLOWED_ROLE_ID"))

# Optional (can be empty string)
EXCLUDED_ROLE_IDS = os.getenv("EXCLUDED_ROLE_IDS", "")
EXCLUDED_ROLE_IDS = [
    int(rid) for rid in EXCLUDED_ROLE_IDS.split(",") if rid.strip().isdigit()
]

TIMEZONE = pytz.timezone("Asia/Kolkata")

# ========== DISCORD SETUP ==========
intents = discord.Intents.default()
intents.members = True

client = discord.Client(intents=intents)

last_post_date = None  # in-memory, resets only if container restarts


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    daily_couple.start()


@tasks.loop(minutes=1)
async def daily_couple():
    global last_post_date

    now = datetime.now(TIMEZONE)

    # 🔹 CHANGE THIS FOR TESTING
    TARGET_HOUR = 12   # change to 10 later
    TARGET_MINUTE = 30  # change to 0 later

    # Only run at exact minute
    if now.hour != TARGET_HOUR or now.minute != TARGET_MINUTE:
        return

    today = now.date()
    if last_post_date == today:
        return  # already posted today

    guild = client.get_guild(GUILD_ID)
    channel = guild.get_channel(CHANNEL_ID)

    allowed_role = guild.get_role(ALLOWED_ROLE_ID)
    excluded_roles = [guild.get_role(rid) for rid in EXCLUDED_ROLE_IDS]

    members = []

    for member in allowed_role.members:
        if member.bot:
            continue
        if any(role in member.roles for role in excluded_roles):
            continue
        members.append(member)

    if len(members) < 2:
        await channel.send("❌ Not enough members to pick a couple today.")
        return

    pair = random.sample(members, 2)

    message = (
        "💖 **Today's Couple Alert!** 💖\n\n"
        f"{pair[0].mention} ❤️ {pair[1].mention}\n\n"
        "✨ Destiny has spoken. Be wholesome ✨"
    )

    await channel.send(message)
    last_post_date = today
    print("✅ Couple posted successfully")


client.run(TOKEN)
