# Generated by Django 3.0.11 on 2021-01-10 20:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interview_request', '0006_auto_20210110_1908'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='google_play_app_id',
            field=models.CharField(default=None, max_length=100, null=True),
        ),
    ]
