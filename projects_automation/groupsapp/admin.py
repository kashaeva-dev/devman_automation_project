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


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    pass

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    pass


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
    pass


@admin.register(StudentProjectSlot)
class StudentProjectSlotAdmin(admin.ModelAdmin):
    pass


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    pass


@admin.register(StudentGroup)
class StudentGroupAdmin(admin.ModelAdmin):
    pass
