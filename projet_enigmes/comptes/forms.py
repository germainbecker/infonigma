from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from .models import Enseignant




LISTE_ADRESSES_CORRECTES = [
    'ac-aix-marseille.fr',
    'ac-amiens.fr',
    'ac-besancon.fr',
    'ac-bordeaux.fr',
    'ac-clermont.fr',
    'ac-corse.fr',
    'ac-creteil.fr',
    'ac-dijon.fr',
    'ac-grenoble.fr',
    'ac-guadeloupe.fr',
    'ac-guyane.fr',
    'ac-reunion.fr',
    'ac-lille.fr',
    'ac-limoges.fr',
    'ac-lyon.fr',
    'ac-martinique.fr',
    'ac-mayotte.fr',
    'ac-montpellier.fr',
    'ac-nancy-metz.fr',
    'ac-nantes.fr',
    'ac-nice.fr',
    'ac-normandie.fr',
    'ac-noumea.fr',
    'ac-orleans-tours.fr',
    'ac-paris.fr',
    'ac-poitiers.fr',
    'ac-polynesie.pf',
    'ac-reims.fr',
    'ac-rennes.fr',
    'ac-spm.fr',
    'ac-strasbourg.fr',
    'ac-toulouse.fr',
    'ac-versailles.fr',
    'ac-wf.wf',
    'aefe.fr',
    'educagri.fr',
]

LISTE_ADRESSES_EXCEPTIONS = settings.EMAIL_EXCEPTIONS

def adresse_email_valide(adresse: str) -> bool:
    """Renvoie True si et seulement si adresse est une adresse e-mail valide"""
    academie = adresse.split('@')[1]
    return academie in LISTE_ADRESSES_CORRECTES or adresse in LISTE_ADRESSES_EXCEPTIONS


class FormulaireInscriptionEnseignant(UserCreationForm):
    accepte_cgu = forms.BooleanField(
        required=True,
        error_messages={
            'required': "Vous devez accepter les conditions générales d'utilisation pour vous inscrire."
        },
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = Enseignant
        fields = ('nom', 'prenom', 'email', 'password1', 'password2', 'accepte_cgu')
        help_texts = {
            'email': 'Utilisez une adresse email académique valide.'
        }
        labels = {
            'nom': "Nom (facultatif)",
            'prenom': "Prénom (facultatif)"
        }

    def clean_email(self):
        email = self.cleaned_data['email']
        if not adresse_email_valide(email):
            raise forms.ValidationError("Veuillez utiliser une adresse email académique.")
        return email

class FormulaireConnexionEnseignant(AuthenticationForm):
    """Formulaire de connexion personnalisé pour modifier les messages d'erreur.

    Ce formulaire permet de personnaliser les messages d'erreur, notamment 
    pour les comptes inactifs. Si aucune personnalisation n'est nécessaire, 
    il est possible d'utiliser directement AuthenticationForm dans views.py.
    """
    error_messages = {
        'invalid_login': _(
            "Veuillez entrer une adresse email et un mot de passe corrects."
        ),
        'inactive': _(
            "Ce compte est inactif. Pour l'activer, vous devez cliquer sur le lien " 
            "qui vous a été envoyé par email."
        ),
    }

class EmailForm(forms.Form):
    sujet = forms.CharField(label='Sujet', max_length=100)
    message = forms.CharField(label='Message', widget=forms.Textarea)

