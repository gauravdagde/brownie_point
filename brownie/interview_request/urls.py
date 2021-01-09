from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from brownie.interview_request.views import TypeformWebhookView

app_name = "interview_request"
urlpatterns = [
    path("typeform-webhook/", view=csrf_exempt(TypeformWebhookView.as_view()), name="webhook"),
]
