# Generated by Django 4.2.7 on 2023-12-04 18:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0017_quiz_edit_only_quiz_hidden'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='quizinstance',
            name='custom_name',
        ),
    ]
