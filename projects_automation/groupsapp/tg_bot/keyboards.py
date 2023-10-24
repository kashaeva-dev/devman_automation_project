from datetime import datetime

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


START_BUTTON = {'callback': 'begin',
                'text': 'Начать'}


def get_start_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(START_BUTTON.get('text'), callback_data=START_BUTTON.get('callback')),
        ],
    ]

    return InlineKeyboardMarkup(keyboard)
