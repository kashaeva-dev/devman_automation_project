import datetime

import django.db.models
from groupsapp.models import (
    Week,
    Timeslot,
    Student,
    StudentProjectWeek,
    StudentProjectSlot,
    PMSchedule
)


def get_student_by_tg(telegram_id):
    student = Student.objects.get(telegram_id=telegram_id)
    if student:
        return student
    return None


def get_available_intervals():
    pm_intervals = PMSchedule.objects.all().order_by('start_time', 'end_time')

    full_intervals = []
    start = pm_intervals[0].start_time
    end = pm_intervals[0].end_time

    for i, interval in enumerate(pm_intervals):
        if i == len(pm_intervals) - 1:
            full_intervals.append({'start': start, 'end': end})
            break

        next_interval = pm_intervals[i+1]

        if end < next_interval.start_time:
            full_intervals.append((start, end))
            start = next_interval.start_time
            end = next_interval.end_time
            continue

        if end > next_interval.end_time:
            continue

        end = next_interval.end_time

    #  Делим на интервалы по 3 часа
    intervals = []
    for full_interval in full_intervals:
        start = full_interval['start']
        time = start.hour+3
        if time > 23:
            time = 23
        end_in_3_hours = datetime.time(time)
        while end_in_3_hours < full_interval['end']:
            end = end_in_3_hours
            interval = {'start': start, 'end': end}
            start = end
            time = start.hour + 3
            if time > 23:
                time = 23
            end_in_3_hours = datetime.time(time)
            intervals.append(interval)
        interval = {'start': start, 'end': full_interval['end']}
        intervals.append(interval)

    if not intervals:
        intervals = full_intervals

    return intervals


def interval_to_text(interval):
    start = interval['start'].strftime("%H:%M")
    end = interval['end'].strftime("%H:%M")
    interval_name = f'{start}-{end}'
    return interval_name


def text_to_interval(interval_name):
    start_end = interval_name.split("-")
    start = datetime.datetime.strptime(start_end[0], '%H:%M').time()
    end = datetime.datetime.strptime(start_end[1], '%H:%M').time()
    return start, end


def get_slots_from_interval(interval) -> django.db.models.QuerySet:
    slots = Timeslot.objects.filter(
        start_time__gte=interval['start'],
        end_time__lte=interval['end'])
    return slots


def save_chosen_slots(student: Student, week: Week, slots: [Timeslot]):
    student_week, created = StudentProjectWeek.objects.get_or_create(
        week=week, student=student)
    student_slots = [
        StudentProjectSlot(
            student=student_week, slot=slot) for slot in slots
    ]
    StudentProjectSlot.objects.bulk_create(student_slots)


def decline_student(student, week):
    try:
        student_week = StudentProjectWeek.objects.get(
            week=week, student=student)
    except StudentProjectWeek.DoesNotExist:
        student_week = None

    if not student_week:
        return

    group = student.groups.filter(week=week)
    if group:
        group.remove(student)
    student_week.slots.all().delete()
    student_week.delete()
