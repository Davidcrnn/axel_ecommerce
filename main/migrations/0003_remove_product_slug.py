# Generated by Django 2.2 on 2020-01-09 16:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_product_slug'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='slug',
        ),
    ]