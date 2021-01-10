from django.apps import AppConfig


class InterviewRequestConfig(AppConfig):
    name = 'brownie.interview_request'

    def ready(self):
        from brownie.utils import scheduler
        scheduler.start()
