# Generated by Django 4.2.7 on 2023-12-03 08:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0008_quiz_category1_quiz_category2_quiz_category3_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quiz',
            name='category1',
            field=models.CharField(blank=True, default='', max_length=30, null=True, verbose_name='Category 1'),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='category2',
            field=models.CharField(blank=True, default='', max_length=30, null=True, verbose_name='Category 2'),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='category3',
            field=models.CharField(blank=True, default='', max_length=30, null=True, verbose_name='Category 3'),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='category4',
            field=models.CharField(blank=True, default='', max_length=30, null=True, verbose_name='Category 4'),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='description',
            field=models.TextField(blank=True, default='', null=True, verbose_name='Quiz description'),
        ),
    ]
