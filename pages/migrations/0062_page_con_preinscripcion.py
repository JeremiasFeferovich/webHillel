# Generated by Django 3.1.7 on 2023-06-13 11:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0061_alter_page_flyer'),
    ]

    operations = [
        migrations.AddField(
            model_name='page',
            name='con_preinscripcion',
            field=models.BooleanField(default=False, verbose_name='Tiene preinscripción?'),
        ),
    ]
