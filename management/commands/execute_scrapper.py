from django.core.management.base import BaseCommand, CommandError

from brownie.utils.cron import execute_interview_request


class Command(BaseCommand):
    help = 'Runs the cron'

    def handle(self, *args, **options):
        execute_interview_request()