# Generated by Django 3.1.4 on 2020-12-03 07:51

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DownloadStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.TextField()),
                ('table_name', models.TextField()),
                ('task_completed', models.BooleanField(default=False)),
                ('filename', models.TextField()),
            ],
        ),
    ]
