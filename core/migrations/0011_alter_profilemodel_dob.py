# Generated by Django 4.1 on 2022-11-04 19:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0010_alter_profilemodel_dob"),
    ]

    operations = [
        migrations.AlterField(
            model_name="profilemodel",
            name="dob",
            field=models.DateTimeField(),
        ),
    ]