# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-17 08:19
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DirectoryMetaObject',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now=True)),
                ('modified_at', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=4096)),
                ('parent', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='core.DirectoryMetaObject')),
                ('storage', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Storage')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='FileMetaObject',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now=True)),
                ('modified_at', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=4096)),
                ('content_type', models.CharField(max_length=100)),
                ('size', models.BigIntegerField()),
                ('parent', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='core.DirectoryMetaObject')),
                ('storage', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Storage')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='metaobject',
            name='storage',
        ),
        migrations.DeleteModel(
            name='MetaObject',
        ),
    ]