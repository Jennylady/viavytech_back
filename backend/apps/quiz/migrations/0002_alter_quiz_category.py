# Generated by Django 5.0 on 2024-11-24 18:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quiz',
            name='category',
            field=models.CharField(choices=[('mst', 'MST'), ('grossesse', 'Grossesse'), ('menstruation', 'Menstruation'), ('contraception', 'Methode contraceptive')], max_length=100),
        ),
    ]
