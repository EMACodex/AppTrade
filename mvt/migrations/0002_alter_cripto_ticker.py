# Generated by Django 4.2 on 2025-02-20 22:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mvt', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cripto',
            name='ticker',
            field=models.CharField(max_length=10, unique=True),
        ),
    ]
