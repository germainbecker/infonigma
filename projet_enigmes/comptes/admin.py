from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Enseignant

class EnseignantAdmin(UserAdmin):
    # Les champs à afficher dans la liste des utilisateurs dans l'administration
    list_display = ('email', 'nom', 'prenom', 'is_active', 'accepte_cgu', 'is_staff', 'is_superuser')
    
    # Les champs sur lesquels on peut cliquer pour accéder à l'objet dans la liste
    list_display_links = ('email',)
    
    # Les champs que l'on peut filtrer dans la barre latérale
    list_filter = ('is_active', 'is_staff', 'is_superuser')

    # Les champs disponibles dans le formulaire de création et modification
    fieldsets = (
        (None, {'fields': ('nom', 'prenom', 'email', 'password')}),
        ('Permissions', {'fields': ('is_active', 'accepte_cgu', 'is_staff', 'is_superuser')}),
        ('Tokens', {'fields': ('email_confirmation_token',)}),
    )

    # Spécifie les champs utilisés lors de la création d'un nouvel utilisateur
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('nom', 'prenom', 'email', 'password1', 'password2'),
        }),
    )

    # Les champs utilisés pour rechercher un utilisateur
    search_fields = ('nom', 'prenom', 'email',)

    # Le champ utilisé pour identifier un utilisateur dans l'administration
    ordering = ('email',)

    # Champs non modifiables en mode lecture seule
    readonly_fields = ('email_confirmation_token',)

# Enregistrez le modèle et son administration personnalisée
admin.site.register(Enseignant, EnseignantAdmin)
