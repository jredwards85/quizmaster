# Generated by Django 4.2.7 on 2023-12-04 09:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0013_quizinstance_completed_on'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quizinstance',
            name='completed_on',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Completed at'),
        ),
        migrations.AlterField(
            model_name='quizinstance',
            name='hosted_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Hosted at'),
        ),
    ]
