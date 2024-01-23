# Generated by Django 4.2.7 on 2023-12-06 08:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0020_quizreviews'),
    ]

    operations = [
        migrations.AddField(
            model_name='quizinstance',
            name='player',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='player', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='quizinstance',
            name='host',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='host', to=settings.AUTH_USER_MODEL),
        ),
    ]
