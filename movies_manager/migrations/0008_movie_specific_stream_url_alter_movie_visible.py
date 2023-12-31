# Generated by Django 4.2.3 on 2023-08-17 21:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies_manager', '0007_rename_hidden_to_users_movie_visible'),
    ]

    operations = [
        migrations.AddField(
            model_name='movie',
            name='specific_stream_url',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='movie',
            name='visible',
            field=models.BooleanField(default=False),
        ),
    ]
