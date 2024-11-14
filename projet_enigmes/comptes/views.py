from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.urls import reverse
from .forms import FormulaireInscriptionEnseignant, FormulaireConnexionEnseignant
from .models import Enseignant





def inscription_enseignant(request):
    if request.method == 'POST':
        formulaire = FormulaireInscriptionEnseignant(request.POST)
        if formulaire.is_valid():
            enseignant = formulaire.save(commit=False)
            enseignant.is_active = False
            enseignant.save()
            
            # Générer et envoyer le token de confirmation
            enseignant.generate_email_confirmation_token()
            sujet = "Confirmation de votre compte Enseignant"
            lien_confirmation = request.build_absolute_uri(
                reverse('confirmer_email', args=[enseignant.email_confirmation_token])
            )
            message_html = render_to_string('comptes/email_confirmation.html', {
                'enseignant': enseignant,
                'lien_confirmation': lien_confirmation,
            })
            message_texte = strip_tags(message_html)
            
            send_mail(sujet, message_texte, settings.DEFAULT_FROM_EMAIL, [enseignant.email], 
                      html_message=message_html)
            
            messages.success(request, """Un email de confirmation vient d'être envoyé à l'adresse email renseignée. Veuillez cliquez sur le lien présent dans cet email afin de valider votre compte Enseignant. Une fois le compte validé vous pourrez vous connecter.""")
            return redirect('connexion_enseignant')
    else:
        formulaire = FormulaireInscriptionEnseignant()
    return render(request, 'comptes/inscription.html', {'formulaire': formulaire})

def confirmer_email(request, token):
    try:
        enseignant = Enseignant.objects.get(email_confirmation_token=token)
        enseignant.is_active = True
        enseignant.email_confirmation_token = ''
        enseignant.save()
        messages.success(request, "Votre compte est désormais actif. Vous pouvez vous connecter.")
        # login(request, enseignant)
        return redirect('connexion_enseignant')
    except Enseignant.DoesNotExist:
        messages.warning(request, "Le lien n'est pas valide ou a déjà été utilisé. Si vous aviez déjà cliqué sur ce lien, votre compte est probablement déjà actif.")
        return redirect('connexion_enseignant')


def connexion_enseignant(request):
    if request.method == 'POST':
        formulaire = FormulaireConnexionEnseignant(request, data=request.POST)
        if formulaire.is_valid():
            enseignant = formulaire.get_user()
            login(request, enseignant)
            return redirect('liste_classes')
    else:
        formulaire = FormulaireConnexionEnseignant()
    return render(request, 'comptes/connexion.html', {'form': formulaire})



def deconnexion_enseignant(request):
    logout(request)
    return redirect('demarrer_concours')

def reinitialisation_mot_de_passe(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            User = get_user_model()
            users = User.objects.filter(email=email)
            if users.exists():
                for user in users:
                    subject = "Réinitialisation de votre mot de passe"
                    email_template_name = "comptes/email_reinitialisation_mot_de_passe.html"
                    c = {
                        "email": user.email,
                        'domain': request.META['HTTP_HOST'],
                        'site_name': 'infonigma',
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        'token': default_token_generator.make_token(user),
                        'protocol': 'https' if request.is_secure() else 'http',
                    }
                    email = render_to_string(email_template_name, c)
                    send_mail(subject, email, 'noreply@votredomaine.com', [user.email], fail_silently=False)
                
            messages.info(request, "Cliquez sur le lien qui vous a été envoyé par email pour réinitialiser votre mot de passe.")

            return redirect('connexion_enseignant')
        
    else:
        form = PasswordResetForm()
    return render(request, 'comptes/reinitialisation_mot_de_passe.html', {'form': form})



