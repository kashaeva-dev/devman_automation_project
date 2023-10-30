import datetime
import logging
import random

from environs import Env

from django.core.management.base import BaseCommand
from django.db.models import Count, Subquery, OuterRef, F
from django.db.models.functions import Coalesce
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

from groupsapp.models import Project_manager, Week, Timeslot, Group, Student, StudentProjectWeek, StudentProjectSlot, \
    PMSchedule

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
                    ],
                    [
                        InlineKeyboardButton("Распределить студентов по группам",
                                             callback_data='student_assignment'),
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


        def student_assignment(update, _):

            def time_plus(time, timedelta):
                start = datetime.datetime(
                    2000, 1, 1,
                    hour=time.hour, minute=time.minute, second=time.second)
                end = start + timedelta
                return end.time()

            def time_minus(time, timedelta):
                start = datetime.datetime(
                    2000, 1, 1,
                    hour=time.hour, minute=time.minute, second=time.second)
                end = start - timedelta
                return end.time()

            week = Week.objects.get(pk=4)

            evening_intervals = {
                '1': '14:00 - 17:00',
                '2': '17:00 - 20:00',
                '3': '20:00 - 23:00',
            }
            for interval in ['1', '2', '3']:
                current_groups = Group.objects.filter(
                    week=week,
                    timeslot__start_time__gte=datetime.datetime.strptime(evening_intervals[interval].split(' - ')[0], '%H:%M').time(),
                    timeslot__end_time__lte=datetime.datetime.strptime(evening_intervals[interval].split(' - ')[1], '%H:%M').time()
                ).count()
                logger.info(f'{evening_intervals[interval]} доступно {current_groups} групп')

            managers = PMSchedule.objects.order_by('start_time').all()
            intersections = []
            last_key = list(evening_intervals)[-1]
            evening_intervals.pop(last_key)
            logger.info(evening_intervals)
            for interval in evening_intervals:
                intersections.append(datetime.datetime.strptime(evening_intervals[interval].split(' - ')[1], '%H:%M').time()),
            logger.info(intersections)

            manager_intersactions = dict()
            for intersection in intersections:
                manager_intersactions[intersection] = []
                for manager in managers:
                    if manager.start_time < intersection and manager.end_time > intersection:
                        manager_intersactions[intersection].append(manager)

            logger.info(manager_intersactions)
            levels = ['1_newborn', '2_newborn_plus']

            for intersection in intersections:
                logger.info(f'intersection: {intersection}')
                for manager in manager_intersactions[intersection]:
                    logger.info(f'manager: {manager.project_manager}')
                    for direction in [1, 2]:
                        step=1
                        timedelta = datetime.timedelta(minutes=0)
                        for level in levels:
                            logger.info(f'level: {level}')
                            if direction == 1:
                                if timedelta == datetime.timedelta(minutes=0):
                                    timedelta = datetime.timedelta(minutes=20)
                                logger.info(f'direction {direction}')
                                start_time = intersection
                                end_time = manager.start_time
                                # добавляем к каждому слоту количество студентов, доступных в этот слот, за исключением студентов,
                                # у которых уже есть группы, сортирую по возрастанию популярности (вначале менее популярные)
                                slots = Timeslot.objects.annotate(
                                    students_count=Coalesce(Subquery(StudentProjectSlot.objects.filter(
                                        student__week=week,
                                        student__student__level=level,
                                        slot_id=OuterRef('id')
                                    ).exclude(
                                        student__student__in=Student.objects.prefetch_related('student_group').filter(
                                            student_group__group__week=week,
                                        )).values('slot').annotate(count=Count('id')).values('count')[:1]
                                                                     ), 0
                                                            )
                                ).order_by('-start_time').filter(
                                    start_time__gte=end_time,
                                    end_time__lte=start_time,
                                    students_count__gt=1
                                ).all()
                                logger.info(f'slots: {slots}')
                                available_groups = Group.objects.filter(
                                    week=week,
                                    timeslot__start_time__gte=end_time,
                                    timeslot__end_time__lte=start_time,
                                    project_manager=manager.project_manager,
                                )
                                logger.info(f'available_groups: {available_groups}')
                                while slots and slots.first().students_count > 1 and available_groups:
                                    logger.info(f'step: {step}')
                                    logger.info(f'timedelta for {step}: {timedelta}')
                                    logger.info(f'количество студентов:{slots.first().students_count}')
                                    if slots.first().students_count > 5 or slots.first().students_count == 3:
                                        places = range(3)
                                    elif slots.first().students_count == 4 or slots.first().students_count == 2:
                                        places = range(2)
                                    else:
                                        logger.info('ELSE')
                                    slot_start_time = time_minus(start_time, timedelta)
                                    if slot_start_time < end_time:
                                        break
                                    logger.info(f'slot_start_time: {slot_start_time}')
                                    current_group = Group.objects.filter(
                                        week=week,
                                        timeslot__start_time=slot_start_time,
                                        project_manager=manager.project_manager,
                                        students__isnull=True,
                                    ).first()
                                    logger.info(f'current_group: {current_group}')
                                    available_students = StudentProjectSlot.objects.filter(
                                        slot__start_time=slot_start_time,
                                        student__week=week,
                                        student__student__level=level,
                                    ).exclude(
                                        student__student__in=Student.objects.prefetch_related(
                                            'student_group').filter(
                                            student_group__group__week=week,
                                        ))
                                    logger.info(f'available_students: {available_students}')
                                    for place in places:
                                        if current_group:
                                            available_students = StudentProjectSlot.objects.filter(
                                                slot__start_time=slot_start_time,
                                                student__week=week,
                                                student__student__level=level,
                                            ).exclude(
                                                student__student__in=Student.objects.prefetch_related(
                                                    'student_group').filter(
                                                    student_group__group__week=week,
                                                ))
                                            logger.info(f'available_students_count: {available_students.count()}')
                                            student = random.choice(available_students)
                                            current_group.students.add(student.student.student)

                                    timedelta += datetime.timedelta(minutes=20)
                                    logger.info(f'new_timedelta: {timedelta}')
                                    step+=1
                                    slots = Timeslot.objects.annotate(
                                        students_count=Coalesce(Subquery(StudentProjectSlot.objects.filter(
                                            student__week=week,
                                            student__student__level=level,
                                            slot_id=OuterRef('id')
                                        ).exclude(
                                            student__student__in=Student.objects.prefetch_related(
                                                'student_group').filter(
                                                student_group__group__week=week,
                                            )).values('slot').annotate(count=Count('id')).values('count')[:1]
                                                                         ), 0
                                                                )
                                    ).order_by('-start_time').filter(
                                        start_time__gte=end_time,
                                        end_time__lte=start_time,
                                        students_count__gt=1
                                    ).all()
                                    logger.info(f'slots for step {step}: {slots}')
                                    available_groups = Group.objects.filter(
                                        week=week,
                                        timeslot__start_time__gte=end_time,
                                        timeslot__end_time__lte=start_time,
                                        project_manager=manager.project_manager,
                                        students__isnull=True,
                                    )
                                    logger.info(f'available_groups for step {step}: {available_groups}')
                            if direction == 2:
                                logger.info(f'direction {direction}')
                                start_time = intersection
                                end_time = manager.end_time
                                slots = Timeslot.objects.annotate(
                                    students_count=Coalesce(Subquery(StudentProjectSlot.objects.filter(
                                        student__week=week,
                                        student__student__level=level,
                                        slot_id=OuterRef('id')
                                    ).exclude(
                                        student__student__in=Student.objects.prefetch_related('student_group').filter(
                                            student_group__group__week=week,
                                        )).values('slot').annotate(count=Count('id')).values('count')[:1]
                                                                     ), 0
                                                            )
                                ).order_by('-start_time').filter(
                                    start_time__gte=start_time,
                                    end_time__lte=end_time,
                                    students_count__gt=1
                                ).all()
                                logger.info(f'slots: {slots}')
                                available_groups = Group.objects.filter(
                                    week=week,
                                    timeslot__start_time__gte=start_time,
                                    timeslot__end_time__lte=end_time,
                                    project_manager=manager.project_manager,
                                )
                                logger.info(f'available_groups: {available_groups}')
                                while slots and slots.first().students_count > 1 and available_groups:
                                    logger.info(f'step: {step}')
                                    logger.info(f'timedelta for {step}: {timedelta}')
                                    logger.info(f'количество студентов:{slots.first().students_count}')
                                    if slots.first().students_count > 5 or slots.first().students_count == 3:
                                        places = range(3)
                                    elif slots.first().students_count == 4 or slots.first().students_count == 2:
                                        places = range(2)
                                    else:
                                        logger.info('ELSE')
                                    slot_start_time = time_plus(start_time, timedelta)
                                    if slot_start_time >= end_time:
                                        break
                                    logger.info(f'slot_start_time: {slot_start_time}')
                                    current_group = Group.objects.filter(
                                        week=week,
                                        timeslot__start_time=slot_start_time,
                                        project_manager=manager.project_manager,
                                        students__isnull=True,
                                    ).first()
                                    logger.info(f'current_group: {current_group}')

                                    for place in places:
                                        if current_group:
                                            available_students = StudentProjectSlot.objects.filter(
                                                slot__start_time=slot_start_time,
                                                student__week=week,
                                                student__student__level=level,
                                            ).exclude(
                                                student__student__in=Student.objects.prefetch_related(
                                                    'student_group').filter(
                                                    student_group__group__week=week,
                                                ))
                                            logger.info(f'available_students: {available_students}')
                                            student = random.choice(available_students)
                                            current_group.students.add(student.student.student)

                                    timedelta += datetime.timedelta(minutes=20)
                                    logger.info(f'new_timedelta: {timedelta}')
                                    step+=1
                                    slots = Timeslot.objects.annotate(
                                        students_count=Coalesce(Subquery(StudentProjectSlot.objects.filter(
                                            student__week=week,
                                            student__student__level=level,
                                            slot_id=OuterRef('id')
                                        ).exclude(
                                            student__student__in=Student.objects.prefetch_related(
                                                'student_group').filter(
                                                student_group__group__week=week,
                                            )).values('slot').annotate(count=Count('id')).values('count')[:1]
                                                                         ), 0
                                                                )
                                    ).order_by('-start_time').filter(
                                        start_time__gte=start_time,
                                        end_time__lte=end_time,
                                        students_count__gt=1
                                    ).all()
                                    logger.info(f'slots for step {step}: {slots}')
                                    available_groups = Group.objects.filter(
                                        week=week,
                                        timeslot__start_time__gte=start_time,
                                        timeslot__end_time__lte=end_time,
                                        project_manager=manager.project_manager,
                                        students__isnull=True,
                                    )
                                    logger.info(f'available_groups for step {step}: {available_groups}')


            return 'STUDENT_ASSIGNMENT'


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
                    CallbackQueryHandler(student_assignment, pattern='student_assignment'),
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
                'STUDENT_ASSIGNMENT': [
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
