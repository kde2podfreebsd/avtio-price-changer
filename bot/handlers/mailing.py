from bot.config import bot
from avito.chats import AvitoChats
from telebot.asyncio_handler_backends import State, StatesGroup
from bot.context import message_context_manager
from telebot import types

message_to_send = None

class MailingSteps(StatesGroup):
    step2 = State()
    confirm = State()

@bot.callback_query_handler(func=lambda call: call.data == 'mailing')
async def mailing_menu(call) -> None:
    await message_context_manager.delete_msgId_from_help_menu_dict(call.message.chat.id)
    chats_controller = AvitoChats()
    await chats_controller.get_chats()
    msg = await bot.send_message(
        chat_id=call.message.chat.id,
        text=f'📤Новая спам рассылка\nВсего чатов для рассылки: {len(chats_controller.chat_ids)}\n\nНапиши текстовое сообщение'
    )
    await bot.set_state(call.message.chat.id, MailingSteps.step2)
    message_context_manager.add_msgId_to_help_menu_dict(call.message.chat.id, msg.message_id)

@bot.message_handler(state=MailingSteps.step2)
async def receive_message_for_mailing(message) -> None:
    await message_context_manager.delete_msgId_from_help_menu_dict(message.chat.id)
    msg = await bot.send_message(
        chat_id=message.chat.id,
        text=f'Ты отправил сообщение:\n"{message.text}"\n\nВыбери действие:',
        reply_markup=confirm_markup()
    )
    global message_to_send
    message_to_send = message.text
    await bot.set_state(message.chat.id, MailingSteps.confirm)
    message_context_manager.add_msgId_to_help_menu_dict(message.chat.id, msg.message_id)

def confirm_markup():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text="Отправить", callback_data="send_message"))
    markup.add(types.InlineKeyboardButton(text="Отменить", callback_data="cancel_message"))
    return markup

@bot.callback_query_handler(state=MailingSteps.confirm)
async def process_confirm_action(call) -> None:
    if call.data == "send_message":
        await send_mailing(call)
    elif call.data == "cancel_message":
        await cancel_mailing(call)

async def send_mailing(call):
    await message_context_manager.delete_msgId_from_help_menu_dict(call.message.chat.id)
    await bot.send_message(chat_id=call.message.chat.id, text="Сообщение отправлено!")
    chats_controller = AvitoChats()
    await chats_controller.get_chats()
    for chat in chats_controller.chat_ids:
        avitochatid = list(chat.keys())[0]
        await chats_controller.send_message(chat_id=avitochatid, text=message_to_send)

async def cancel_mailing(call):
    await message_context_manager.delete_msgId_from_help_menu_dict(call.message.chat.id)
    await bot.send_message(chat_id=call.message.chat.id, text="Рассылка отменена.")
