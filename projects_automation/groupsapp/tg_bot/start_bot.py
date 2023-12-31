from telegram.ext import Updater
from telegram.ext import (CommandHandler,
                          CallbackQueryHandler,
                          ConversationHandler)

from groupsapp.tg_bot import handlers


def start_bot(tg_key):
    updater = Updater(token=tg_key, use_context=True)
    dispatcher = updater.dispatcher

    student_conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', handlers.student_start)
        ],
        states={
            handlers.HELLO: [
                CallbackQueryHandler(
                    callback=handlers.hello_keyboard_handler,
                    pass_chat_data=True)
            ],
            handlers.SCHEDULE: [
                CallbackQueryHandler(
                    callback=handlers.schedule_keyboard_handler,
                    pass_chat_data=True)
            ],
            handlers.SLOTS: [
                CallbackQueryHandler(
                    callback=handlers.slots_keyboard_handler,
                    pass_chat_data=True)
            ],
            handlers.FINAL: [
                CallbackQueryHandler(
                    callback=handlers.final_keyboard_handler,
                    pass_chat_data=True)
            ]
        },
        fallbacks=[
            CommandHandler('cancel', handlers.cancel_handler)
        ]
    )

    dispatcher.add_handler(student_conv_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    start_bot()
