# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-30 20:43
from __future__ import unicode_literals

import django.core.files.storage
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('registered_dataverse', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='GISDataFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dv_user_id', models.IntegerField(db_index=True)),
                ('dv_username', models.CharField(max_length=255)),
                ('dv_user_email', models.EmailField(max_length=254)),
                ('return_to_dataverse_url', models.URLField(blank=True, max_length=255)),
                ('datafile_download_url', models.URLField(max_length=255)),
                ('dataverse_installation_name', models.CharField(default=b'Harvard Dataverse', help_text=b'url to Harvard Dataverse, Odum Institute Dataverse, etc', max_length=255)),
                ('dataverse_id', models.IntegerField(default=-1, help_text=b'id in database')),
                ('dataverse_name', models.CharField(db_index=True, max_length=255)),
                ('dataverse_description', models.TextField(blank=True)),
                ('dataset_id', models.IntegerField(default=-1, help_text=b'id in database')),
                ('dataset_version_id', models.IntegerField(default=-1, help_text=b'id in database')),
                ('dataset_semantic_version', models.CharField(blank=True, help_text=b'example: "DRAFT",  "1.2", "2.3", etc', max_length=25)),
                ('dataset_name', models.CharField(blank=True, max_length=255)),
                ('dataset_citation', models.CharField(max_length=255)),
                ('dataset_description', models.TextField(blank=True)),
                ('dataset_is_public', models.BooleanField(default=False)),
                ('datafile_id', models.IntegerField(db_index=True, default=-1, help_text=b'id in database')),
                ('datafile_label', models.CharField(help_text=b'original file name', max_length=255)),
                ('datafile_expected_md5_checksum', models.CharField(max_length=100)),
                ('datafile_filesize', models.IntegerField(help_text=b'in bytes')),
                ('datafile_content_type', models.CharField(max_length=255)),
                ('datafile_create_datetime', models.DateTimeField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('dv_session_token', models.CharField(blank=True, max_length=255)),
                ('dv_file', models.FileField(blank=True, null=True, storage=django.core.files.storage.FileSystemStorage(location=b'/Users/rmp553/Documents/iqss-git/geoconnect/test_setup/dv_datafile_directory'), upload_to=b'dv_files/%Y/%m/%d')),
                ('gis_scratch_work_directory', models.CharField(blank=True, help_text=b'scratch directory for files', max_length=255)),
                ('md5', models.CharField(blank=True, db_index=True, help_text=b'auto-filled on save', max_length=40)),
                ('registered_dataverse', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='registered_dataverse.RegisteredDataverse')),
            ],
            options={
                'ordering': ('-modified',),
            },
        ),
    ]
