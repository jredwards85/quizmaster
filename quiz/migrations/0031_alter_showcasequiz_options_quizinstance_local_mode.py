# Generated by Django 4.2.7 on 2023-12-13 18:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0030_showcasequiz'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='showcasequiz',
            options={'verbose_name_plural': 'ShowcaseQuiz'},
        ),
        migrations.AddField(
            model_name='quizinstance',
            name='local_mode',
            field=models.BooleanField(default=False, verbose_name='Local Mode'),
        ),
    ]
