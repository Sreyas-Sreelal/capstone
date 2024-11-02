# Generated by Django 5.1.1 on 2024-11-02 11:42

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Classroom',
            fields=[
                ('class_id', models.UUIDField(primary_key=True, serialize=False)),
                ('trainer_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='authentication.user')),
            ],
        ),
        migrations.CreateModel(
            name='ClassMember',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('member', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='authentication.user')),
                ('class_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='classroom.classroom')),
            ],
        ),
        migrations.CreateModel(
            name='ClassCourse',
            fields=[
                ('sno', models.AutoField(primary_key=True, serialize=False)),
                ('class_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='classroom.classroom')),
            ],
        ),
    ]
