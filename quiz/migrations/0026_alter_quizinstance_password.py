# Generated by Django 4.2.7 on 2023-12-07 14:32

from django.db import migrations, models
import quiz.models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0025_remove_quizinstance_instance_type_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quizinstance',
            name='password',
            field=models.CharField(blank=True, default=quiz.models.generate_unique_string, max_length=50, null=True, verbose_name='Password'),
        ),
    ]
