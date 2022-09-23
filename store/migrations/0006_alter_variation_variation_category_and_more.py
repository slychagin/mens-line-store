# Generated by Django 4.1 on 2022-09-22 06:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0005_alter_productgallery_options_alter_product_category_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='variation',
            name='variation_category',
            field=models.CharField(choices=[('цвет', 'цвет'), ('размер', 'размер')], max_length=100, verbose_name='Категория вариации'),
        ),
        migrations.AlterField(
            model_name='variation',
            name='variation_value',
            field=models.CharField(choices=[('цвет', 'цвет'), ('размер', 'размер')], max_length=100, verbose_name='Значение вариации'),
        ),
    ]