# Generated by Django 4.2.7 on 2023-12-04 09:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0012_quizinstance_archived'),
    ]

    operations = [
        migrations.AddField(
            model_name='quizinstance',
            name='completed_on',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
