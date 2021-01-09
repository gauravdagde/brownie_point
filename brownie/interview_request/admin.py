from django.contrib import admin

# Register your models here.
from brownie.interview_request.models import InterviewRequestResult, Users, Company, JobProfile, InterviewRequest, \
    TypeformWebhookData

admin.register(Users)
admin.register(Company)
admin.register(JobProfile)
admin.register(InterviewRequest)
admin.register(InterviewRequestResult)
admin.register(TypeformWebhookData)
