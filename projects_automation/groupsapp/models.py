from django.db import models


class Student(models.Model):
    LEVELS = [
        ('1_newborn', 'Новички'),
        ('2_newborn_plus', 'Новички+'),
        ('3_junior', 'Джуны'),
    ]
    firstname = models.CharField(
        max_length=40,
        verbose_name='Имя',
    )
    lastname = models.CharField(
        max_length=100,
        verbose_name='Фамилия'
    )
    telegram_id = models.PositiveBigIntegerField(
        verbose_name='Telegram id',
        db_index=True,
    )
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
        return f'{self.firstname} {self.lastname}'


class Project_manager(models.Model):
    firstname = models.CharField(
        max_length=40,
        verbose_name='Имя',
    )
    lastname = models.CharField(
        max_length=100,
        verbose_name='Фамилия'
    )
    telegram_id = models.PositiveBigIntegerField(
        verbose_name='Telegram id',
        db_index=True,
    )

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
    start_date = models.DateField(
        verbose_name='Дата начала',
    )
    end_date = models.DateField(
        verbose_name='Дата окончания',
    )

    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'

    def __str__(self):
        return f'{self.name}'


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
        return f'{self.start_time} - {self.end_time}'


class Trello_board(models.Model):
    name = models.CharField(
        verbose_name='Название доски',
        max_length=200,
    )
    url = models.URLField(
        verbose_name='Ссылка на доску',
    )

    class Meta:
        verbose_name = 'Доска Trello'
        verbose_name_plural = 'Доски Trello'

    def __str__(self):
        return f'{self.name}'


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

class StudentSchedule(models.Model):
    project = models.ForeignKey(
        Project,
        verbose_name='Проект',
        on_delete=models.PROTECT,
        related_name='schedule',
    )
    student = models.ForeignKey(
        Student,
        verbose_name='Студент',
        on_delete=models.PROTECT,
        related_name='schedule',
    )
    slot = models.ForeignKey(
        Timeslot,
        verbose_name='Временной слот',
        on_delete=models.PROTECT,
        related_name='schedule',
    )

    class Meta:
        verbose_name = 'Расписание студента'
        verbose_name_plural = 'Расписания студентов'

    def __str__(self):
        return f'{self.student}: {self.slot}'


class Group(models.Model):
    project = models.ForeignKey(
        Project,
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
    trello_board = models.ForeignKey(
        Trello_board,
        verbose_name='Доска Trello',
        on_delete=models.PROTECT,
        related_name='groups',
    )

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    def __str__(self):
        return f'{self.project} - {self.project_manager.lastname} - {self.timeslot}'


class StudentGroup(models.Model):
    Group = models.ForeignKey(
        Group,
        verbose_name='Группа',
        on_delete=models.PROTECT,
        related_name='students',
    )
    student = models.ForeignKey(
        Student,
        verbose_name='Студент',
        on_delete=models.PROTECT,
        related_name='groups',
    )

    class Meta:
        verbose_name = 'Студент в группе'
        verbose_name_plural = 'Студенты в группах'

    def __str__(self):
        return f'{self.student}: {self.Group}'
