# Generated by Django 2.2.3 on 2019-08-13 19:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='loomstock',
            old_name='bag_type',
            new_name='bag_type_id',
        ),
    ]
