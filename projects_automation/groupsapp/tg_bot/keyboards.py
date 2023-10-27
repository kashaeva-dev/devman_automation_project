from datetime import datetime

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


START_BUTTON = InlineKeyboardButton('Начать', callback_data='begin')
CHOOSE_TIME_BUTTON = InlineKeyboardButton('Выбрать время', callback_data='choose_time')
ANY_TIME_BUTTON = InlineKeyboardButton('В любое время', callback_data='any_time')
ADD_SLOT_BUTTON = InlineKeyboardButton('Добавить слот', callback_data='add_slot')

TIMESLOT_BUTTONS = [
    [
        InlineKeyboardButton('7:00', callback_data='7:00'),
        InlineKeyboardButton('7:20', callback_data='7:20'),
        InlineKeyboardButton('7:40', callback_data='7:40')
    ],
    [
        InlineKeyboardButton('8:00', callback_data='8:00'),
        InlineKeyboardButton('8:20', callback_data='8:20'),
        InlineKeyboardButton('8:40', callback_data='8:40')
     ],
]
MANUAL_BUTTON = InlineKeyboardButton('Указать вручную', callback_data='manual')
BACK_BUTTON = InlineKeyboardButton('Отмена', callback_data='back')
CANCELL_BUTTON =  InlineKeyboardButton('Отменить участие в проекте', callback_data='back')


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


def get_slots_keyboard(start=''):
    slot_buttons = TIMESLOT_BUTTONS
    slot_buttons.append([MANUAL_BUTTON])
    slot_buttons.append([BACK_BUTTON])
    keyboard = slot_buttons

    return InlineKeyboardMarkup(keyboard)


def get_final_keyboard():
    keyboard = [
        [
            CANCELL_BUTTON
        ],
    ]

    return InlineKeyboardMarkup(keyboard)