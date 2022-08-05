# Generated by Django 4.0.6 on 2022-08-05 12:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0004_alter_tag_color'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='color',
            field=models.CharField(choices=[('#1965b5', 'Синий'), ('#0dbf60', 'Зелёный'), ('#e6766a', 'Красный'), ('#fca503', 'Белый')], max_length=7, unique=True, verbose_name='Цвет тега'),
        ),
    ]