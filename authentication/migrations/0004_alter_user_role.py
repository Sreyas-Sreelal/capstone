# Generated by Django 5.1.1 on 2024-11-05 08:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0003_alter_user_certifications'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(default='employee', max_length=200),
        ),
    ]
