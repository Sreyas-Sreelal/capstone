# Generated by Django 5.1.1 on 2024-11-03 07:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classroom', '0005_alter_classroom_class_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='classroom',
            name='class_id',
            field=models.UUIDField(auto_created=True, primary_key=True, serialize=False, unique=True),
        ),
    ]
