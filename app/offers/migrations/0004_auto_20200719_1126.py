# Generated by Django 2.2.3 on 2020-07-19 15:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('offers', '0003_auto_20200717_1315'),
    ]

    operations = [
        migrations.AlterField(
            model_name='material',
            name='title_en',
            field=models.CharField(help_text='Material title', max_length=120, unique=True),
        ),
        migrations.AlterField(
            model_name='material',
            name='title_es',
            field=models.CharField(help_text='Material title', max_length=120, unique=True),
        ),
        migrations.AlterUniqueTogether(
            name='material',
            unique_together=set(),
        ),
    ]
