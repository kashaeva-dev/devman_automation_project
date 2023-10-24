from re import match
from datetime import datetime

from telegram import Update
from telegram.ext import CallbackContext
from telegram.ext import ConversationHandler

from projects_automation.groupsapp.tg_bot import keyboards


HELLO = 1


def start(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Привет! Проверим хендлер?",
                             reply_markup=keyboards.get_start_keyboard())
    return HELLO


def hello_keyboard_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data
    chat_id = update.effective_message.chat_id
    current_text = update.effective_message.text

    query.edit_message_text(text=current_text)
    context.bot.send_message(chat_id=chat_id,
                             text='Похоже, работает',)

    return ConversationHandler.END
