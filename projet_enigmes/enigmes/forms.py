from django import forms
from .models import Classe, Enigme, Equipe

class FormulaireCreationClasse(forms.ModelForm):
    enigmes = forms.ModelMultipleChoiceField(
        queryset=Enigme.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        initial=Enigme.objects.all(),
        required=False
    )

    class Meta:
        model = Classe
        fields = ['nom', 'enigmes']

    def __init__(self, *args, **kwargs):
        enseignant = kwargs.pop('enseignant', None)
        super().__init__(*args, **kwargs)
        if enseignant:
            self.instance.enseignant = enseignant

    def clean_enigmes(self):
        enigmes = self.cleaned_data.get('enigmes')
        if not enigmes:
            raise forms.ValidationError("Vous devez sélectionner au moins une énigme.")
        return enigmes

class FormulaireCodeClasse(forms.Form):
    code_classe = forms.CharField(
        label="Code fourni par l'enseignant", 
        max_length=10,
        widget=forms.TextInput(attrs={'style': 'text-align:center'})
    )


class FormulaireEquipe(forms.Form):
    nom = forms.CharField(
        label="Nom de l'équipe", 
        max_length=100, 
        required=False,
        widget=forms.TextInput(attrs={'placeholder': "Saisisez un nom d'équipe. Celui-ci ne devrait pas comporter de données personnelles."})
    )
    code_equipe = forms.CharField(
        label="Code équipe (si vous reprenez le concours)",
        max_length=10,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': "Saisisez le code d'équipe unique attribué"})
        )
    
    def __init__(self, *args, classe=None, **kwargs):
        # on passe la classe au formulaire pour la validation (méthode clean)
        self.classe = classe
        super().__init__(*args, **kwargs)
    
    def clean(self):
        cleaned_data = super().clean()
        nom = cleaned_data.get('nom')
        code_equipe = cleaned_data.get('code_equipe')
        
        if not nom and not code_equipe:
            raise forms.ValidationError("Vous devez soit créer une équipe (en saisissant un nom) soit saisir un code d'équipe pour reprendre.")
        
        # Vérifier si le nom d'équipe existe déjà dans la classe
        if nom and self.classe:
            if Equipe.objects.filter(nom=nom, classe=self.classe).exists():
                raise forms.ValidationError(
                    "Une équipe avec ce nom existe déjà dans cette classe. Veuillez en choisir un autre."
                )
            
        return cleaned_data
    
    # def clean(self):
    #     cleaned_data = super().clean()
    #     nom = cleaned_data.get('nom')
    #     code_equipe = cleaned_data.get('code_equipe')
        
    #     if not nom and not code_equipe:
    #         raise forms.ValidationError("Vous devez soit créer une équipe (en saisissant un nom) soit saisir un code d'équipe pour reprendre.")
        
    #     # Vérifier si le nom d'équipe existe déjà
    #     if nom:
    #         if Equipe.objects.filter(nom=nom).exists():
    #             raise forms.ValidationError("Une équipe avec ce nom existe déjà. Veuillez en choisir un autre.")
            
    #     return cleaned_data
    
class FormulaireRepriseEquipe(forms.Form):
    code_equipe = forms.CharField(
        label="Code équipe (si vous reprenez le concours)",
        max_length=10,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': "Saisisez le code d'équipe unique attribué"})
        )
    
    def clean(self):
        cleaned_data = super().clean()
        code_equipe = cleaned_data.get('code_equipe')
                
        # Vérifier si le code d'équipe existe déjà
        if code_equipe:
            if not Equipe.objects.filter(code_equipe=code_equipe).exists():
                raise forms.ValidationError("Ce code ne correspond à aucune équipe pour ce concours.")
        else:
            raise forms.ValidationError("Vous devez saisir un code d'équipe pour reprendre.")
        return cleaned_data

class FormulairePartie1(forms.Form):
    code_partie1 = forms.CharField(
        label="Code de la première partie",
        max_length=50,
        widget=forms.TextInput(attrs={
            'placeholder': 'Saisir le code de la première partie',
            'style': 'text-align:center',
        }))
    


class FormulairePartie2(forms.Form):
    code_partie2 = forms.CharField(
        label="Code de la seconde partie",
        max_length=50,
        help_text="Attention, toute réponse est définitive !",
        widget=forms.TextInput(attrs={
            'placeholder': 'Saisir le code de la seconde partie',
            'style': 'text-align:center',
        })
    )

    class Meta:
        helptexts = {
            'code_partie2': 'Attention'
        }
