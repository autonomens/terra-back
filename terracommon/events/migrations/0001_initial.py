# Generated by Django 2.0.5 on 2018-06-21 14:06

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EventHandler',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(max_length=255)),
                ('handler', models.CharField(max_length=255)),
                ('settings', django.contrib.postgres.fields.jsonb.JSONField(default={})),
            ],
        ),
    ]
