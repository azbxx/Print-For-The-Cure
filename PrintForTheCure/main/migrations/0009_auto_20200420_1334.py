# Generated by Django 3.0.3 on 2020-04-20 20:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_auto_20200420_1332'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='requestmodel',
            name='primary_key',
        ),
        migrations.AlterField(
            model_name='requestmodel',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
