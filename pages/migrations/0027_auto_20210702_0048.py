# Generated by Django 3.1.7 on 2021-07-02 00:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0026_auto_20210702_0021'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='page',
            options={'ordering': ['dia__order'], 'verbose_name': 'página', 'verbose_name_plural': 'páginas'},
        ),
    ]
