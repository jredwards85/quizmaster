# Generated by Django 4.2.7 on 2023-11-30 08:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0003_rename_authur_quiz_author'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quiz',
            name='private',
            field=models.BooleanField(default=False, verbose_name='Marked as private (no for public hosting)'),
        ),
    ]
