# Generated by Django 2.0.2 on 2018-02-16 16:49

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('terra', '0003_auto_20180216_1333'),
    ]

    operations = [
        migrations.CreateModel(
            name='LayerRelation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('schema', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict)),
                ('destination', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='relations_as_destination', to='terra.Layer')),
                ('origin', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='relations_as_origin', to='terra.Layer')),
            ],
        ),
    ]
