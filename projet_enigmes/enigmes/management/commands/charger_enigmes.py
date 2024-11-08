from django.core.management.base import BaseCommand
import json
from enigmes.models import Enigme

class Command(BaseCommand):
    help = """Importe les énigmes depuis un fichier JSON
    À utiliser en exécutant la commande :
    python manage.py charger_enigmes path/to/enigmes.json
    """

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Chemin vers le fichier JSON contenant les énigmes')

    def handle(self, *args, **options):
        json_file = options['json_file']
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f'Le fichier {json_file} n\'existe pas'))
            return
        except json.JSONDecodeError:
            self.stderr.write(self.style.ERROR('Le fichier JSON est mal formaté'))
            return

        enigmes_created = 0
        enigmes_updated = 0

        for enigme_data in data['enigmes']:
            # On utilise get_or_create pour éviter les doublons
            # On utilise le titre comme identifiant unique
            enigme, created = Enigme.objects.get_or_create(
                titre=enigme_data['titre'],
                defaults={
                    'a_un_complement_pdf': enigme_data['a_un_complement_pdf'],
                    'titre_complement': enigme_data['titre_complement'],
                    'code_partie1': enigme_data['code_partie1'],
                    'code_partie2': enigme_data['code_partie2'],
                }
            )

            if created:
                enigmes_created += 1
            else:
                # Mise à jour des champs si l'énigme existe déjà
                enigme.a_un_complement_pdf = enigme_data['a_un_complement_pdf']
                enigme.titre_complement = enigme_data['titre_complement']
                enigme.code_partie1 = enigme_data['code_partie1']
                enigme.code_partie2 = enigme_data['code_partie2']
                enigme.save()
                enigmes_updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Import terminé avec succès: {enigmes_created} énigmes créées, {enigmes_updated} énigmes mises à jour'
            )
        )

# import json
# from django.core.management.base import BaseCommand
# from enigmes.models import Enigme

# class Command(BaseCommand):
#     help = 'Charge les énigmes depuis le fichier de configuration JSON'

#     def handle(self, *args, **options):
#         try:
#             with open('enigmes_config.json', 'r', encoding='utf-8') as config_file:
#                 config = json.load(config_file)

#             for enigme_data in config['enigmes']:
#                 enigme, created = Enigme.objects.update_or_create(
#                     numero=enigme_data['numero'],
#                     defaults={
#                         'titre': enigme_data['titre'],
#                         'a_un_complement_pdf': enigme_data['a_un_complement_pdf']
#                     }
#                 )
#                 if created:
#                     self.stdout.write(self.style.SUCCESS(f'Énigme créée : {enigme.titre}'))
#                 else:
#                     self.stdout.write(self.style.SUCCESS(f'Énigme mise à jour : {enigme.titre}'))

#             self.stdout.write(self.style.SUCCESS('Chargement des énigmes terminé'))
        
#         except UnicodeDecodeError:
#             self.stdout.write(self.style.ERROR('Erreur de décodage UTF-8. Assurez-vous que le fichier JSON est encodé en UTF-8.'))
#         except json.JSONDecodeError:
#             self.stdout.write(self.style.ERROR('Erreur de parsing JSON. Vérifiez le format de votre fichier JSON.'))
#         except Exception as e:
#             self.stdout.write(self.style.ERROR(f'Une erreur est survenue : {str(e)}'))