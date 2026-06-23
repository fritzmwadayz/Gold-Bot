import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
INTERVAL_MINUTES = int(os.getenv("INTERVAL_MINUTES", "5"))
SYMBOL = os.getenv("SYMBOL", "GC=F")  # Gold futures on yfinance