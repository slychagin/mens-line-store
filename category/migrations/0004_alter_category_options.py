# Generated by Django 4.1 on 2022-09-22 11:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('category', '0003_alter_category_cat_image_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'verbose_name': 'Категория', 'verbose_name_plural': 'Категории'},
        ),
    ]
