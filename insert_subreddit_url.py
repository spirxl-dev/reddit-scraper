"""Helper script to manual insert urls into subreddit table"""

import sqlite3

db_path = "database/data.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS subreddits (
    id INTEGER PRIMARY KEY,
    url TEXT NOT NULL UNIQUE
)
""")

subreddit_urls = [
    "https://www.reddit.com/r/CryptoCurrency",
    "https://www.reddit.com/r/Bitcoin",
    "https://www.reddit.com/r/ethereum",
    "https://www.reddit.com/r/ethtrader",
    "https://www.reddit.com/r/StockMarket",
    "https://www.reddit.com/r/stocks",
    "https://www.reddit.com/r/WallStreetBets",
    "https://www.reddit.com/r/investing",
    "https://www.reddit.com/r/pennystocks",
    "https://www.reddit.com/r/cryptomarkets",
    "https://www.reddit.com/r/cryptotechnology",
    "https://www.reddit.com/r/BitcoinBeginners",
    "https://www.reddit.com/r/DeFi",
    "https://www.reddit.com/r/cryptocurrencies",
    "https://www.reddit.com/r/altcoin",
    "https://www.reddit.com/r/dogecoin",
    "https://www.reddit.com/r/SHIBArmy",
    "https://www.reddit.com/r/Monero",
    "https://www.reddit.com/r/Ripple",
    "https://www.reddit.com/r/litecoin",
    "https://www.reddit.com/r/cardano",
    "https://www.reddit.com/r/solana",
    "https://www.reddit.com/r/AlgorandOfficial",
    "https://www.reddit.com/r/Polkadot",
    "https://www.reddit.com/r/Chainlink",
    "https://www.reddit.com/r/VeChain",
    "https://www.reddit.com/r/Stellar",
    "https://www.reddit.com/r/Tezos",
    "https://www.reddit.com/r/Tronix",
    "https://www.reddit.com/r/IOTA",
    "https://www.reddit.com/r/NEO",
    "https://www.reddit.com/r/Zilliqa",
    "https://www.reddit.com/r/ElrondNetwork",
    "https://www.reddit.com/r/Hedera",
    "https://www.reddit.com/r/Theta_Network",
    "https://www.reddit.com/r/ICONproject",
    "https://www.reddit.com/r/Qtum",
    "https://www.reddit.com/r/NanoCurrency",
    "https://www.reddit.com/r/DashPay",
    "https://www.reddit.com/r/Zcash",
    "https://www.reddit.com/r/EOS",
    "https://www.reddit.com/r/BitcoinCash",
    "https://www.reddit.com/r/Decred",
    "https://www.reddit.com/r/BasicAttentionToken",
    "https://www.reddit.com/r/0xProject",
    "https://www.reddit.com/r/OMGnetwork",
    "https://www.reddit.com/r/EnjinCoin",
    "https://www.reddit.com/r/Siacoin",
    "https://www.reddit.com/r/ArkEcosystem",
    "https://www.reddit.com/r/KomodoPlatform",
    "https://www.reddit.com/r/Wavesplatform",
    "https://www.reddit.com/r/Stratisplatform",
    "https://www.reddit.com/r/Lisk",
    "https://www.reddit.com/r/NEM",
    "https://www.reddit.com/r/Steemit",
    "https://www.reddit.com/r/BitShares",
    "https://www.reddit.com/r/FactomProtocol",
    "https://www.reddit.com/r/MaidSafe"
]

for url in subreddit_urls:
    try:
        cursor.execute("INSERT OR IGNORE INTO subreddits (url) VALUES (?)", (url,))
    except sqlite3.Error as e:
        print(f"Error inserting {url}: {e}")

conn.commit()
conn.close()

print("Subreddits have been successfully inserted into the database.")