# Generated by Django 2.2.3 on 2019-08-13 19:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_auto_20190813_1932'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loomstock',
            name='bag_type_id',
            field=models.IntegerField(),
        ),
    ]
