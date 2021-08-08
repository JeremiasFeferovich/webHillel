# Generated by Django 3.1.7 on 2021-08-04 14:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0048_auto_20210804_1428'),
    ]

    operations = [
        migrations.AlterField(
            model_name='page',
            name='horaDesde',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=2, null=True, verbose_name='Hora desde'),
        ),
        migrations.AlterField(
            model_name='page',
            name='horaHasta',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=2, null=True, verbose_name='Hora hasta'),
        ),
    ]
