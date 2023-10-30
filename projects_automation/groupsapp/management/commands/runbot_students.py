from django.core.management.base import BaseCommand

from groupsapp.tg_bot.start_bot import start_bot

import os
from dotenv import load_dotenv


class Command(BaseCommand):
    def handle(self, *args, **options):
        load_dotenv()

        TG_API_KEY = os.getenv('TG_API_KEY')
        start_bot(TG_API_KEY)

