# Generated by Django 2.0.8 on 2018-08-17 08:01

import uuid

import django.contrib.gis.db.models.fields
import django.contrib.postgres.fields.jsonb
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import terracommon.terra.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Feature',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('geom', django.contrib.gis.db.models.fields.GeometryField()),
                ('identifier', models.CharField(default=uuid.uuid4, max_length=255)),
                ('properties', django.contrib.postgres.fields.jsonb.JSONField()),
                ('from_date', terracommon.terra.fields.DateFieldYearLess(default='01-01', help_text='Layer validity period start')),
                ('to_date', terracommon.terra.fields.DateFieldYearLess(default='12-31', help_text='Layer validity period end')),
            ],
        ),
        migrations.CreateModel(
            name='FeatureRelation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('properties', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict)),
                ('destination', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='relations_as_destination', to='terra.Feature')),
                ('origin', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='relations_as_origin', to='terra.Feature')),
            ],
        ),
        migrations.CreateModel(
            name='Layer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
                ('group', models.CharField(default='__nogroup__', max_length=255)),
                ('schema', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict)),
            ],
        ),
        migrations.CreateModel(
            name='LayerRelation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('schema', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict)),
                ('destination', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='relations_as_destination', to='terra.Layer')),
                ('origin', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='relations_as_origin', to='terra.Layer')),
            ],
        ),
        migrations.AddField(
            model_name='feature',
            name='layer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='features', to='terra.Layer'),
        ),
    ]
