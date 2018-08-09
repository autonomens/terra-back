# Generated by Django 2.0.7 on 2018-08-09 09:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trrequests', '0015_auto_20180726_0759'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='userrequest',
            options={'permissions': (('can_create_requests', 'Is able to create a new requests'), ('can_read_self_requests', 'Is able to get own requests'), ('can_read_all_requests', 'Is able to get all requests'), ('can_comment_requests', 'Is able to comment an user request'), ('can_internal_comment_requests', 'Is able to add comments not visible by users'), ('can_change_state_requests', 'Is authorized to change the request state'), ('can_create_documenttemplate', 'Is able to create a new document template'))},
        ),
    ]
