from django.contrib import admin
from .models import Classe, Enigme, Equipe, ProgressionEquipe

@admin.register(Enigme)
class EnigmeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'titre', 'a_un_complement_pdf')
    list_filter = ('a_un_complement_pdf',)
    search_fields = ('titre',)

@admin.register(Classe)
class ClasseAdmin(admin.ModelAdmin):
    list_display = ('nom', 'code', 'enseignant')
    fields = ('nom', 'enseignant', 'enigmes')
    list_filter = ('enseignant',)
    search_fields = ('nom', 'code')
    filter_horizontal = ('enigmes',)
    readonly_fields = ('code',)

    def get_fields(self, request, obj=None):
        """
        Cette méthode personnalise les champs affichés en fonction de l'action :
        - Lors de la consultation d'une instance (obj != None), on affiche tous les champs, incluant 'code'.
        - Lors de la création ou modification (obj == None), on cache 'code'.
        """
        if obj:  # Si on consulte une instance existante
            return ('nom', 'code', 'enseignant', 'enigmes')
        return self.fields  # Lors de la création/modification, on utilise `fields`

    # def save_model(self, request, obj, form, change):
    #     if not obj.code:
    #         obj.code = obj.generer_code_unique()
    #     super().save_model(request, obj, form, change)


@admin.register(Equipe)
class EquipeAdmin(admin.ModelAdmin):
    list_display = ('nom', 'classe', 'code_equipe')
    list_filter = ('classe',)
    search_fields = ('nom', 'code_equipe')

@admin.register(ProgressionEquipe)
class ProgressionEquipeAdmin(admin.ModelAdmin):
    list_display = (
        'equipe', 
        'enigme', 
        'code_partie1', 
        'partie1_resolue', 
        'code_partie2', 
        'partie2_resolue'
    )
    # list_filter = ('classe',)
    search_fields = ('equipe', 'enigme')