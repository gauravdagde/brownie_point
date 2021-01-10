from django.contrib import admin

from brownie.interview_request.models import InterviewRequestResult, User, Company, JobProfile, InterviewRequest, \
    TypeformWebhookData

admin.site.site_header = 'Interview Brownie Point'
admin.site.register(User)
admin.site.register(Company)
admin.site.register(JobProfile)
admin.site.register(InterviewRequest)
admin.site.register(InterviewRequestResult)
admin.site.register(TypeformWebhookData)
