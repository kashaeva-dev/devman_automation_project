import datetime
import logging
import random

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

from groupsapp.models import Project_manager, Week, Timeslot, Group, Student, StudentProjectWeek, StudentProjectSlot

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
            logger.info(f'{query}')
            project_manager_ids = Project_manager.objects.values_list('telegram_id', flat=True)
            logger.info(f'{project_manager_ids}')

            if update.effective_chat.id in project_manager_ids:
                text = 'ГЛАВНОЕ МЕНЮ:'
                main_menu_keyboard = [
                    [
                        InlineKeyboardButton("Создать группы", callback_data='make_groups'),
                        InlineKeyboardButton("Посмотреть группы", callback_data='look_groups'),

                    ],
                    [
                        InlineKeyboardButton("Создать тестовые слоты для студентов",
                                             callback_data='make_student_slots'),
                    ]
                ]
                if query:
                    query.edit_message_text(
                        text=text,
                        reply_markup=InlineKeyboardMarkup(main_menu_keyboard),
                )
                else:
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
            logger.info("Start make groups")
            query = update.callback_query
            week = Week.objects.get(pk=4)
            project_manager = Project_manager.objects.prefetch_related('schedule').get(telegram_id=update.effective_chat.id)
            timeslots = Timeslot.objects.all()
            created_groups_count = 0
            for schedule in project_manager.schedule.all():
                for timeslot in timeslots:
                    if timeslot.start_time >= schedule.start_time and timeslot.end_time <= schedule.end_time:
                        group, created = Group.objects.get_or_create(
                            week=week,
                            timeslot=timeslot,
                            project_manager=project_manager,
                        )
                        if created:
                            created_groups_count += 1
            keyboard = [
                [InlineKeyboardButton("На главный", callback_data="to_start")]
                ]
            query.edit_message_text(
                text=f'Было создано {created_groups_count} групп',
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            query.answer()

            return 'MAKE_GROUPS'


        def make_student_slots(update, _):
            logger.info('Start making student slots')
            morning_intervals = {
                '1': '07:00 - 09:00',
                '2': '09:00 - 12:00',
            }

            evening_intervals = {
                '1': '14:00 - 17:00',
                '2': '17:00 - 20:00',
                '3': '20:00 - 23:00',
            }
            text = '14:00 - 17:00'.split(' - ')
            students = StudentProjectWeek.objects.select_related('student').all()
            timeslots = Timeslot.objects.all()
            student_slots_created = 0
            for student in students:
                if student.student.location_FE:
                    choosen_interval = morning_intervals[random.choice(list(morning_intervals))].split(' - ')
                    interval_start_time = datetime.datetime.strptime(choosen_interval[0], '%H:%M').time()
                    interval_end_time = datetime.datetime.strptime(choosen_interval[1], '%H:%M').time()
                    for timeslot in timeslots:
                        if timeslot.start_time >= interval_start_time and timeslot.end_time <= interval_end_time:
                            slot, created = StudentProjectSlot.objects.get_or_create(
                                student=student,
                                slot=timeslot,
                            )
                            if created:
                                student_slots_created += 1
                else:
                    choosen_interval = evening_intervals[random.choice(list(evening_intervals))].split(' - ')
                    interval_start_time = datetime.datetime.strptime(choosen_interval[0], '%H:%M').time()
                    interval_end_time = datetime.datetime.strptime(choosen_interval[1], '%H:%M').time()
                    for timeslot in timeslots:
                        if timeslot.start_time >= interval_start_time and timeslot.end_time <= interval_end_time:
                            slot, created = StudentProjectSlot.objects.get_or_create(
                                student=student,
                                slot=timeslot,
                            )
                            if created:
                                student_slots_created += 1

            return 'MAKE_STUDENT_SLOTS'


        def cancel(update, _):
            update.message.reply_text(
                'До новых встреч',
                reply_markup=ReplyKeyboardRemove(),
            )
            return ConversationHandler.END

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', start_conversation),
                          CallbackQueryHandler(start_conversation, pattern='to_start'),
                          ],
            states={
                'MAIN_MENU': [
                    CallbackQueryHandler(make_groups, pattern='make_groups'),
                    CallbackQueryHandler(make_student_slots, pattern='make_student_slots'),
                    CommandHandler('start', start_conversation),
                ],
                'MAKE_GROUPS': [
                    CallbackQueryHandler(start_conversation, pattern='to_start'),
                    CommandHandler('start', start_conversation),
                ],
                'MAKE_STUDENT_SLOTS': [
                    CallbackQueryHandler(start_conversation, pattern='to_start'),
                    CommandHandler('start', start_conversation),
                ],
            },
            fallbacks=[CommandHandler('cancel', cancel)],
        )
        dispatcher.add_handler(conv_handler)
        start_handler = CommandHandler('start', start_conversation)
        dispatcher.add_handler(start_handler)
        updater.start_polling()
        updater.idle()
