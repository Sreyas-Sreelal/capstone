# Generated by Django 5.1.1 on 2024-11-09 04:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classroom', '0011_alter_meetings_meeting_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='meetings',
            name='conducted',
            field=models.BooleanField(default=False),
        ),
    ]
