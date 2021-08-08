# Generated by Django 3.1.7 on 2021-08-06 19:28

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('pages', '0053_auto_20210806_1914'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cuestionario',
            name='orden',
        ),
        migrations.RemoveField(
            model_name='cuestionario',
            name='respuesta1',
        ),
        migrations.RemoveField(
            model_name='cuestionario',
            name='respuesta2',
        ),
        migrations.RemoveField(
            model_name='cuestionario',
            name='respuesta3',
        ),
        migrations.RemoveField(
            model_name='cuestionario',
            name='respuesta4',
        ),
        migrations.RemoveField(
            model_name='cuestionario',
            name='respuesta5',
        ),
        migrations.RemoveField(
            model_name='cuestionario',
            name='user',
        ),
        migrations.CreateModel(
            name='CuestionarioRespuesta',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pregunta1', models.CharField(blank=True, default='', max_length=200, null=True, verbose_name='Pregunta1')),
                ('respuesta1', models.CharField(blank=True, default='', max_length=200, null=True, verbose_name='Respuesta1')),
                ('pregunta2', models.CharField(blank=True, default='', max_length=200, null=True, verbose_name='Pregunta2')),
                ('respuesta2', models.CharField(blank=True, default='', max_length=200, null=True, verbose_name='Respuesta2')),
                ('pregunta3', models.CharField(blank=True, default='', max_length=200, null=True, verbose_name='Pregunta3')),
                ('respuesta3', models.CharField(blank=True, default='', max_length=200, null=True, verbose_name='Respuesta3')),
                ('pregunta4', models.CharField(blank=True, default='', max_length=200, null=True, verbose_name='Pregunta4')),
                ('respuesta4', models.CharField(blank=True, default='', max_length=200, null=True, verbose_name='Respuesta4')),
                ('pregunta5', models.CharField(blank=True, default='', max_length=200, null=True, verbose_name='Pregunta5')),
                ('respuesta5', models.CharField(blank=True, default='', max_length=200, null=True, verbose_name='Respuesta5')),
                ('created', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Fecha de creación')),
                ('updated', models.DateTimeField(auto_now=True, null=True, verbose_name='Fecha de edición')),
                ('page', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pagina_cuestionario_respuesta', to='pages.page', verbose_name='Actividad')),
                ('user', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Cuestionario Respuesta',
                'verbose_name_plural': 'Cuestionario Respuestas',
                'ordering': ['updated'],
            },
        ),
    ]
