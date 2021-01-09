import json

from annoying.functions import get_object_or_None
from django.core.exceptions import ValidationError
from django.http.response import JsonResponse
from django.views import View

from brownie.interview_request.models import User, Company, InterviewRequest, JobProfile, TypeformWebhookData


class TypeformWebhookView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            email = data['email']
            user = get_object_or_None(User, email=email)
            if not user:
                user = User(email=email, first_name=data['first_name'],
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
            return JsonResponse({'message': 'Received successfully.'})
        except Exception as e:
            print("Error", e)
            raise ValidationError(message=e)
