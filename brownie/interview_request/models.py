# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
import datetime

import django
from django.db import models
from django.utils import timezone

from django.contrib.postgres.fields import JSONField


class Users(models.Model):
    id = models.AutoField(primary_key=True)
    email = models.CharField(max_length=100, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    created_on = models.DateTimeField(default=timezone.now)
    modified_on = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = True
        db_table = 'users'


class Company(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20)
    google_play_app_id = models.CharField(max_length=20, null=True, default=None)
    created_on = models.DateTimeField(default=timezone.now)
    modified_on = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = True
        db_table = 'company'


class JobProfile(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20)
    created_on = models.DateTimeField(default=timezone.now)
    modified_on = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = True
        db_table = 'job_profile'


class InterviewRequest(models.Model):
    id = models.AutoField(primary_key=True)
    type_form_id = models.CharField(max_length=20)
    company = models.ForeignKey('Company', on_delete=models.CASCADE, null=False)
    user = models.ForeignKey('Users', on_delete=models.CASCADE, null=False)
    job_profile = models.ForeignKey('JobProfile', on_delete=models.CASCADE, null=False)
    is_visited_by_cron = models.BooleanField(default=False)
    created_on = models.DateTimeField(default=timezone.now)
    modified_on = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = True
        db_table = 'interview_request'


class InterviewRequestResult(models.Model):
    id = models.AutoField(primary_key=True)
    type_form_id = models.CharField(max_length=20)
    status = models.CharField(max_length=20)
    is_published = models.BooleanField(default=False)
    interview_request = models.ForeignKey('InterviewRequest', on_delete=models.CASCADE)
    company = models.ForeignKey('Company', on_delete=models.CASCADE)
    user = models.ForeignKey('Users', on_delete=models.CASCADE)
    created_on = models.DateTimeField(default=timezone.now)
    modified_on = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = True
        db_table = 'interview_request_result'


class TypeformWebhookData(models.Model):
    id = models.AutoField(primary_key=True)
    type_form_id = models.CharField(max_length=20)
    interview_request = models.ForeignKey('InterviewRequest', on_delete=models.CASCADE)
    data = JSONField()
    created_on = models.DateTimeField(default=timezone.now)
    modified_on = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = True
        db_table = 'typeform_webhook_data'
