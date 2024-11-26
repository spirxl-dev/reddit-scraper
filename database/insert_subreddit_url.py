"""Helper script to manual insert urls into subreddit table"""

import sqlite3

db_path = "data.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute(
    """
CREATE TABLE IF NOT EXISTS subreddits (
    id INTEGER PRIMARY KEY,
    url TEXT NOT NULL UNIQUE
)
"""
)

bitcoin_subreddit_urls = [
    "https://www.reddit.com/r/Bitcoin/new",
    "https://www.reddit.com/r/BitcoinBeginners/new",
    "https://www.reddit.com/r/BitcoinMarkets/new",
    "https://www.reddit.com/r/btc/new",
    "https://www.reddit.com/r/BitcoinTrading/new",
    "https://www.reddit.com/r/BitcoinUK/new",
    "https://www.reddit.com/r/BitcoinMining/new",
    "https://www.reddit.com/r/BitcoinCA/new",
    "https://www.reddit.com/r/BitcoinAUS/new",
    "https://www.reddit.com/r/BitcoinCash/new",
    "https://www.reddit.com/r/CryptoCurrency/new",
    "https://www.reddit.com/r/Crypto_General/new",
]

for url in bitcoin_subreddit_urls:
    try:
        cursor.execute("INSERT OR IGNORE INTO subreddits (url) VALUES (?)", (url,))
    except sqlite3.Error as e:
        print(f"Error inserting {url}: {e}")

conn.commit()
conn.close()

print("Subreddits have been successfully inserted into the database.")
