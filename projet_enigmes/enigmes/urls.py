from django.urls import path
from . import views
from .views import (
    ClasseCreationView,
    ClasseDetailView,
    ClasseUpdateView,
    ClasseDeleteView,
    TelechargerEnigmesZipView,
)

urlpatterns = [
    path('', views.demarrer_concours, name='demarrer_concours'),
    path('mes-classes/', views.liste_classes, name='liste_classes'),

    path('creer-classe/', ClasseCreationView.as_view(), name='creer_classe'),
    path('classe/<str:code_classe>/reponses/', views.voir_reponses_classe, name='reponses_classe'),
    path('classe/<str:code_classe>/', ClasseDetailView.as_view(), name='detail_classe'),
    path('classe/<str:code_classe>/modifier/', ClasseUpdateView.as_view(), name='modifier_classe'),
    path('classe/<str:code_classe>/supprimer/', ClasseDeleteView.as_view(), name='supprimer_classe'),
    path('classe/<str:code_classe>/activer/', views.activer_classe, name='activer_classe'),
    path('classe/<str:code_classe>/desactiver/', views.desactiver_classe, name='desactiver_classe'),
    path('mes-classes/classe/<str:code_classe>/activer/', views.activer_classe_dans_mes_classes, name='activer_classe_dans_mes_classes'),
    path('mes-classes/classe/<str:code_classe>/desactiver/', views.desactiver_classe_dans_mes_classes, name='desactiver_classe_dans_mes_classes'),

    path('pdf-protege/<int:enigme_id>/<str:nom_fichier>', views.pdf_protege, name='pdf_protege'),
    
    path('enigmes/', views.liste_enigmes, name='liste_enigmes'),
    path('enigme/apercu/<str:enigme_id>/', views.apercu_enigme, name='apercu_enigme'),
    path('enigmes/telecharger-ressources/', TelechargerEnigmesZipView.as_view(), name='telecharger_ressources'),
    path('enigmes/telecharger-reponses/', views.telecharger_reponses_enigmes, name='telecharger_reponses_enigmes'),

    path('concours/<str:code_classe>/equipe/', views.creer_ou_reprendre_equipe, name='creer_ou_reprendre_equipe'),
    path('concours/reprise/', views.reprendre_equipe, name='reprendre_equipe'),
    path('concours/quitter/', views.quitter_concours, name='quitter_concours'),
    path('concours/enigmes/', views.liste_enigmes_classe, name='liste_enigmes_classe'),
    path('concours/enigme/<int:enigme_id>/', views.resoudre_enigme, name='resoudre_enigme'),

    path('a-propos/', views.a_propos, name='a_propos'),
    path('cgu/', views.cgu, name='cgu'),
    path('politique-confidentialite/', views.politique_confidentialite, name='politique_confidentialite'),
    
]