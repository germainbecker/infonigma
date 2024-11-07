from django.db import models
from comptes.models import Enseignant

import string
import random

# class Enigme(models.Model):
#     titre = models.CharField(max_length=200)
#     partie1_pdf = models.FileField(upload_to='enigmes/pdfs/')
#     partie2_markdown = models.TextField()
#     code_partie1 = models.CharField(max_length=50)
#     code_partie2 = models.CharField(max_length=50)


class Enigme(models.Model):
    # ENIGME_CHOICES = [
    #     ('01', 'Énigme 1'),
    #     ('02', 'Énigme 2'),
    #     ('03', 'Énigme 3'),
    #     ('04', 'Énigme 4'),
    #     ('05', 'Énigme 5'),
    #     ('06', 'Énigme 6'),
    # ]

    # numero = models.CharField(max_length=2, choices=ENIGME_CHOICES, primary_key=True)
    titre = models.CharField(max_length=200)
    a_un_complement_pdf = models.BooleanField(default=False)
    titre_complement = models.CharField(max_length=200,blank=True, null=True)
    code_partie1 = models.CharField(max_length=50)
    code_partie2 = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.pk} - {self.titre}"

    @property
    def partie1_pdf_path(self):
        return f'enigmes/pdfs/enigme_{self.pk}.pdf'

    @property
    def chemin_pdf_complementaire(self):
        if self.a_un_complement_pdf:
            return f'enigmes/pdfs/enigme_{self.pk}_complementaire.pdf'
        return None
    
    @property
    def partie2_markdown_path(self):
        return f'enigmes/markdown/enigme_{self.pk}_partie2.md'


    # @property
    # def code_partie1(self):
    #     codes = {
    #         '01': 'CODE1_E1',
    #         '02': 'CODE1_E2',
    #         '03': 'CODE1_E3',
    #         '04': 'CODE1_E4',
    #         '05': 'CODE1_E5',
    #         '06': 'CODE1_E6',
    #     }
    #     return codes.get(self.numero)

    # @property
    # def code_partie2(self):
    #     codes = {
    #         '01': 'CODE2_E1',
    #         '02': 'CODE2_E2',
    #         '03': 'CODE2_E3',
    #         '04': 'CODE2_E4',
    #         '05': 'CODE2_E5',
    #         '06': 'CODE2_E6',
    #     }
    #     return codes.get(self.numero)

class Classe(models.Model):
    nom = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True, blank=True)
    enseignant = models.ForeignKey(Enseignant, on_delete=models.CASCADE)
    enigmes = models.ManyToManyField(Enigme)
    est_active = models.BooleanField(default=True, help_text="Détermine si les équipes peuvent accéder aux énigmes")

    def __str__(self):
        return self.nom
    
    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generer_code_unique()
        super().save(*args, **kwargs)

    def generer_code_unique(self):
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        while Classe.objects.filter(code=code).exists():
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        return code

class Equipe(models.Model):
    nom = models.CharField(max_length=10, unique=True)
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE)
    code_equipe = models.CharField(max_length=10, unique=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nom} - {self.classe.nom}"

    def save(self, *args, **kwargs):
        # Générer un code équipe unique avant de sauvegarder l'équipe
        if not self.code_equipe:
            self.code_equipe = self.generer_code_unique()
        # Vérifier si la classe est active avant de créer une équipe
        if not self.classe.est_active:
            raise ValueError("Impossible de créer une équipe car le code n'est pas actif.")
        super().save(*args, **kwargs)

    def generer_code_unique(self):
        """Générer un code unique de 10 caractères"""
        characters = string.ascii_letters + string.digits
        while True:
            # Générer un code aléatoire de 10 caractères
            code = ''.join(random.choices(characters, k=10))
            # Vérifier que le code est unique
            if not Equipe.objects.filter(code_equipe=code).exists():
                return code


class ProgressionEquipe(models.Model):
    equipe = models.ForeignKey(Equipe, on_delete=models.CASCADE)
    enigme = models.ForeignKey(Enigme, on_delete=models.CASCADE)
    
    # Champs pour la partie 1
    partie1_resolue = models.BooleanField(default=False)
    code_partie1 = models.CharField(max_length=50, blank=True, null=True)
    date_reponse_partie1 = models.DateTimeField(null=True, blank=True)

    # Champs pour la partie 2
    partie2_resolue = models.BooleanField(default=False)
    code_partie2 = models.CharField(max_length=200, blank=True, null=True)
    date_reponse_partie2 = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['equipe', 'enigme']

    def __str__(self):
        return f"{self.equipe} - {self.enigme}"