import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from utils import db

load_dotenv()
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in successfully as {bot.user}")
    db.init_db()

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    db.add_user_if_not_exists(message.author.id)
    db.add_coins(message.author.id, 10)
    await bot.process_commands(message)

@bot.command()
async def balance(ctx):
    coins = db.get_balance(ctx.author.id)
    await ctx.send(f"{ctx.author.mention}, you have {coins} coins 💰")

@bot.command()
async def place_bet(ctx, condition: str, amount: int, target: discord.Member):
    if (ctx.author == target):
        await ctx.send("You can't place a bet on yourself!")
        return None
    else:
        if (db.insert_bet(amount, condition, ctx.author.id, target.id)):
            await ctx.send(f"{ctx.author.mention()}, you successfully placed your bet on {condition} from {target}")
        else: await ctx.send(f"{ctx.author.mention()}, you have insufficient balance to place this bet")


bot.run(os.getenv("DISCORD_TOKEN"))
 
    