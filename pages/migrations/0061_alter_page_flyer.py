# Generated by Django 3.2.6 on 2021-08-14 01:16

from django.db import migrations, models
import pages.models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0060_alter_page_flyer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='page',
            name='flyer',
            field=models.ImageField(blank=True, null=True, upload_to=pages.models.custom_upload_to),
        ),
    ]
