# Generated by Django 3.0.11 on 2021-01-10 05:31

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('interview_request', '0004_auto_20210109_1739'),
    ]

    operations = [
        migrations.AddField(
            model_name='interviewrequestresult',
            name='data',
            field=django.contrib.postgres.fields.jsonb.JSONField(default={}),
            preserve_default=False,
        ),
    ]
