# Generated by Django 4.2.7 on 2023-12-07 15:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0026_alter_quizinstance_password'),
    ]

    operations = [
        migrations.AddField(
            model_name='quizinstance',
            name='multichoice_only',
            field=models.BooleanField(default=False, verbose_name='Archived status'),
        ),
    ]
