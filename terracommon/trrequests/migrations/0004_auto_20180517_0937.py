# Generated by Django 2.0.5 on 2018-05-17 09:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trrequests', '0003_auto_20180517_0922'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userrequest',
            old_name='feature',
            new_name='layer',
        ),
    ]