# Generated by Django 2.0.5 on 2018-06-05 12:53

from django.db import migrations, models


class Migration(migrations.Migration):

    replaces = [('trrequests', '0006_auto_20180604_1351'), ('trrequests', '0007_auto_20180604_1353'), ('trrequests', '0008_auto_20180604_1406')]

    dependencies = [
        ('trrequests', '0005_auto_20180604_0940'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='userrequest',
            options={'permissions': (('can_administrate_requests', 'Has administrator permissions on requests'), ('can_create_requests', 'Is able to create a new requests'), ('can_read_self_requests', 'Is able to get own requests'), ('can_read_all_requests', 'Is able to get all requests'), ('can_comment_requests', 'Is able to comment an user request'), ('can_internal_comment_requests', 'Is able to add comments not visible by users'), ('can_change_state_requests', 'Is authorized to change the request state'), ('can_approve_requests', 'Is able to set the approved state'))},
        ),
        migrations.AlterField(
            model_name='userrequest',
            name='state',
            field=models.IntegerField(default=0),
        ),
    ]