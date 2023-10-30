from datetime import datetime

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from groupsapp.tg_bot import bot_methods


START_BUTTON = InlineKeyboardButton('Начать', callback_data='begin')
CHOOSE_TIME_BUTTON = InlineKeyboardButton('Выбрать время', callback_data='choose_time')
ANY_TIME_BUTTON = InlineKeyboardButton('В любое время', callback_data='any_time')
ADD_SLOT_BUTTON = InlineKeyboardButton('Добавить слот', callback_data='add_slot')

BACK_BUTTON = InlineKeyboardButton('Отмена', callback_data='back')
CANCELL_BUTTON = InlineKeyboardButton('Отменить участие в проекте', callback_data='quit')
DONE_BUTTON = InlineKeyboardButton('Готово', callback_data='done')


def get_start_keyboard():
    keyboard = [
        [
            START_BUTTON,
        ],
    ]

    return InlineKeyboardMarkup(keyboard)


def get_hello_keyboard():
    keyboard = [
        [
            CHOOSE_TIME_BUTTON,
        ],
    ]

    return InlineKeyboardMarkup(keyboard)


def get_schedule_keyboard():
    keyboard = [
        [
            ANY_TIME_BUTTON,
        ],
        [
            ADD_SLOT_BUTTON,
        ],
    ]

    return InlineKeyboardMarkup(keyboard)


def get_slots_keyboard(chosen_slots):
    intervals = bot_methods.get_available_intervals()
    interval_buttons = []
    for interval in intervals:
        interval_name = bot_methods.interval_to_text(interval)
        if interval_name in chosen_slots:
            continue
        interval_button = InlineKeyboardButton(interval_name, callback_data=interval_name)
        interval_buttons.append([interval_button])

    if not interval_buttons:
        interval_buttons.append([InlineKeyboardButton('Интервалы закончились. Продолжить', callback_data='any_time')])

    keyboard = interval_buttons

    return InlineKeyboardMarkup(keyboard)


def get_slot_chosen_keyboard():
    keyboard = [
        [
            ADD_SLOT_BUTTON,
        ],
        [
            DONE_BUTTON,
        ],
    ]

    return InlineKeyboardMarkup(keyboard)


def get_final_keyboard():
    keyboard = [
        [
            CANCELL_BUTTON
        ],
    ]

    return InlineKeyboardMarkup(keyboard)
