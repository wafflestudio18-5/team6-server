# Generated by Django 3.1 on 2021-01-08 05:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('village', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='article',
            name='deleted_at',
        ),
        migrations.RemoveField(
            model_name='comment',
            name='deleted_at',
        ),
    ]
