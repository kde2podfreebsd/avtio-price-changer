import os
import requests
import datetime
from db import QuoteController
from dotenv import load_dotenv
from bot import bot
from telebot import types

load_dotenv()

qc = QuoteController(os.getenv("DB_PATH"))

def update_quotes_price():
    preview_active_quotes = qc.get_ads_by_status(status=True)
    qc.update_btc_price()
    active_quotes = qc.get_ads_by_status(status=True)
    message = f'Report on {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n\n'
    for i, quote in enumerate(active_quotes):

        # !!!
        # TODO: AVITO PRICE CHANGE METHOD HERE

        message += f"Price changed for https://mock_url.com/avitoid:{quote[0]} avito quote:\n\nRUB price: {preview_active_quotes[i][1]}₽ -> {quote[1]}₽\n\nBTC price: {preview_active_quotes[i][2]}₿ -> {quote[2]}₿"
    for admin in [int(x) for x in os.getenv("ADMIN_CHATIDS").replace("[", "").replace("]", "").split(",")]:
        bot.send_message(
            admin,
            message,
            reply_markup=types.ReplyKeyboardRemove(),
            parse_mode="html"
        )

if __name__ == "__main__":
    update_quotes_price()