from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('inscription/', views.inscription_enseignant, name='inscription_enseignant'),
    path('confirmer-email/<str:token>/', views.confirmer_email, name='confirmer_email'),
    path('connexion/', views.connexion_enseignant, name='connexion_enseignant'),
    path('deconnexion/', views.deconnexion_enseignant, name='deconnexion_enseignant'),
    
    path('reinitialisation-mot-de-passe/', views.reinitialisation_mot_de_passe, name='reinitialisation_mot_de_passe'),
    path('reinitialisation-mot-de-passe-envoye/', 
         auth_views.PasswordResetDoneView.as_view(template_name="comptes/reinitialisation_mot_de_passe_envoye.html"), name="reinitialisation_mot_de_passe_envoye"),
    path('reinitialisation-mot-de-passe-confirme/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='comptes/reinitialisation_mot_de_passe_confirme.html',
             success_url=reverse_lazy('reinitialisation_mot_de_passe_termine')
          ),
         name='reinitialisation_mot_de_passe_confirme'),
    path('reinitialisation-mot-de-passe-termine/',
         auth_views.PasswordResetCompleteView.as_view(template_name='comptes/reinitialisation_mot_de_passe_terminee.html'),
         name='reinitialisation_mot_de_passe_termine'),
]