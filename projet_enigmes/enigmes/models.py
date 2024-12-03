from django.db import models
from django.conf import settings

from comptes.models import Enseignant

from pathlib import Path
import os
import string
import random



class Enigme(models.Model):
    titre = models.CharField(max_length=200)
    a_un_complement_pdf = models.BooleanField(default=False)
    titre_complement = models.CharField(max_length=200,blank=True, null=True)
    code_partie1 = models.CharField(max_length=50)
    code_partie2 = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.pk} - {self.titre}"

    @property
    def partie1_pdf_path(self):
        repertoire = Path(settings.PROTECTED_FILES_ROOT)
        return repertoire / 'pdfs' / f'enigme_{self.pk}.pdf'
        
    
    @property
    def nom_fichier_partie1_pdf(self):
        return f'enigme_{self.pk}.pdf'
        
    @property
    def chemin_pdf_complementaire(self):
        if self.a_un_complement_pdf:
            repertoire = Path(settings.PROTECTED_FILES_ROOT)
            return repertoire / 'pdfs' / f'enigme_{self.pk}_complementaire.pdf'
        return None
    
    @property
    def nom_fichier_pdf_complementaire(self):
        if self.a_un_complement_pdf:
            return f'enigme_{self.pk}_complementaire.pdf'
        return None
    
    @property
    def partie2_markdown_path(self):
        repertoire = Path(settings.PROTECTED_FILES_ROOT)
        return repertoire / 'markdown' / f'enigme_{self.pk}_partie2.md'


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
        # certains caractères qui peuvent être confondus sont exclus
        caracteres = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
        code = ''.join(random.choices(caracteres, k=8))
        while Classe.objects.filter(code=code).exists():
            code = ''.join(random.choices(caracteres, k=8))
        return code

class Equipe(models.Model):
    nom = models.CharField(max_length=100)
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE)
    code_equipe = models.CharField(max_length=10, unique=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['nom', 'classe']  # Contrainte d'unicité sur le couple (nom, classe)

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
        # caracteres = string.ascii_letters + string.digits
        # on retire les caractères qui peuvent être confondus
        caracteres = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789"
        while True:
            # Générer un code aléatoire de 10 caractères
            code = ''.join(random.choices(caracteres, k=10))
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