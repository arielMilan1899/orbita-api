# Generated by Django 2.2.3 on 2020-07-26 13:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('offers', '0004_auto_20200719_1126'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='poster_public_id',
            field=models.CharField(blank=True, help_text='Image public_id', max_length=150, null=True),
        ),
        migrations.AddField(
            model_name='category',
            name='poster_url',
            field=models.CharField(blank=True, help_text='Image url', max_length=150, null=True),
        ),
    ]