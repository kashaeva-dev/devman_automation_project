import datetime
import logging
from environs import Env

from django.core.management.base import BaseCommand
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardRemove,
    ParseMode,
)
from telegram.ext import (
    Updater,
    Filters,
    MessageHandler,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
)

from groupsapp.models import Project_manager, Week, Timeslot

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO,
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):


    def handle(self, *args, **options):
        env = Env()
        env.read_env()
        tg_bot_token=env('TG_BOT_TOKEN')
        updater = Updater(token=tg_bot_token, use_context=True)
        dispatcher = updater.dispatcher


        def start_conversation(update, _):
            query = update.callback_query
            project_manager_ids = Project_manager.objects.values_list('telegram_id', flat=True)
            logger.info(f'{project_manager_ids}')
            if update.effective_chat.id in project_manager_ids:
                text = 'ГЛАВНОЕ МЕНЮ:'
                main_menu_keyboard = [
                    [
                        InlineKeyboardButton("Создать группы", callback_data='make_groups'),
                        InlineKeyboardButton("Посмотреть группы", callback_data='look_groups'),
                    ],
                ]
                update.message.reply_text(
                    text=text,
                    reply_markup=InlineKeyboardMarkup(main_menu_keyboard),
                    )
            else:
                update.message.reply_text(
                    text='Вы не являетесь менеджером проекта. Пожалуйста, перейдите к функционалу для студентов!',
                    )

            return 'MAIN_MENU'


        # def choose_week(update, _):
        #     query = update.callback_query
        #     today = datetime.date.today()
        #     weeks = Week.objects.filter(start_date__gt=today)


        def make_groups(update, _):
            week = Week.objects.get(pk=3)
            project_manager = Project_manager.objects.select_related('schedule').get(telegram_id=update.effective_chat.id)
            timeslots = Timeslot.objects.all()
            for schedule in project_manager.schedule:
                for timeslot in timeslots:
                    if timeslot.start_time >= schedule.start_time and timeslot.end_time <= schedule.end_time:
                        pass


        start_handler = CommandHandler('start', start_conversation)
        dispatcher.add_handler(start_handler)
        updater.start_polling()
        updater.idle()
