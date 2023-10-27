from re import match
from datetime import datetime

from telegram import Update
from telegram.ext import CallbackContext
from telegram.ext import ConversationHandler

from projects_automation.groupsapp.tg_bot import keyboards


HELLO = 1  # projects is coming
SCHEDULE = 2  # add slots or choose any time
SLOTS = 3  # choose starting time for the slot
FINAL = 4  # choose ending time for the slot
SLOT_CHOSEN = 5  # another slot or ready?
READY = 6


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
                             text='Привет!\n '
                                  'Наступает пора командных проектов. Будет вместо учебного плана.\n'
                                  'Будет что-то вроде урока на девмане, только без шагов, '
                                  'зато втроём (очень редко вдвоем) + с ПМом.\n'
                                  'Созвоны будут по 20 минут каждый день в течение недели. '
                                  'Быть у компьютера не обязательно.\n'
                                  ''
                                  'Слоты для созвонов:'
                                  '09.00 - 13.00, 19.00 - 23.00 мск.'
                                  ''
                                  'Выбери удобное время для созвонов.',
                             reply_markup=keyboards.get_hello_keyboard())

    return SCHEDULE


def schedule_keyboard_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data
    chat_id = update.effective_message.chat_id
    current_text = update.effective_message.text

    query.edit_message_text(text=current_text)
    context.bot.send_message(chat_id=chat_id,
                             text='Время для созвонов:\n\n '
                                  '- 07.00 - 12.00 мск.\n'
                                  '- 14.00 - 24.00 мск.\n\n'
                                  'Выбери подходящее время',
                             reply_markup=keyboards.get_schedule_keyboard())

    return SLOTS


def slots_keyboard_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data
    chat_id = update.effective_message.chat_id
    current_text = update.effective_message.text

    query.edit_message_text(text=current_text)
    if data == 'any_time':
        context.bot.send_message(chat_id=chat_id,
                                 text='Составы команд, бриф и все остальное пришлю в следующий понедельни.\n\n'
                                      'Пока почитай статью по командным проектам:\n'
                                      'https://dvmn.org/encyclopedia/team-projects/i-need-team-lead/.',
                                 reply_markup=keyboards.get_final_keyboard())
        return FINAL
    elif data == 'add_slot' or data == 'back':
        context.bot.send_message(chat_id=chat_id,
                                 text='Выбери время начала слота\n\n'
                                      'Готов созваниваться в промежутке с...',
                                 reply_markup=keyboards.get_slots_keyboard())
    else:  # выбрано время
        pass


def slots_final_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data
    chat_id = update.effective_message.chat_id
    current_text = update.effective_message.text

    query.edit_message_text(text=current_text)
    context.bot.send_message(chat_id=chat_id,
                             text='Ваше участие в проекте отменено')