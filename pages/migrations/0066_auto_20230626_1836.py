# Generated by Django 3.1.7 on 2023-06-26 18:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0065_page_fecha'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='page',
            options={'ordering': ['horaDesde', '-title'], 'verbose_name': 'actividad', 'verbose_name_plural': 'actividades'},
        ),
        migrations.RemoveField(
            model_name='page',
            name='dia',
        ),
        migrations.DeleteModel(
            name='Day',
        ),
    ]
