# Generated by Django 2.0.8 on 2018-09-11 08:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='terrauser',
            options={'permissions': (('can_manage_users', 'Is able create, delete, update users'),)},
        ),
    ]
