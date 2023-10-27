from django import forms
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
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
from django.utils.translation import gettext_lazy as _
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
            return queryset.filter(student__in=Student.objects.filter(level=self.value()))
        else:
            return queryset


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    pass

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_filter = (
        'level',
    )


@admin.register(Project_manager)
class Project_managerAdmin(admin.ModelAdmin):
    pass


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    pass


@admin.register(Week)
class WeekAdmin(admin.ModelAdmin):
    pass


@admin.register(Timeslot)
class TimeslotAdmin(admin.ModelAdmin):
    pass


@admin.register(PMSchedule)
class PMScheduleAdmin(admin.ModelAdmin):
    pass


@admin.register(StudentProjectWeek)
class StudentProjectWeekAdmin(admin.ModelAdmin):
    list_filter = (
        ByLevelFilter,
        'week',
    )


@admin.register(StudentProjectSlot)
class StudentProjectSlotAdmin(admin.ModelAdmin):
    pass


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    pass


@admin.register(StudentGroup)
class StudentGroupAdmin(admin.ModelAdmin):
    pass
