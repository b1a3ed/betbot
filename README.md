# BetBot

Discord bot for accepting, placing, and resolving bets with virtual currency.


## Features

Virtual Currency System: Each user has a persistent coin balance stored in SQLite.

Bet Placement: Place bets on conditions with the b!pb command targeting other users.

Bet Management: View personal bets (b!mybets) or all active bets (b!allbets – admin only).

Bet Resolution: Resolve individual bets (b!res) or all bets for a specific user (b!restarget) – admin only.

Role-based Permissions: Only authorized roles can view and resolve bets.

## Tech Stack

Python (discord.py, sqlite3)

SQLite for persistent storage

Discord API for integration

## Setup

1. Clone the repository:
```
git clone https://github.com/b1a3ed/betbot.git
cd betbot
```


2. Install dependencies:
```
pip install -r requirements.txt
```


3. Add your Discord bot token to a .env file:
```
DISCORD_TOKEN=your_token_here
```


4. Run the bot:
```
python bot.py
```
