# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-23 07:04
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    replaces = [('agrf_feed', '0001_initial'), ('agrf_feed', '0002_auto_20170409_0037'), ('agrf_feed', '0003_auto_20170522_0652'), ('agrf_feed', '0004_auto_20170523_0328'), ('agrf_feed', '0005_auto_20170523_0353')]

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='FileDescriptor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('path', models.CharField(db_index=True, max_length=244)),
                ('exported', models.SmallIntegerField(choices=[(1, 'New'), (2, 'Pending Upload'), (3, 'Uploaded'), (4, 'Upload Failed')], default=1)),
            ],
            options={
                'ordering': ['path'],
            },
        ),
    ]
