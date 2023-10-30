# Generated by Django 3.2.15 on 2023-10-30 06:42

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('groupsapp', '0002_week_actual'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='email',
            field=models.EmailField(default=datetime.datetime(2023, 10, 30, 6, 42, 13, 73956, tzinfo=utc), max_length=254, verbose_name='Email'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='person',
            name='trello_id',
            field=models.CharField(blank=True, max_length=100, verbose_name='ID Trello'),
        ),
        migrations.AddField(
            model_name='week',
            name='end_date',
            field=models.DateField(blank=True, default=datetime.datetime(2023, 10, 30, 6, 41, 50, 451003, tzinfo=utc), verbose_name='Дата окончания'),
        ),
    ]