import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from utils import db, utility

load_dotenv()
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="b!", intents=intents, help_command=None)
allowed_roles = ["Authority", "Moderator", "VIP"]

@bot.event
async def on_ready():
    print(f"Logged in successfully as {bot.user}.")
    db.init_db()

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if not message.content.startswith("b!"):
        db.add_user_if_not_exists(message.author.id)
        db.add_coins(message.author.id, 10)
    await bot.process_commands(message)

@bot.command()
async def bal(ctx):
    coins = db.get_balance(ctx.author.id)
    await ctx.send(f"{ctx.author.mention}, you have {coins} coins 💰.")

@bot.command()
async def pb(ctx, condition: str, amount: int, target: discord.Member):
        if(ctx.author.id == target.id):
            await ctx.send(f"{ctx.author.mention}, you can not place a bet targeting yourself.")
        else: 
            betid = db.insert_bet(amount, condition, ctx.author.id, target.id)
            if (betid):
                await ctx.send(f"{ctx.author.mention}, you successfully placed your bet on {condition} from {target}. Bet ID: {betid[0]}")
            else: await ctx.send(f"{ctx.author.mention}, you have insufficient balance to place this bet.")



@bot.command()
async def mybets(ctx):
    bets = db.get_my_bets(ctx.author.id, None)
    table_content = utility.displayBets(bets, ctx)
    if not table_content:
        await ctx.send(f"{ctx.author.mention}, you have no currently active bets.")
        return
    await ctx.send(f"{ctx.author.mention}, here are your active bets:\n\n```{table_content}```")

@bot.command()
async def allbets(ctx):
    if not any(role.name in allowed_roles for role in ctx.author.roles):
        await ctx.send(f"{ctx.author.mention}, you are not allowed to see all currently active bets. Ask admins for help.")
        return
    bets = db.get_all_bets()
    table_content = utility.displayBets(bets, ctx)
    if not table_content:
        await ctx.send("Wow, there are no currently active bets. Let's do some gambling!")
        return
    await ctx.send(f"All currently active bets:\n\n```{table_content}```")

@bot.command()
async def res(ctx, bet_id, outcome):
    if not any(role.name in allowed_roles for role in ctx.author.roles):
        await ctx.send(f"{ctx.author.mention}, you are not allowed to resolve bets. Ask admins to resolve.")
        return
    else:
        success = db.bet_resolve(bet_id, outcome)
        if success:
            await ctx.send(f"{ctx.author.mention}, you have successfully resolved the bet {bet_id}!")
        else:
            await ctx.send(f"{ctx.author.mention}, there was an error while resolving the bet {bet_id}.")

@bot.command()
async def restarget(ctx, target: discord.Member, outcome):
    target_id = str(target.id)
    if not any(role.name in allowed_roles for role in ctx.author.roles):
        await ctx.send("You are not allowed to resolve bets. Ask admins to resolve.")
        return
    else:
        success = db.resolve_target(target_id, outcome)
        if success:
            await ctx.send(f"{ctx.author.mention}, you have successfully resolved all bets targeting {target_id}!")
        else:
            await ctx.send(f"{ctx.author.mention}, there was an error while resolving all bets targeting {target_id}.")



@bot.command()
async def zero(ctx, target : discord.Member):
    if not any(role.name in allowed_roles for role in ctx.author.roles):
        await ctx.send("You are not allowed to resolve bets. Ask admins to resolve.")
        return
    else:
        target_balance = db.get_balance(target.id)
        success = db.update_balance(target.id, target_balance, False, None)

    if success:
        await ctx.send(f'{ctx.author.mention}, you successfully zeroed balance of {target.name}')
    else:
        await ctx.send(f"{ctx.author.mention}, there was an error updating user's balance")


        


@bot.command()
async def help(ctx):
    
    await ctx.send(
    "**📜 Available Commands:**\n\n"
    "• `b!bal`\n"
    "  Check your current coin balance.\n\n"
    "• `b!pb 'Condition' <Amount> @User`\n"
    "  Place a new bet. Set a condition, the amount of coins, and the user you're betting on.\n\n"
    "• `b!mybets`\n"
    "  View your active (unresolved) bets.\n\n"
    "• `b!allbets` – *(Admin only)*\n"
    "  View all currently unresolved bets across all users.\n\n"
    "• `b!res <Bet ID> <0/1>` – *(Admin only)*\n"
    "  Resolve a specific bet by its ID. Use `1` for win, `0` for loss.\n\n"
    "• `b!restarget @User <0/1>` – *(Admin only)*\n"
    "  Resolve all bets targeting the specified user. Use `1` for win, `0` for loss.")

            
        
    
         
bot.run(os.getenv("DISCORD_TOKEN"))
 
    