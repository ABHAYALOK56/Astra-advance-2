import discord
from discord.ext import commands
import json, os, asyncio, sys
from flask import Flask
from threading import Thread

# ================== PREFIX FUNCTIONS ================== #
def load_prefix():
    if os.path.exists("bot_prefix.json"):
        with open("bot_prefix.json", 'r') as f:
            return json.load(f).get("prefix", "!")
    return "!"

def load_server_prefixes():
    if os.path.exists("server_prefixes.json"):
        with open("server_prefixes.json", 'r') as f:
            return json.load(f)
    return {}

def save_server_prefixes(prefixes):
    with open("server_prefixes.json", 'w') as f:
        json.dump(prefixes, f, indent=4)

def get_server_prefix(guild_id):
    prefixes = load_server_prefixes()
    return prefixes.get(str(guild_id), load_prefix())

# ================== NO PREFIX USERS ================== #
def load_no_prefix_users():
    if os.path.exists("no_prefix_users.json"):
        with open("no_prefix_users.json", 'r') as f:
            return json.load(f)
    return {}

no_prefix_users = load_no_prefix_users()
bot_owner_id = 1049708274032853003

async def get_prefix(bot, message):
    guild_id = message.guild.id if message.guild else None
    current_prefix = get_server_prefix(guild_id) if guild_id else load_prefix()

    if str(message.author.id) in no_prefix_users or message.author.id == bot_owner_id:
        return commands.when_mentioned_or(current_prefix, "")(bot, message)
    return commands.when_mentioned_or(current_prefix)(bot, message)

# ================== BOT SETUP ================== #
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=get_prefix, intents=intents, help_command=None)

# ================== ON READY ================== #
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    print(f"🛡️ Connected to {len(bot.guilds)} servers")
    print(f"🧠 Commands: {len(bot.commands)} | Cogs: {len(bot.cogs)}")

    await bot.change_presence(
        activity=discord.Streaming(
            name=f"{len(bot.guilds)} servers | {load_prefix()}help",
            url="https://www.twitch.tv/discord"
        ),
        status=discord.Status.online
    )

# ================== ERROR HANDLER ================== #
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send(f"❌ Missing Permissions: {', '.join(error.missing_permissions)}")
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send("❌ I don't have permission to do that.")
    else:
        print(f"⚠️ Error: {error}")

# ================== STATUS COMMAND ================== #
@bot.command(name="status")
async def bot_status(ctx):
    embed = discord.Embed(title="📊 Bot Status", color=0x00ff00)
    embed.add_field(name="Latency", value=f"{round(bot.latency * 1000)}ms")
    embed.add_field(name="Servers", value=len(bot.guilds))
    embed.add_field(name="Users", value=len(bot.users))
    embed.add_field(name="Prefix", value=await get_prefix(bot, ctx.message))
    embed.add_field(name="Commands", value=len(bot.commands))
    embed.add_field(name="Cogs", value=len(bot.cogs))
    await ctx.send(embed=embed)

# ================== LOAD COGS ================== #
async def load_cogs():
    extensions = [
        "moderation",
        "utility",
        "welcome",
        "giveaway",
        "help",
        "Owners_only"
    ]
    for ext in extensions:
        try:
            await bot.load_extension(ext)
            print(f"✅ Loaded cog: {ext}")
        except Exception as e:
            print(f"❌ Failed to load cog {ext}: {e}")
            import traceback
            traceback.print_exc()

# ================== FLASK KEEP ALIVE ================== #
app = Flask("")

@app.route("/")
def home():
    return "✅ Bot is running"

def run():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    Thread(target=run).start()

# ================== START BOT ================== #
async def main():
    await load_cogs()
    token = os.getenv("BOT_TOKEN")
    if not token:
        print("❌ BOT_TOKEN not found")
        sys.exit(1)
    await bot.start(token)

if __name__ == "__main__":
    keep_alive()
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"❌ Error while running bot: {e}")
        import traceback
        traceback.print_exc()
        
