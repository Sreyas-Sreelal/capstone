# Generated by Django 5.1.1 on 2024-11-07 06:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('classroom', '0008_meetings'),
    ]

    operations = [
        migrations.RenameField(
            model_name='meetings',
            old_name='clasroom_id',
            new_name='classroom_id',
        ),
    ]