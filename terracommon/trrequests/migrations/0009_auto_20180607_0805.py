# Generated by Django 2.0.5 on 2018-06-07 08:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trrequests', '0008_auto_20180607_0803'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='userrequest',
            options={'permissions': (('can_create_requests', 'Is able to create a new requests'), ('can_read_self_requests', 'Is able to get own requests'), ('can_read_all_requests', 'Is able to get all requests'), ('can_comment_requests', 'Is able to comment an user request'), ('can_internal_comment_requests', 'Is able to add comments not visible by users'), ('can_change_state_requests', 'Is authorized to change the request state'))},
        ),
    ]