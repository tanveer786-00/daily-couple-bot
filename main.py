import os
import random
import discord
from discord.ext import commands, tasks
from datetime import datetime
import pytz

# ===== ENV =====
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
ALLOWED_ROLE_ID = int(os.getenv("ALLOWED_ROLE_ID"))
EXCLUDED_ROLE_IDS = os.getenv("EXCLUDED_ROLE_IDS", "")
EXCLUDED_ROLE_IDS = [int(r) for r in EXCLUDED_ROLE_IDS.split(",") if r]

TIMEZONE = pytz.timezone("Asia/Kolkata")

# ===== BOT =====
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

last_post_date = None


def pick_random_couple(guild):
    allowed_role = guild.get_role(ALLOWED_ROLE_ID)
    excluded_roles = [guild.get_role(rid) for rid in EXCLUDED_ROLE_IDS]

    members = []
    for m in allowed_role.members:
        if m.bot:
            continue
        if any(role in m.roles for role in excluded_roles):
            continue
        members.append(m)

    if len(members) < 2:
        return None

    return random.sample(members, 2)


async def send_couple(guild):
    global last_post_date

    guild = bot.get_guild(GUILD_ID)
    channel = guild.get_channel(CHANNEL_ID)

    pair = pick_random_couple(guild)
    if not pair:
        return

    msg = (
        "💖 **Today's Random Couple!** 💖\n\n"
        f"✨ {pair[0].mention} × {pair[1].mention} ✨\n\n"
        "Be wholesome, be kind 😌\n"
        "⏰ Next couple drops tomorrow at **10:00 AM IST**"
    )

    await channel.send(msg)
    last_post_date = datetime.now(TIMEZONE).date()


@tasks.loop(minutes=1)
async def daily_couple():
    global last_post_date

    now = datetime.now(TIMEZONE)

    if now.hour == 12 and 0 <= now.minute <= 20:
        if last_post_date != now.date():
            guild = bot.get_guild(GUILD_ID)
if guild:
    await send_couple(guild)



@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    if not daily_couple.is_running():
        daily_couple.start()


@bot.command()
async def testcouple(ctx):
    await send_couple(ctx.guild)
    await ctx.send("✅ Test couple posted!")


bot.run(TOKEN)



