# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-03-06 13:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blog',
            name='text_markup_type',
            field=models.CharField(choices=[(b'', b'--'), (b'html', 'HTML'), (b'plain', 'Plain'), (b'markdown', 'Markdown'), (b'restructuredtext', 'Restructured Text')], default='plain', max_length=30),
        ),
    ]
