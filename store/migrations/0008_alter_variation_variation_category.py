# Generated by Django 4.1 on 2022-09-22 09:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0007_alter_variation_variation_value'),
    ]

    operations = [
        migrations.AlterField(
            model_name='variation',
            name='variation_category',
            field=models.CharField(choices=[('color', 'цвет'), ('size', 'размер')], max_length=100, verbose_name='Категория вариации'),
        ),
    ]
