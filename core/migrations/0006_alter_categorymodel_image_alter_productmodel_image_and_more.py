# Generated by Django 4.1.2 on 2022-10-29 08:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0005_profile_delete_profilemodel"),
    ]

    operations = [
        migrations.AlterField(
            model_name="categorymodel",
            name="image",
            field=models.ImageField(
                default="default/category.png", upload_to="category/image/"
            ),
        ),
        migrations.AlterField(
            model_name="productmodel",
            name="image",
            field=models.ImageField(
                default="default/product.png", upload_to="product/image/"
            ),
        ),
        migrations.AlterField(
            model_name="profile",
            name="account_type",
            field=models.CharField(
                choices=[
                    ("Customer", "customer"),
                    ("Merchant", "merchant"),
                    ("Administrator", "admin"),
                ],
                default="customer",
                max_length=16,
            ),
        ),
    ]
