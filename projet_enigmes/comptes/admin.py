from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from django.shortcuts import render, redirect
from django.core.mail import send_mail, EmailMessage
from django.http import HttpResponseRedirect
from django.conf import settings

from .models import Enseignant
from .forms import EmailForm


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

    actions = ['envoyer_email']

    def envoyer_email(self, request, queryset):
        if 'apply' in request.POST:
            form = EmailForm(request.POST)
            if form.is_valid():
                sujet = form.cleaned_data['sujet']
                message = form.cleaned_data['message']
                from_email = settings.DEFAULT_FROM_EMAIL
                
                try:
                    # Crée un seul email avec tous les destinataires en BCC
                    email = EmailMessage(
                        subject=sujet,
                        body=message,
                        from_email=from_email,
                        bcc=[user.email for user in queryset],  # Tous les destinataires en BCC
                    )
                    
                    # Envoie l'email
                    email.send(fail_silently=False)
                    
                    # Message de confirmation
                    self.message_user(
                        request,
                        f"Email envoyé avec succès à {queryset.count()} utilisateur(s)",
                        messages.SUCCESS
                    )
                        
                    return HttpResponseRedirect(request.get_full_path())
                
                except Exception as e:
                    self.message_user(
                        request,
                        f"Erreur lors de l'envoi de l'email : {str(e)}",
                        messages.ERROR
                    )
        
        else:
            form = EmailForm()

        return render(
            request,
            'admin/envoyer_email.html',
            {
                'enseignants': queryset,
                'form': form,
                'title': "Envoyer un email",
                'opts': self.model._meta,
            }
        )

    envoyer_email.short_description = "Envoyer un email aux utilisateurs sélectionnés"



# Enregistrez le modèle et son administration personnalisée
admin.site.register(Enseignant, EnseignantAdmin)
