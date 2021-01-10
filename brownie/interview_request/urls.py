from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from brownie.interview_request.views import TypeformWebhookView, GenerateReportView, HealthCheckView

app_name = "interview_request"
urlpatterns = [
    path("health/", view=HealthCheckView.as_view(), name="health"),
    path("typeform-webhook/", view=csrf_exempt(TypeformWebhookView.as_view()), name="webhook"),
    path("generate/", view=csrf_exempt(GenerateReportView.as_view()), name="generate-report"),
]
