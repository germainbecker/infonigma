# Generated by Django 5.1.1 on 2024-11-15 22:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('comptes', '0005_enseignant_nom_enseignant_prenom'),
    ]

    operations = [
        migrations.AlterField(
            model_name='enseignant',
            name='prenom',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Prénom'),
        ),
    ]
