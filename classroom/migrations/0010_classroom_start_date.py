# Generated by Django 5.1.1 on 2024-11-08 04:11

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classroom', '0009_rename_clasroom_id_meetings_classroom_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='classroom',
            name='start_date',
            field=models.DateField(default=datetime.date.today),
            preserve_default=False,
        ),
    ]
