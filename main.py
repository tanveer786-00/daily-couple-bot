import discord
from discord.ext import tasks
import random
import json
import os
from datetime import datetime, timedelta
import pytz
import os
from datetime import datetime

if os.path.exists("today.txt"):
    os.remove("today.txt")

TOKEN = os.getenv("DISCORD_TOKEN")

GUILD_ID = int(os.getenv("GUILD_ID"))
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
ALLOWED_ROLE_ID = int(os.getenv("ALLOWED_ROLE_ID"))
EXCLUDED_ROLE_IDS = list(map(int, os.getenv("EXCLUDED_ROLE_IDS").split(",")))

TIMEZONE = pytz.timezone("Asia/Kolkata")
COOLDOWN_DAYS = int(os.getenv("COOLDOWN_DAYS", "30"))

intents = discord.Intents.default()
intents.members = True
intents.message_content = False

client = discord.Client(intents=intents)

DATA_FILE = "couples.json"


def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    daily_couple.start()


@tasks.loop(minutes=1)
async def daily_couple():
    now = datetime.now(TIMEZONE)

if not (now.hour == 11 and 30 <= now.minute <= 35):
    return


    if os.path.exists("today.txt"):
        return

    with open("today.txt", "w") as f:
        f.write(now.strftime("%Y-%m-%d"))


    data = load_data()
    cutoff = datetime.now(TIMEZONE) - timedelta(days=COOLDOWN_DAYS)

    recent_pairs = {
        tuple(pair["pair"])
        for pair in data
        if datetime.fromisoformat(pair["date"]) > cutoff
    }

    guild = client.get_guild(GUILD_ID)
    channel = guild.get_channel(CHANNEL_ID)

    allowed_role = guild.get_role(ALLOWED_ROLE_ID)
    excluded_roles = [guild.get_role(rid) for rid in EXCLUDED_ROLE_IDS]

    members = [
        m for m in allowed_role.members
        if not m.bot and not any(r in m.roles for r in excluded_roles)
    ]

    if len(members) < 2:
        return

    tries = 0
    while tries < 20:
        pair = random.sample(members, 2)
        pair_ids = tuple(sorted([pair[0].id, pair[1].id]))
        if pair_ids not in recent_pairs:
            break
        tries += 1
    else:
        return

    message = (
        "💖 **Today's Couple Alert!** 💖\n\n"
        f"🌸 {pair[0].mention} × {pair[1].mention} 🌸\n\n"
        "Destiny has spoken. Be nice to each other today 😌✨\n\n"
        "🔁 *New couple drops tomorrow at 10 AM IST*"
    )

    await channel.send(message)

    data.append({
        "pair": list(pair_ids),
        "date": datetime.now(TIMEZONE).isoformat()
    })
    save_data(data)


@daily_couple.before_loop
async def before_daily():
    await client.wait_until_ready()
    if os.path.exists("today.txt"):
        with open("today.txt") as f:
            if f.read().strip() != datetime.now(TIMEZONE).strftime("%Y-%m-%d"):
                os.remove("today.txt")

daily_couple.start()

client.run(TOKEN)


