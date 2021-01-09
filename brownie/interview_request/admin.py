from django.contrib import admin

# Register your models here.
from brownie.interview_request.models import InterviewRequestResult, User, Company, JobProfile, InterviewRequest, \
    TypeformWebhookData

admin.site.register(User)
admin.site.register(Company)
admin.site.register(JobProfile)
admin.site.register(InterviewRequest)
admin.site.register(InterviewRequestResult)
admin.site.register(TypeformWebhookData)
