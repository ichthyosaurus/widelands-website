# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-04-09 09:24


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notification', '0002_auto_20170417_1857'),
    ]

    operations = [
        migrations.AlterField(
            model_name='noticetype',
            name='display',
            field=models.CharField(help_text='Used as subject when sending emails.', max_length=50, verbose_name='display'),
        ),
    ]
