# Generated by Django 5.1.1 on 2024-11-04 09:57

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Chapter',
            fields=[
                ('chapter_id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('chapter_name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('course_id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('course_name', models.TextField()),
                ('course_type', models.CharField(max_length=20)),
                ('deliverables', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Assesment',
            fields=[
                ('question_id', models.AutoField(primary_key=True, serialize=False)),
                ('question', models.TextField()),
                ('option_1', models.TextField()),
                ('option_2', models.TextField()),
                ('option_3', models.TextField()),
                ('option_4', models.TextField()),
                ('correct_option', models.TextField()),
                ('chapter_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='course.chapter')),
            ],
        ),
        migrations.CreateModel(
            name='ChapterUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(max_length=100)),
                ('chapter_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='course.chapter')),
            ],
        ),
        migrations.CreateModel(
            name='Module',
            fields=[
                ('module_id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('module_name', models.CharField(max_length=50)),
                ('course_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='course.course')),
            ],
        ),
        migrations.AddField(
            model_name='chapter',
            name='module_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='course.module'),
        ),
        migrations.CreateModel(
            name='UserProgress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.IntegerField()),
                ('attempted', models.BooleanField(default=False)),
                ('chapter_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='course.chapter')),
            ],
        ),
    ]
