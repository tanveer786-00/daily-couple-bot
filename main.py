import os
import random
from datetime import datetime, time

import discord
from discord.ext import commands, tasks
import pytz

# ─── CONFIG ──────────────────────────────────────────────
TOKEN = os.getenv("DISCORD_TOKEN")

GUILD_ID = int(os.getenv("GUILD_ID"))
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
ALLOWED_ROLE_ID = int(os.getenv("ALLOWED_ROLE_ID"))
EXCLUDED_ROLE_IDS = list(map(int, os.getenv("EXCLUDED_ROLE_IDS", "").split(",")))

TIMEZONE = pytz.timezone("Asia/Kolkata")

POST_HOUR = 12     # 10 AM IST (change if needed)
POST_MINUTE = 0

# ─── BOT SETUP ───────────────────────────────────────────
intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

last_post_date = None


# ─── HELPER FUNCTIONS ────────────────────────────────────
def pick_random_couple(guild: discord.Guild):
    allowed_role = guild.get_role(ALLOWED_ROLE_ID)
    excluded_roles = {guild.get_role(rid) for rid in EXCLUDED_ROLE_IDS}

    if not allowed_role:
        print("❌ Allowed role not found")
        return None

    members = [
        m for m in allowed_role.members
        if not m.bot
        and not any(r in excluded_roles for r in m.roles)
    ]

    if len(members) < 2:
        print("❌ Not enough valid members")
        return None

    return random.sample(members, 2)


async def send_couple(guild: discord.Guild):
    global last_post_date

    channel = guild.get_channel(CHANNEL_ID)
    if not channel:
        print("❌ Channel not found")
        return

    pair = pick_random_couple(guild)
    if not pair:
        return

    message = (
        "💖 **Today's Random Couple!** 💖\n\n"
        f"✨ {pair[0].mention} × {pair[1].mention} ✨\n\n"
        "Be wholesome & kind today 🥰\n"
        "⏰ Next couple drops tomorrow at **10:00 AM IST**"
    )

    await channel.send(message)
    last_post_date = datetime.now(TIMEZONE).date()
    print("✅ Couple posted")


# ─── DAILY TASK ──────────────────────────────────────────
@tasks.loop(minutes=1)
async def daily_couple():
    global last_post_date

    now = datetime.now(TIMEZONE)

    if now.hour == POST_HOUR and 0 <= now.minute <= 59:
        if last_post_date != now.date():
            guild = bot.get_guild(GUILD_ID)
            if guild:
                await send_couple(guild)


@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    if not daily_couple.is_running():
        daily_couple.start()


# ─── TEST COMMAND ────────────────────────────────────────
@bot.command()
async def testcouple(ctx):
    await send_couple(ctx.guild)
    await ctx.send("✅ Test couple posted!")


bot.run(TOKEN)




