import datetime

from groupsapp.models import Project_manager, Week, Timeslot, Group, Student, StudentProjectWeek, StudentProjectSlot, PMSchedule


def get_student_by_tg(telegram_id):
    return Student.objects.get(telegram_id=telegram_id)


def get_available_intervals():
    pm_intervals = PMSchedule.objects.all().order_by('start_time', 'end_time')

    intervals = []
    start = pm_intervals[0].start_time
    end = pm_intervals[0].end_time

    for i, interval in enumerate(pm_intervals):
        if i == len(pm_intervals) - 1:
            intervals.append({'start': start, 'end': end})
            break

        next_interval = pm_intervals[i+1]

        if end < next_interval.start_time:
            intervals.append((start, end))
            start = next_interval.start_time
            end = next_interval.end_time
            continue

        if end > next_interval.end_time:
            continue

        end = next_interval.end_time

    return intervals


def interval_to_text(interval):
    start = interval['start'].strftime("%H:%M")
    end = interval['end'].strftime("%H:%M")
    interval_name = f'{start}-{end}'
    return interval_name
