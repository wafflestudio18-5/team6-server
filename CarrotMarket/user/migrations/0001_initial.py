# Generated by Django 3.1 on 2021-01-08 15:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('area', models.CharField(blank=True, max_length=20)),
                ('nickname', models.CharField(blank=True, db_index=True, max_length=10)),
                ('phone', models.CharField(blank=True, db_index=True, max_length=13)),
                ('user_type', models.CharField(blank=True, default='django', max_length=10)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='userprofile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
