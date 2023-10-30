import os
from dotenv import load_dotenv

from telegram.ext import Updater
from telegram.ext import CommandHandler, CallbackQueryHandler, ConversationHandler
from telegram.ext import MessageHandler, Filters

from groupsapp.tg_bot import handlers


load_dotenv()

TG_API_KEY = os.getenv('TG_API_KEY')


def start_bot():
    updater = Updater(token=TG_API_KEY, use_context=True)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', handlers.start)
        ],
        states={
            handlers.HELLO: [
                CallbackQueryHandler(callback=handlers.hello_keyboard_handler, pass_chat_data=True)
            ],
            handlers.SCHEDULE: [
                CallbackQueryHandler(callback=handlers.schedule_keyboard_handler, pass_chat_data=True)
            ],
            handlers.SLOTS: [
                CallbackQueryHandler(callback=handlers.slots_keyboard_handler, pass_chat_data=True)
            ],
            handlers.FINAL: [
                CallbackQueryHandler(callback=handlers.final_keyboard_handler, pass_chat_data=True)
            ]
        },
        fallbacks=[
            CommandHandler('cancel', handlers.cancel_handler)
        ]
    )

    dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    start_bot()
