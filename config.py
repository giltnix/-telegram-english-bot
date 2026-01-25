import os

BOT_TOKEN = os.environ.get("BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN not found in environment variables")BOT_TOKEN = "8281276886:AAFH0HizBFyieJyoP0crR9r1nVrKyAtyX3g"
