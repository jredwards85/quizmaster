# Generated by Django 4.2.7 on 2023-12-04 13:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0015_quizinstance_instance_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='participant',
            name='archived',
            field=models.BooleanField(default=False, verbose_name='Archived status'),
        ),
    ]
