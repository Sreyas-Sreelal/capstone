# Generated by Django 5.1.1 on 2024-11-06 04:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('classroom', '0005_classroom_eod'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='curriculum',
            name='curriculum_name',
        ),
    ]