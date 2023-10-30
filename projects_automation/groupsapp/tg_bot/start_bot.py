import os
from dotenv import load_dotenv

from telegram.ext import Updater
from telegram.ext import CommandHandler, CallbackQueryHandler, ConversationHandler
from telegram.ext import MessageHandler, Filters

from groupsapp.tg_bot import handlers, pm_handlers


load_dotenv()

TG_API_KEY = os.getenv('TG_API_KEY')


def start_bot():
    updater = Updater(token=TG_API_KEY, use_context=True)
    dispatcher = updater.dispatcher

    student_conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('student', handlers.student_start)
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

    pm_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', pm_handlers.start_conversation),
                      CallbackQueryHandler(pm_handlers.start_conversation, pattern='to_start'),
                      ],
        states={
            'MAIN_MENU': [
                CallbackQueryHandler(pm_handlers.make_groups, pattern='make_groups'),
                CallbackQueryHandler(pm_handlers.make_student_slots, pattern='make_student_slots'),
                CallbackQueryHandler(pm_handlers.student_assignment, pattern='student_assignment'),
                CommandHandler('start', pm_handlers.start_conversation),
            ],
            'MAKE_GROUPS': [
                CallbackQueryHandler(pm_handlers.start_conversation, pattern='to_start'),
                CommandHandler('start', pm_handlers.start_conversation),
            ],
            'MAKE_STUDENT_SLOTS': [
                CallbackQueryHandler(pm_handlers.start_conversation, pattern='to_start'),
                CommandHandler('start', pm_handlers.start_conversation),
            ],
            'STUDENT_ASSIGNMENT': [
                CallbackQueryHandler(pm_handlers.start_conversation, pattern='to_start'),
                CommandHandler('start', pm_handlers.start_conversation),
            ],
        },
        fallbacks=[CommandHandler('cancel', pm_handlers.cancel)],
    )

    dispatcher.add_handler(student_conv_handler)
    dispatcher.add_handler(pm_conv_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    start_bot()
