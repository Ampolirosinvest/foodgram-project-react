# Generated by Django 4.0.6 on 2022-07-26 09:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ingredient',
            old_name='units_measurement',
            new_name='measurement_unit',
        ),
    ]
