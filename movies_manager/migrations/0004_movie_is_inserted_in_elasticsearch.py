# Generated by Django 4.2.3 on 2023-07-21 08:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies_manager', '0003_movie_genre'),
    ]

    operations = [
        migrations.AddField(
            model_name='movie',
            name='is_inserted_in_elasticsearch',
            field=models.BooleanField(default=False),
        ),
    ]
