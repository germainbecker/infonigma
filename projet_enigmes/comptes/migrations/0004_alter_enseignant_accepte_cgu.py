# Generated by Django 5.1.1 on 2024-11-09 13:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('comptes', '0003_enseignant_accepte_cgu'),
    ]

    operations = [
        migrations.AlterField(
            model_name='enseignant',
            name='accepte_cgu',
            field=models.BooleanField(default=False, verbose_name='Accepte les CGU'),
        ),
    ]
