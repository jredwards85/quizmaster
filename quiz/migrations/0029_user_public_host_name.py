# Generated by Django 4.2.7 on 2023-12-09 10:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0028_alter_quizinstance_multichoice_only'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='public_host_name',
            field=models.CharField(blank=True, default='', max_length=50, null=True, verbose_name='Public Host Name'),
        ),
    ]