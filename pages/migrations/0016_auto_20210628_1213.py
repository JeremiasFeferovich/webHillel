# Generated by Django 3.1.7 on 2021-06-28 15:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0015_auto_20210628_1128'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='titulo')),
                ('updated', models.DateTimeField(auto_now_add=True, verbose_name='modificado')),
                ('created', models.DateTimeField(auto_now=True, verbose_name='creado')),
            ],
            options={
                'verbose_name': 'categoria',
                'verbose_name_plural': 'categorias',
                'ordering': ['-created'],
            },
        ),
        migrations.AddField(
            model_name='page',
            name='categories',
            field=models.ManyToManyField(related_name='get_pages', to='pages.Category', verbose_name='categorias'),
        ),
    ]
