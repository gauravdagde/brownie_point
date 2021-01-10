from adminactions import actions
from django.contrib import admin
from django.contrib.admin import site

from brownie.interview_request.models import InterviewRequestResult, User, Company, JobProfile, InterviewRequest, \
    TypeformWebhookData

actions.add_to_site(site)
admin.site.site_header = 'Interview Brownie Point'
admin.site.register(User)
admin.site.register(Company)
admin.site.register(JobProfile)
admin.site.register(InterviewRequest)
admin.site.register(InterviewRequestResult)
admin.site.register(TypeformWebhookData)
