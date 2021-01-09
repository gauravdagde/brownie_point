import json

from annoying.functions import get_object_or_None
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.http.response import JsonResponse
from django.shortcuts import render
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from brownie.interview_request.models import Users, Company, InterviewRequest, JobProfile, TypeformWebhookData
from brownie.utils import tasks


class TypeformWebhookView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            email = data['email']
            user = get_object_or_None(Users, email=email)
            if not user:
                user = Users(email=email, first_name=data['first_name'],
                             last_name=data['last_name'])
                user.save()

            company_name = data['company_name']
            company = get_object_or_None(Company, name=company_name)
            if not company:
                company = Company(name=company_name)
                company.save()

            job_profile_title = data['job_profile']
            job_profile = get_object_or_None(JobProfile, name=job_profile_title)
            if not job_profile:
                job_profile = JobProfile(name=job_profile_title)
                job_profile.save()

            interview_request = get_object_or_None(InterviewRequest, type_form_id=data['id'],
                                                   company_id=company.id,
                                                   user_id=user.id,
                                                   job_profile_id=job_profile.id)
            if not interview_request:
                interview_request = InterviewRequest(type_form_id=data['id'],
                                                     company_id=company.id,
                                                     user_id=user.id,
                                                     job_profile_id=job_profile.id)
                interview_request.save()

            typeform_webhook_data = TypeformWebhookData(data=data,
                                                        type_form_id=data['id'],
                                                        interview_request_id=interview_request.id)
            typeform_webhook_data.save()

            # use celery for fast response
            # tasks.execute_interview_request.delay(interview_request.id)

            return JsonResponse({'message': 'Received successfully.'})
        except Exception as e:
            print("Error", e)
            raise ValidationError(message=e)
