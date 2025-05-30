# Generated by Django 5.0 on 2024-11-24 18:35

import apps.users.models
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0002_alter_quiz_category'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='QuizFinished',
            fields=[
                ('id_quiz_finished', models.AutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(default=apps.users.models.default_created_at)),
                ('quiz', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='quiz_finished', to='quiz.quiz')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='quiz_finished', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'quiz_finished',
            },
        ),
    ]
