from django.core.management.base import BaseCommand
from comptes.models import Enseignant

class Command(BaseCommand):
    help = "Normalise les adresses email des enseignants en les convertissant en minuscules."

    def handle(self, *args, **kwargs):
        enseignants = Enseignant.objects.all()
        for enseignant in enseignants:
            if enseignant.email != enseignant.email.lower():
                self.stdout.write(f"Normalisation : {enseignant.email} → {enseignant.email.lower()}")
                enseignant.email = enseignant.email.lower()
                enseignant.save()
        self.stdout.write(self.style.SUCCESS("Toutes les adresses email ont été normalisées."))
