import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from utils.db import init_db, add_user_if_not_exists, add_coins, get_balance

load_dotenv()
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in successfully as {bot.user}")
    init_db()

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    add_user_if_not_exists(message.author.id)
    add_coins(message.author.id, 10)
    await bot.process_commands(message)

@bot.command()
async def balance(ctx):
    coins = get_balance(ctx.author.id)
    await ctx.send(f"{ctx.author.mention}, you have {coins} coins 💰")

bot.run(os.getenv("DISCORD_TOKEN"))
 
    