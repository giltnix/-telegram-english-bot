import os

# Берём токен из переменных окружения
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Если переменная окружения не задана, используем локальный токен (для разработки)
if not BOT_TOKEN:
    BOT_TOKEN = "8281276886:AAFH0HizBFyieJyoP0crR9r1nVrKyAtyX3g"

# Если хотите строго через env и аварийно падать при отсутствии:
# if not BOT_TOKEN:
#     raise RuntimeError("BOT_TOKEN not found in environment variables")
