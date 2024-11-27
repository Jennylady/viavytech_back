# Generated by Django 5.0 on 2024-11-24 10:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Quiz',
            fields=[
                ('id_quiz', models.AutoField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('question_text', models.TextField()),
                ('category', models.CharField(choices=[('mst', 'MST'), ('grossesse', 'Grossesse'), ('menstruation', 'Menstruation'), ('contraception', 'Methode contraceptive'), ('general', 'Géneral')], default='general', max_length=100)),
            ],
            options={
                'db_table': 'quiz',
            },
        ),
        migrations.CreateModel(
            name='ResponseQuiz',
            fields=[
                ('id_response_quiz', models.AutoField(primary_key=True, serialize=False)),
                ('content', models.TextField()),
                ('is_correct', models.BooleanField(default=False)),
                ('rank', models.PositiveIntegerField(default=0)),
                ('quiz', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='responses', to='quiz.quiz')),
            ],
            options={
                'db_table': 'responsequiz',
            },
        ),
    ]
