import os
from math import ceil
from dotenv import load_dotenv
from telebot import telebot
from telebot import types
from db import QuoteController
from typing import Dict, List, Optional
import datetime
from utils import ItemStatus

load_dotenv()

bot = telebot.TeleBot(os.getenv('TELEGRAM_BOT_TOKEN'))
qc = QuoteController(os.getenv('DB_PATH'))
QUOTES_PER_PAGE = int(os.getenv("QUOTES_PER_PAGE"))

class MessageContextManager:
    _instance: Optional['MessageContextManager'] = None

    def __new__(cls, *args, **kwargs) -> 'MessageContextManager':
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        self.help_menu_msgId_to_delete: Dict[int, List[int]] = {}

    def add_msgId_to_help_menu_dict(self, chat_id: int, msgId: int) -> None:
        self.help_menu_msgId_to_delete.setdefault(chat_id, []).append(msgId)

    def delete_msgId_from_help_menu_dict(self, chat_id: int) -> None:
        try:
            msg_ids = self.help_menu_msgId_to_delete.pop(chat_id, [])
            for msg_id in msg_ids:
                bot.delete_message(chat_id, msg_id)
        except Exception as e:
            raise Exception(f"Не удалось удалить сообщения: {chat_id}, {msg_ids} | Exception: {e}")

message_context_manager: MessageContextManager = MessageContextManager()

def main_menu(message, page=1) -> None:
    try:
        message_context_manager.delete_msgId_from_help_menu_dict(message.chat.id)
        if message.chat.id in [int(x) for x in os.getenv("ADMIN_CHATIDS").replace("[", "").replace("]", "").replace(" ", "").split(",")]:
            all_ads = qc.get_all_ads()
            amount_of_pages = ceil(len(all_ads) / QUOTES_PER_PAGE)

            chunks = []
            i = 0
            while i < len(all_ads):
                chunks.append(all_ads[i:i + QUOTES_PER_PAGE])
                i += QUOTES_PER_PAGE

            data_to_display = chunks[page - 1] if page <= len(chunks) else []

            keyboard = types.InlineKeyboardMarkup(row_width=3)
            for ad in data_to_display:
                keyboard.add(types.InlineKeyboardButton(text=ad[6], callback_data=f"quote_{ad[0]}"))

            if amount_of_pages != 1:
                back = types.InlineKeyboardButton(
                    text="<", callback_data=f"main_menu#{page - 1 if page - 1 >= 1 else page}"
                )
                page_cntr = types.InlineKeyboardButton(
                    text=f"{page}/{amount_of_pages}", callback_data="nullified_{}".format(page)
                )
                forward = types.InlineKeyboardButton(
                    text=">", callback_data=f"main_menu#{page + 1 if page + 1 <= amount_of_pages else page}"
                )
                keyboard.add(back, page_cntr, forward)

                garantex_url = types.InlineKeyboardButton(
                    text="Garantex", url="https://garantex.org/"
                )

                keyboard.add(garantex_url)

            msg = bot.send_message(
                message.chat.id,
                f'<i>Allowed for {message.chat.username if message.chat.username is not None else message.chat.id}!</i>\nBTC price on {datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")}: {qc.get_current_btc_price()}₽\n\n<b>Объявления:</b>',
                parse_mode="html",
                reply_markup=keyboard
                )
            message_context_manager.add_msgId_to_help_menu_dict(message.chat.id, msg.message_id)
        else:
            bot.send_message(message.chat.id, '<b>Access denied</b>', parse_mode="html")
    except Exception as e:
        pass

@bot.message_handler(commands=['start'])
def start(message) -> None:
    main_menu(message)

@bot.callback_query_handler(func=lambda call: call.data.startswith('main_menu'))
def main_menu_inline(call) -> None:
    try:
        page = int(call.data.split('#')[1])
    except IndexError:
        page = 1
    main_menu(call.message, page)

def prepare_quote_message(avito_id):
    quote = qc.get_ad_by_avito_id(avito_id=avito_id)
    message = f'''
Название объявления: {quote[6]}
Avito ID: {quote[0]}
Адрес: {quote[1]}
Категория: {quote[2]}
Цена RUB: {quote[3]} ₽
Цена BTC: {qc.get_current_btc_price()} ₿
Соотношение цен rub/btc: {round(quote[4], 5)}
Status: {'✅ Active' if quote[5] == ItemStatus.ACTIVE.value else f'❌ {quote[5]}'}
Последнее время обновления: {quote[8]}
'''
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton(text="🔗 Item URL", url=quote[7]),
        types.InlineKeyboardButton(text="🔙 Back", callback_data="main_menu#1")
    )
    return message, keyboard

@bot.callback_query_handler(func=lambda call: call.data.startswith('quote_'))
def callback_quote_inline(call):
    message_context_manager.delete_msgId_from_help_menu_dict(call.message.chat.id)
    avito_id = qc.get_ad_by_avito_id(avito_id=call.data.split('_')[1])[0]
    message, keyboard = prepare_quote_message(avito_id)
    msg = bot.send_message(call.message.chat.id, message, reply_markup=keyboard)
    message_context_manager.add_msgId_to_help_menu_dict(call.message.chat.id, msg.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('nullified_'))
def nullified(call):
    bot.answer_callback_query(call.id, f"Current page: {call.data}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('change_status_'))
def change_status(call):
    message_context_manager.delete_msgId_from_help_menu_dict(call.message.chat.id)
    avito_id = call.data.split('_')[2]
    current_status = bool(qc.get_status(avito_id)[0])
    new_status = not current_status  
    if qc.update_status(avito_id, new_status):
        bot.answer_callback_query(call.id, "Status updated successfully!")
    else:
        bot.answer_callback_query(call.id, "Failed to update status.")

    message, keyboard = prepare_quote_message(avito_id)

    msg = bot.send_message(call.message.chat.id, message, reply_markup=keyboard)
    message_context_manager.add_msgId_to_help_menu_dict(call.message.chat.id, msg.message_id)
    

if __name__ == '__main__':
    qc.create_quote_table()
    bot.polling()
