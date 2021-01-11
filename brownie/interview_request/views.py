import json

from annoying.functions import get_object_or_None
from django.core.exceptions import ValidationError
from django.http.response import JsonResponse
from django.views import View

from brownie.interview_request.models import User, Company, InterviewRequest, JobProfile, TypeformWebhookData
from brownie.utils.tasks import get_google_play_store_app_id

field_mapping_dict = {
    '9129320': 'first_name',
    '7Yu2iCMEfpBT': 'last_name',
    'mDjKcHAvbZmq': 'email',
    'Vmo2TlXAsJ4h': 'company_name',
    'wjr77EnQTSlL': 'job_profile',
}


class HealthCheckView(View):
    def get(self, request):
        return JsonResponse({'message': 'Healthy host'})


class TypeformWebhookView(View):
    def post(self, request):
        try:
            payload = json.loads(request.body)
            form_response = payload['form_response']
            data = {}
            for answer in form_response['answers']:
                text = ''
                if answer['type'] == 'text':
                    text = answer['text']
                elif answer['type'] == 'choice':
                    text = answer['choice']['label']
                elif answer['type'] == 'email':
                    text = answer['email']
                data[field_mapping_dict[answer['field']['id']]] = text
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

            google_play_store_app_id = get_google_play_store_app_id(company_name)
            if google_play_store_app_id:
                company.google_play_app_id = google_play_store_app_id
                company.save()

            job_profile_title = data['job_profile']
            job_profile = get_object_or_None(JobProfile, name=job_profile_title)
            if not job_profile:
                job_profile = JobProfile(name=job_profile_title)
                job_profile.save()

            typeform_id = form_response['form_id']
            interview_request = get_object_or_None(InterviewRequest, type_form_id=typeform_id,
                                                   company_id=company.id,
                                                   user_id=user.id,
                                                   job_profile_id=job_profile.id)
            if not interview_request:
                interview_request = InterviewRequest(type_form_id=typeform_id,
                                                     company_id=company.id,
                                                     user_id=user.id,
                                                     job_profile_id=job_profile.id)
                interview_request.save()

            typeform_webhook_data = TypeformWebhookData(data=payload,
                                                        type_form_id=typeform_id,
                                                        interview_request_id=interview_request.id)
            typeform_webhook_data.save()

            # use celery for fast response
            # tasks.execute_interview_request.delay(interview_request.id)

            return JsonResponse({'message': 'Received successfully.'})
        except Exception as e:
            print("Error", e)
            raise ValidationError(message=e)


class GenerateReportView(View):
    def post(self, request):
        try:
            payload = json.loads(request.body)
            interview_request = payload['interview_request_id']
            # tasks.execute_interview_request(interview_request)
            return JsonResponse({'message': 'Not supported now, deprecated this'})
        except Exception as e:
            print("Error", e)
            raise ValidationError(message=e)
