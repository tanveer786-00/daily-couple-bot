import os
import random
from datetime import datetime
import pytz

import discord
from discord.ext import commands, tasks

# ========== CONFIG ==========
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
ALLOWED_ROLE_ID = int(os.getenv("ALLOWED_ROLE_ID"))
EXCLUDED_ROLE_IDS = list(map(int, os.getenv("EXCLUDED_ROLE_IDS", "").split(","))) if os.getenv("EXCLUDED_ROLE_IDS") else []

TIMEZONE = pytz.timezone("Asia/Kolkata")
POST_HOUR = 10  # 10 AM IST
WINDOW_MINUTES = 10  # 10:00–10:09 window
# ============================

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

last_post_date = None


def pick_random_couple(guild: discord.Guild):
    allowed_role = guild.get_role(ALLOWED_ROLE_ID)
    excluded_roles = [guild.get_role(rid) for rid in EXCLUDED_ROLE_IDS]

    members = []
    for m in allowed_role.members:
        if m.bot:
            continue
        if any(r in m.roles for r in excluded_roles if r):
            continue
        members.append(m)

    if len(members) < 2:
        return None

    return random.sample(members, 2)


async def send_couple():
    global last_post_date

    guild = bot.get_guild(GUILD_ID)
    if not guild:
        return

    channel = guild.get_channel(CHANNEL_ID)
    if not channel:
        return

    pair = pick_random_couple(guild)
    if not pair:
        return

    msg = (
        "💖 **Today's Random Couple!** 💖\n\n"
        f"✨ {pair[0].mention}  ×  {pair[1].mention} ✨\n\n"
        "Be wholesome & kind today 😊\n"
        "⏰ Next couple drops tomorrow at **10:00 AM IST**"
    )

    await channel.send(msg)
    last_post_date = datetime.now(TIMEZONE).date()


@tasks.loop(minutes=1)
async def daily_couple():
    global last_post_date

    now = datetime.now(TIMEZONE)

    if now.hour == POST_HOUR and 0 <= now.minute < WINDOW_MINUTES:
        if last_post_date != now.date():
            await send_couple()


@daily_couple.before_loop
async def before_daily():
    await bot.wait_until_ready()


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    if not daily_couple.is_running():
        daily_couple.start()


# ===== TEST COMMAND (REAL POST) =====
@bot.command()
async def testcouple(ctx):
    await send_couple()
    await ctx.send("✅ Test couple posted!")


bot.run(TOKEN)





