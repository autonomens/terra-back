# Generated by Django 2.0.9 on 2018-10-24 16:09

import django.db.models.deletion
from django.db import migrations, models

import terracommon.datastore.models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('datastore', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='RelatedDocument',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=255)),
                ('object_id', models.PositiveIntegerField()),
                ('document', models.FileField(upload_to=terracommon.datastore.models.related_document_path)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='contenttypes.ContentType')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='relateddocument',
            unique_together={('key', 'content_type', 'object_id')},
        ),
    ]