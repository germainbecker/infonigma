# Generated by Django 5.1.1 on 2024-11-11 13:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('comptes', '0004_alter_enseignant_accepte_cgu'),
    ]

    operations = [
        migrations.AddField(
            model_name='enseignant',
            name='nom',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='enseignant',
            name='prenom',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
