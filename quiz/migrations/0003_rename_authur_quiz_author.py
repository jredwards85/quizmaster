# Generated by Django 4.2.7 on 2023-11-30 08:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0002_quiz_complete_alter_quiz_private'),
    ]

    operations = [
        migrations.RenameField(
            model_name='quiz',
            old_name='authur',
            new_name='author',
        ),
    ]
