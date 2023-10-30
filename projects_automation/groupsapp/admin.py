from datetime import time

from django.conf import settings
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from import_export.admin import ImportExportModelAdmin

from .models import (
    Person,
    Student,
    Project_manager,
    Project,
    Week,
    Timeslot,
    PMSchedule,
    StudentProjectWeek,
    StudentProjectSlot,
    Group,
    StudentGroup,
)
from .trello_api import (
    create_project_name,
    create_workspace,
    delete_workspace,
    create_board,
    delete_board,
    invite_member_to_board_via_email
)

trello_key = settings.TRELLO_API_KEY
trello_token = settings.TRELLO_API_TOKEN


class ByLevelFilter(admin.SimpleListFilter):
    title = _('Уровень')
    parameter_name = 'student'

    def lookups(self, request, model_admin):

        filters = [
            ('1_newborn', 'Новички'),
            ('2_newborn_plus', 'Новички+'),
            ('3_junior', 'Джуны'),
        ]

        return filters if filters else None

    def queryset(self, request, queryset):
        if self.value() is not None:
            level = Student.objects.filter(level=self.value())
            return queryset.filter(student__in=level)
        return queryset


@admin.register(Person)
class PersonAdmin(ImportExportModelAdmin):
    list_display = ['firstname', 'lastname', 'telegram_id', 'email']
    list_editable = ['telegram_id', 'email']
    list_per_page = 20


@admin.register(Student)
class StudentAdmin(ImportExportModelAdmin):
    list_filter = (
        'level',
    )
    list_per_page = 20


@admin.register(Project_manager)
class Project_managerAdmin(ImportExportModelAdmin):
    list_per_page = 20


@admin.register(Project)
class ProjectAdmin(ImportExportModelAdmin):
    list_per_page = 20


@admin.register(Week)
class WeekAdmin(ImportExportModelAdmin):
    list_display = ['project', 'start_date', 'end_date', 'get_trello_link']
    list_filter = ['actual', 'start_date', 'end_date']
    list_per_page = 20
    actions = ['create_trello', 'delete_workspace']

    def get_trello_link(self, obj):
        if obj.trello_link:
            return format_html(
                f'<a href="{obj.trello_link}" target="_blank">'
                f'перейти на Trello</a>')
        return 'ссылка отсутствует'

    get_trello_link.short_description = 'trello'

    @admin.action(description='* создать Trello')
    def create_trello(self, request, queryset):
        """Возвращает id и ссылку на рабочее пространство в Trello"""
        try:
            for obj in queryset:
                if not obj.trello_id:
                    project_name = create_project_name(
                        obj.project.name, obj.start_date, obj.end_date)
                    workspace = create_workspace(
                        trello_key, trello_token, project_name)
                    obj.trello_link = workspace['url']
                    obj.trello_id = workspace['id']
                    obj.save()
        except Exception as e:
            print(e)
            pass

    @admin.action(description='* удалить Trello')
    def delete_workspace(self, request, queryset):
        """Удаляет рабочее пространство в Trello"""
        try:
            for obj in queryset:
                if obj.trello_id:
                    delete_board(trello_key, trello_token, obj.trello_id)
                    obj.trello_link = ''
                    obj.trello_id = ''
                    obj.save()
        except Exception as e:
            print(e)
            pass


@admin.register(Timeslot)
class TimeslotAdmin(ImportExportModelAdmin):
    list_per_page = 20


@admin.register(PMSchedule)
class PMScheduleAdmin(ImportExportModelAdmin):
    list_per_page = 20


@admin.register(StudentProjectWeek)
class StudentProjectWeekAdmin(ImportExportModelAdmin):
    list_filter = (
        ByLevelFilter,
        'week',
    )
    list_per_page = 20


@admin.register(StudentProjectSlot)
class StudentProjectSlotAdmin(ImportExportModelAdmin):
    list_per_page = 20


@admin.register(Group)
class GroupAdmin(ImportExportModelAdmin):
    list_display = ['week', 'timeslot', 'project_manager', 'get_trello_link']
    readonly_fields = ['trello_link']
    list_filter = ['project_manager']
    list_per_page = 20
    actions = ['create_ws_board', 'invite_members',
               'delete_ws_board']

    def get_trello_link(self, obj):
        if obj.trello_link:
            return format_html(
                f'<a href="{obj.trello_link}" target="_blank">'
                f'перейти на Trello</a>')
        return 'нет доски'

    get_trello_link.short_description = 'trello'

    @admin.action(description='* создать доску')
    def create_ws_board(self, request, queryset):
        """Создает доску в Trello"""
        try:
            for obj in queryset:
                if not obj.week.trello_id:
                    continue
                if not obj.trello_id:
                    calltime = time.strftime(obj.timeslot.start_time,
                                             '%H:%M')
                    participants = ', '.join(
                        obj.students.all().values_list(
                            'lastname', flat=True))
                    board_name = (f'[{calltime}] '
                                  f'{obj.project_manager.lastname} '
                                  f'- {participants}')
                    board = create_board(
                        trello_key, trello_token,
                        ws_id=obj.week.trello_id,
                        board_name=board_name,
                        background='blue')
                    obj.trello_link = board['shortUrl']
                    obj.trello_id = board['id']
                    obj.save()
        except Exception as e:
            print(e)
            pass

    @admin.action(description='* удалить доску')
    def delete_ws_board(self, request, queryset):
        """Удаляет доску в Trello"""
        try:
            for obj in queryset:
                if obj.trello_id:
                    delete_board(trello_key, trello_token, obj.trello_id)
                    obj.trello_link = ''
                    obj.trello_id = ''
                    obj.save()
        except Exception as e:
            print(e)
            pass

    @admin.action(description='* отправить ссылку')
    def invite_members(self, request, queryset):
        """Направляет участникам письмо со ссылкой на доску Trello."""
        try:
            for obj in queryset:
                if obj.trello_id:
                    member_id = invite_member_to_board_via_email(
                        trello_key, trello_token, obj.trello_id,
                        obj.project_manager.email,
                        obj.project_manager.fullname)
                    obj.project_manager.trello_id = member_id
                    obj.project_manager.save()

                    for student in obj.students.all():
                        member_id = invite_member_to_board_via_email(
                            trello_key, trello_token, obj.trello_id,
                            student.email, student.fullname)
                        student.trello_id = member_id
                        student.save()
                        obj.save()
        except Exception as e:
            print(e)
            pass


@admin.register(StudentGroup)
class StudentGroupAdmin(ImportExportModelAdmin):
    list_per_page = 20
