# Generated by Django 3.1.6 on 2022-09-09 21:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_auto_20220908_2140'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transactions',
            name='datetime_transfer',
            field=models.DateField(auto_now_add=True),
        ),
    ]
