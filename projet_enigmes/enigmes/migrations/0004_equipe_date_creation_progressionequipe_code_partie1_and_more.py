# Generated by Django 5.1.1 on 2024-10-21 20:40

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('enigmes', '0003_equipe_code_equipe'),
    ]

    operations = [
        migrations.AddField(
            model_name='equipe',
            name='date_creation',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='progressionequipe',
            name='code_partie1',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='progressionequipe',
            name='code_partie2',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='progressionequipe',
            name='date_reponse_partie1',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='progressionequipe',
            name='date_reponse_partie2',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
