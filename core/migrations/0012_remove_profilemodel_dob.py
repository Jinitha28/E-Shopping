# Generated by Django 4.1 on 2022-11-05 21:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0011_alter_profilemodel_dob"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="profilemodel",
            name="dob",
        ),
    ]
