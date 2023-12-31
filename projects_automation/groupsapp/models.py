import os
from datetime import time

from django.db import models
from dotenv import load_dotenv
from telegram import Bot


class Person(models.Model):
    firstname = models.CharField(
        max_length=40,
        verbose_name='Имя',
    )
    lastname = models.CharField(
        max_length=40,
        verbose_name='Фамилия',
    )
    telegram_id = models.PositiveBigIntegerField(
        verbose_name='Telegram id',
        db_index=True,
    )
    email = models.EmailField(
        verbose_name='Email')
    trello_id = models.CharField(
        max_length=100, verbose_name='ID Trello',
        blank=True)

    class Meta:
        verbose_name = 'Участник'
        verbose_name_plural = 'Участники'

    def __str__(self):
        return f'{self.firstname} {self.lastname}'


class Student(Person):
    LEVELS = [
        ('1_newborn', 'Новички'),
        ('2_newborn_plus', 'Новички+'),
        ('3_junior', 'Джуны'),
    ]
    level = models.CharField(
        verbose_name='Уровень',
        max_length=15,
        choices=LEVELS,
        default='1_newborn',
        db_index=True,
    )
    location_FE = models.BooleanField(
        verbose_name='Дальний Восток',
        default=False,
    )

    class Meta:
        verbose_name = 'Студент'
        verbose_name_plural = 'Студенты'

    def __str__(self):
        return f'{self.firstname} {self.lastname} - {self.get_level_display()}'


class Project_manager(Person):
    class Meta:
        verbose_name = 'Менеджер проектов'
        verbose_name_plural = 'Менеджеры проектов'

    def __str__(self):
        return f'{self.firstname} {self.lastname}'


class Project(models.Model):
    name = models.CharField(
        verbose_name='Название проекта',
        max_length=100,
    )

    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'

    def __str__(self):
        return f'{self.name}'


class Week(models.Model):
    start_date = models.DateField(
        verbose_name='Дата начала',
    )
    end_date = models.DateField(
        verbose_name='Дата окончания'
    )
    project = models.ForeignKey(
        Project,
        verbose_name='Проект',
        on_delete=models.PROTECT,
        related_name='weeks',
    )
    actual = models.BooleanField(
        verbose_name='Идёт набор команд',
        default=False,
    )
    trello_link = models.URLField(
        verbose_name='Ссылка на Trello', blank=True)
    trello_id = models.CharField(
        max_length=100, verbose_name='ID Trello',
        blank=True)

    class Meta:
        verbose_name = 'Неделя'
        verbose_name_plural = 'Недели'

    def __str__(self):
        return f'{self.start_date}'

    def save(self, *args, **kwargs):
        super(Week, self).save(*args, **kwargs)
        load_dotenv()
        tg_bot_key = os.getenv('TG_API_KEY')
        bot = Bot(token=tg_bot_key)

        if not self.actual:
            return

        students = Student.objects.all()

        for student in students:
            user_id = student.telegram_id
            message = ('Настало время проектов. '
                       'тобы выбрать себе удобное время для '
                       'созвонов, введите /start')
            try:
                bot.send_message(text=message, chat_id=user_id)
            except Exception:
                pass


class Timeslot(models.Model):
    start_time = models.TimeField(
        verbose_name='Время начала',
    )
    end_time = models.TimeField(
        verbose_name='Время окончания',
    )

    class Meta:
        verbose_name = 'Временной слот'
        verbose_name_plural = 'Временные слоты'

    def __str__(self):
        start = time.strftime(self.start_time, '%H:%M')
        end = time.strftime(self.end_time, '%H:%M')
        return f'{start} - {end}'


class PMSchedule(models.Model):
    project_manager = models.ForeignKey(
        Project_manager,
        verbose_name='Менеджер проекта',
        on_delete=models.PROTECT,
        related_name='schedule',
    )
    start_time = models.TimeField(
        verbose_name='Время начала',
    )
    end_time = models.TimeField(
        verbose_name='Время окончания',
    )

    class Meta:
        verbose_name = 'Расписание менеджера проекта'
        verbose_name_plural = 'Расписания менеджеров проектов'

    def __str__(self):
        return f'{self.project_manager}: {self.start_time} - {self.end_time}'


class StudentProjectWeek(models.Model):
    week = models.ForeignKey(
        Week,
        verbose_name='Неделя',
        on_delete=models.PROTECT,
        related_name='schedule',
    )
    student = models.ForeignKey(
        Student,
        verbose_name='Студент',
        on_delete=models.PROTECT,
        related_name='schedule',
    )

    class Meta:
        verbose_name = 'Студенты по неделям'
        verbose_name_plural = 'Студенты по неделям'

    def __str__(self):
        student = (self.student.firstname +
                   ' ' + self.student.lastname)
        return f'{self.pk}: {self.week}: {student}'


class StudentProjectSlot(models.Model):
    student = models.ForeignKey(
        StudentProjectWeek,
        verbose_name='Студент',
        on_delete=models.PROTECT,
        related_name='slots',
    )
    slot = models.ForeignKey(
        Timeslot,
        verbose_name='Временной слот',
        on_delete=models.PROTECT,
        related_name='schedule',
    )

    class Meta:
        verbose_name = 'Слоты студента'
        verbose_name_plural = 'Слоты студентов'

    def __str__(self):
        student = (self.student.student.firstname +
                   ' ' + self.student.student.lastname)
        slot = self.slot
        return f'{student}: {slot}'


class Group(models.Model):
    week = models.ForeignKey(
        Week,
        verbose_name='Проект',
        on_delete=models.PROTECT,
        related_name='groups',
    )
    timeslot = models.ForeignKey(
        Timeslot,
        verbose_name='Временной слот',
        on_delete=models.PROTECT,
        related_name='groups',
    )
    students = models.ManyToManyField(
        Student,
        verbose_name='Студенты',
        related_name='groups',
        through='StudentGroup',
    )
    project_manager = models.ForeignKey(
        Project_manager,
        verbose_name='Менеджер проекта',
        on_delete=models.PROTECT,
        related_name='groups',
    )
    trello_link = models.URLField(
        verbose_name='Ссылка на Trello', blank=True)
    trello_id = models.CharField(
        max_length=100, verbose_name='ID Trello',
        blank=True)

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    def __str__(self):
        project = self.week.project.name
        start = self.week.start_date
        manager = self.project_manager.lastname
        timeslot = self.timeslot
        return f'{project} ({start}) - {manager} - {timeslot}'


class StudentGroup(models.Model):
    group = models.ForeignKey(
        Group,
        verbose_name='Группа',
        on_delete=models.PROTECT,
    )
    student = models.ForeignKey(
        Student,
        verbose_name='Студент',
        on_delete=models.PROTECT,
        related_name='student_group',
    )

    class Meta:
        verbose_name = 'Студент в группе'
        verbose_name_plural = 'Студенты в группах'

    def __str__(self):
        return f'{self.student}: {self.group}'

    def save(self, *args, **kwargs):
        super(StudentGroup, self).save(*args, **kwargs)
        load_dotenv()
        tg_bot_key = os.getenv('TG_API_KEY')
        user_id = self.student.telegram_id
        bot = Bot(token=tg_bot_key)
        message = f'Вам назначили время проекта и ПМ-а: {self.group}'
        try:
            bot.send_message(text=message, chat_id=user_id)
        except Exception:
            pass
