# Generated by Django 4.2.3 on 2023-08-18 14:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies_manager', '0009_alter_movie_specific_stream_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='movie',
            name='specific_stream_url',
            field=models.CharField(blank=True, default='', max_length=1000),
        ),
    ]
