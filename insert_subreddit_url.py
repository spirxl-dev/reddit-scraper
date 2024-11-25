"""Helper script to manual insert urls into subreddit table"""

import sqlite3

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

bitcoin_subreddit_urls = [
    "https://www.reddit.com/r/Bitcoin/new",
    "https://www.reddit.com/r/BitcoinBeginners/new",
    "https://www.reddit.com/r/BitcoinMarkets/new",
    "https://www.reddit.com/r/btc/new",
    "https://www.reddit.com/r/BitcoinTrading/new",
    "https://www.reddit.com/r/BitcoinUK/new",
    "https://www.reddit.com/r/BitcoinMining/new",
    "https://www.reddit.com/r/BitcoinCA/new",
    "https://www.reddit.com/r/BitcoinDE/new",
    "https://www.reddit.com/r/BitcoinAUS/new",
]

subreddit_urls = [
    "https://www.reddit.com/r/CryptoCurrency/new",
    "https://www.reddit.com/r/Bitcoin/new",
    "https://www.reddit.com/r/ethereum/new",
    "https://www.reddit.com/r/ethtrader/new",
    "https://www.reddit.com/r/StockMarket/new",
    "https://www.reddit.com/r/stocks/new",
    "https://www.reddit.com/r/WallStreetBets/new",
    "https://www.reddit.com/r/investing/new",
    "https://www.reddit.com/r/pennystocks/new",
    "https://www.reddit.com/r/cryptomarkets/new",
    "https://www.reddit.com/r/cryptotechnology/new",
    "https://www.reddit.com/r/BitcoinBeginners/new",
    "https://www.reddit.com/r/DeFi/new",
    "https://www.reddit.com/r/cryptocurrencies/new",
    "https://www.reddit.com/r/altcoin/new",
    "https://www.reddit.com/r/dogecoin/new",
    "https://www.reddit.com/r/SHIBArmy/new",
    "https://www.reddit.com/r/Monero/new",
    "https://www.reddit.com/r/Ripple/new",
    "https://www.reddit.com/r/litecoin/new",
    "https://www.reddit.com/r/cardano/new",
    "https://www.reddit.com/r/solana/new",
    "https://www.reddit.com/r/AlgorandOfficial/new",
    "https://www.reddit.com/r/Polkadot/new",
    "https://www.reddit.com/r/Chainlink/new",
    "https://www.reddit.com/r/VeChain/new",
    "https://www.reddit.com/r/Stellar/new",
    "https://www.reddit.com/r/Tezos/new",
    "https://www.reddit.com/r/Tronix/new",
    "https://www.reddit.com/r/IOTA/new",
    "https://www.reddit.com/r/NEO/new",
    "https://www.reddit.com/r/Zilliqa/new",
    "https://www.reddit.com/r/ElrondNetwork/new",
    "https://www.reddit.com/r/Hedera/new",
    "https://www.reddit.com/r/Theta_Network/new",
    "https://www.reddit.com/r/ICONproject/new",
    "https://www.reddit.com/r/Qtum/new",
    "https://www.reddit.com/r/NanoCurrency/new",
    "https://www.reddit.com/r/DashPay/new",
    "https://www.reddit.com/r/Zcash/new",
    "https://www.reddit.com/r/EOS/new",
    "https://www.reddit.com/r/BitcoinCash/new",
    "https://www.reddit.com/r/Decred/new",
    "https://www.reddit.com/r/BasicAttentionToken/new",
    "https://www.reddit.com/r/0xProject/new",
    "https://www.reddit.com/r/OMGnetwork/new",
    "https://www.reddit.com/r/EnjinCoin/new",
    "https://www.reddit.com/r/Siacoin/new",
    "https://www.reddit.com/r/ArkEcosystem/new",
    "https://www.reddit.com/r/KomodoPlatform/new",
    "https://www.reddit.com/r/Wavesplatform/new",
    "https://www.reddit.com/r/Stratisplatform/new",
    "https://www.reddit.com/r/Lisk/new",
    "https://www.reddit.com/r/NEM/new",
    "https://www.reddit.com/r/Steemit/new",
    "https://www.reddit.com/r/BitShares/new",
    "https://www.reddit.com/r/FactomProtocol/new",
    "https://www.reddit.com/r/MaidSafe/new",
]

for url in bitcoin_subreddit_urls:
    try:
        cursor.execute("INSERT OR IGNORE INTO subreddits (url) VALUES (?)", (url,))
    except sqlite3.Error as e:
        print(f"Error inserting {url}: {e}")

conn.commit()
conn.close()

print("Subreddits have been successfully inserted into the database.")
