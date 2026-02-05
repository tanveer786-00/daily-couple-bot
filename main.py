import os
import random
from datetime import datetime
import pytz
import discord
from discord.ext import tasks, commands

# ================= CONFIG =================

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
ALLOWED_ROLE_ID = int(os.getenv("ALLOWED_ROLE_ID"))
EXCLUDED_ROLE_IDS = list(map(int, os.getenv("EXCLUDED_ROLE_IDS", "").split(",")))

TIMEZONE = pytz.timezone("Asia/Kolkata")

POST_HOUR = 10
POST_MINUTE = 0
WINDOW_MINUTES = 5

# =========================================

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

last_posted_date = None


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    daily_couple.start()


async def send_couple():
    guild = await bot.fetch_guild(GUILD_ID)
    channel = await bot.fetch_channel(CHANNEL_ID)

    allowed_role = guild.get_role(ALLOWED_ROLE_ID)
    excluded_roles = {guild.get_role(rid) for rid in EXCLUDED_ROLE_IDS}

    members = []
    async for m in guild.fetch_members(limit=None):
        if m.bot:
            continue
        if allowed_role not in m.roles:
            continue
        if any(r in excluded_roles for r in m.roles):
            continue
        members.append(m)

    if len(members) < 2:
        await channel.send("❌ Not enough members to create a couple.")
        return

    pair = random.sample(members, 2)

    message = (
        "💖 **Today's Couple Alert!** 💖\n\n"
        f"{pair[0].mention} × {pair[1].mention}\n\n"
        "✨ Destiny has spoken. Be nice to each other today ✨\n\n"
        "⏰ *New couple drops tomorrow at 10 AM IST*"
    )

    await channel.send(message)
    print("Couple sent successfully")


@tasks.loop(minutes=1)
async def daily_couple():
    global last_posted_date

    now = datetime.now(TIMEZONE)

    if not (
        now.hour == POST_HOUR
        and POST_MINUTE <= now.minute < POST_MINUTE + WINDOW_MINUTES
    ):
        return

    today = now.strftime("%Y-%m-%d")
    if last_posted_date == today:
        return

    await send_couple()
    last_posted_date = today


# 🔥 MANUAL TEST COMMAND
@bot.command()
@commands.has_permissions(administrator=True)
async def testcouple(ctx):
    await send_couple()
    await ctx.send("✅ Test couple sent!")


bot.run(TOKEN)


