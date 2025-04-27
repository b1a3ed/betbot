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
    if not message.content.startswith("!"):
        db.add_user_if_not_exists(message.author.id)
        db.add_coins(message.author.id, 10)
    await bot.process_commands(message)

@bot.command()
async def balance(ctx):
    coins = db.get_balance(ctx.author.id)
    await ctx.send(f"{ctx.author.mention}, you have {coins} coins 💰")

@bot.command()
async def place_bet(ctx, condition: str, amount: int, target: discord.Member):

        if (db.insert_bet(amount, condition, ctx.author.id, target.id)):
            await ctx.send(f"{ctx.author.mention}, you successfully placed your bet on {condition} from {target}")
        else: await ctx.send(f"{ctx.author.mention}, you have insufficient balance to place this bet")

@bot.command()
async def mybets(ctx):
    bets = db.get_my_bets(ctx.author.id, None)
    if not bets:
         await ctx.send(f"{ctx.author.mention}, you have no active bets.")
    else:
        table_content = "Bet ID     Coins     Condition       Target        Time\n"
        table_content +="-------------------------------------------------------\n"
        for bet in bets:
            id, coins, condition, target, time = bet
            member = ctx.guild.get_member(int(target))
            target_name = member.display_name if member else str(target)
            table_content += f"{str(id).ljust(10)} {str(coins).ljust(10)} {condition.ljust(12)} {target_name.ljust(18)} {time}\n"

        await ctx.send(f"{ctx.author.mention}, here are your active bets:\n\n```{table_content}```")


             
        
    
         

bot.run(os.getenv("DISCORD_TOKEN"))
 
    