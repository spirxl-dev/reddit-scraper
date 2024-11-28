import sqlite3

# Config
DEFAULT_PATH = "/new"  # Default subreddit path
ENABLE_HOT = False     # Include /hot
ENABLE_TOP = False     # Include /top with variations

db_path = "database/data.db"

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

base_subreddit_urls = [
    "https://www.reddit.com/r/Bitcoin",
    "https://www.reddit.com/r/BitcoinBeginners",
    "https://www.reddit.com/r/BitcoinMarkets",
    "https://www.reddit.com/r/btc",
    "https://www.reddit.com/r/BitcoinTrading",
    "https://www.reddit.com/r/BitcoinUK",
    "https://www.reddit.com/r/BitcoinMining",
    "https://www.reddit.com/r/BitcoinCA",
    "https://www.reddit.com/r/BitcoinAUS",
    "https://www.reddit.com/r/BitcoinCash",
    "https://www.reddit.com/r/CryptoCurrency",
    "https://www.reddit.com/r/Crypto_General",
]

subreddit_urls = []
for base_url in base_subreddit_urls:
    subreddit_urls.append(f"{base_url}{DEFAULT_PATH}")
    if ENABLE_HOT:
        subreddit_urls.append(f"{base_url}/hot")
    if ENABLE_TOP:
        subreddit_urls.append(f"{base_url}/top")
        subreddit_urls.append(f"{base_url}/top/?t=all")
        subreddit_urls.append(f"{base_url}/top/?t=year")
        subreddit_urls.append(f"{base_url}/top/?t=month")
        subreddit_urls.append(f"{base_url}/top/?t=day")

for url in subreddit_urls:
    try:
        cursor.execute("INSERT OR IGNORE INTO subreddits (url) VALUES (?)", (url,))
    except sqlite3.Error as e:
        print(f"Error inserting {url}: {e}")

conn.commit()
conn.close()

print("Subreddit URLs have been successfully inserted into the database.")