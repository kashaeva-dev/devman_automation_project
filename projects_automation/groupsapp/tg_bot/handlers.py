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

    context.user_data['slots'] = []

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
        # TODO: set all possible slots as chosen
        context.bot.send_message(chat_id=chat_id,
                                 text='Составы команд, бриф и все остальное пришлю в следующий понедельни.\n\n'
                                      'Пока почитай статью по командным проектам:\n'
                                      'https://dvmn.org/encyclopedia/team-projects/i-need-team-lead/.',
                                 reply_markup=keyboards.get_final_keyboard())
        return FINAL

    if data == 'done':
        # TODO: set slots from context.user_data['slots'] as chosen for the user
        context.bot.send_message(chat_id=chat_id,
                                 text='Составы команд, бриф и все остальное пришлю в следующий понедельни.\n\n'
                                      'Пока почитай статью по командным проектам:\n'
                                      'https://dvmn.org/encyclopedia/team-projects/i-need-team-lead/.',
                                 reply_markup=keyboards.get_final_keyboard())
        return FINAL

    if data == 'add_slot':
        if not context.user_data['slots']:
            context.bot.send_message(chat_id=chat_id,
                                     text='Выбери слот для созвона:',
                                     reply_markup=keyboards.get_slots_keyboard())
        else:
            query.edit_message_text(text=current_text,
                                    reply_markup=keyboards.get_slots_keyboard())

    else:  # выбрано время
        context.user_data['slots'].append(data)
        text = 'Выбранные слоты\n'
        for i, slot in enumerate(context.user_data['slots']):
            text = text + f'\nSlot {i+1}: {slot}'

        query.edit_message_text(text=text,
                                reply_markup=keyboards.get_slot_chosen_keyboard())


def final_keyboard_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data
    chat_id = update.effective_message.chat_id
    current_text = update.effective_message.text

    query.edit_message_text(text=current_text)

    if data == 'quit':
        # TODO: remove all chosen slots and remove user from project if exists
        context.bot.send_message(chat_id=chat_id,
                                 text='Ваше участие в проекте отменено')
        return ConversationHandler.END

    if data != 'no' and data != 'quit':
        context.user_data['new_slot'] = data

    context.bot.send_message(chat_id=chat_id,
                             text='Спасибо!\n\n'
                                  'Скоро пришлю расписание')


def cancel_handler(update: Update, context: CallbackContext):
    """ Отменить весь процесс диалога. Данные будут утеряны
    """
    update.message.reply_text('Отмена. Для начала с нуля введите /start')
    return ConversationHandler.END
