from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.contrib import messages
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import DetailView, DeleteView

from django.urls import reverse_lazy, reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string
from django.db.models import Prefetch

from .models import Enigme, Classe, Equipe, ProgressionEquipe
from .forms import FormulaireCreationClasse, FormulairePartie1, FormulairePartie2, FormulaireCodeClasse, FormulaireEquipe, FormulaireRepriseEquipe
from .decorators import equipe_requise

from .utils import render_markdown_file

import unicodedata
import random
import string


# def accueil(request):
#     return render(request, 'enigmes/accueil.html')


def a_propos(request):
    return render(request, 'enigmes/a_propos.html')

def cgu(request):
    return render(request, 'enigmes/cgu.html')

def politique_confidentialite(request):
    return render(request, 'enigmes/politique_confidentialite.html')

##### CLASSES #####

class ClasseCreationView(LoginRequiredMixin, CreateView):
    model = Classe
    form_class = FormulaireCreationClasse
    template_name = 'enigmes/classe_creation.html'
    success_url = reverse_lazy('liste_classes')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['enseignant'] = self.request.user
        return kwargs

class ClasseDetailView(LoginRequiredMixin, DetailView):
    model = Classe
    template_name = 'enigmes/detail_classe.html'
    context_object_name = 'classe'
    
    def get_object(self, queryset=None):
        # Récupérer l'objet et vérifier que l'enseignant est bien le propriétaire
        obj = get_object_or_404(Classe, code=self.kwargs['code_classe'])
        if obj.enseignant != self.request.user:
            raise HttpResponseForbidden("Vous n'avez pas accès à cette classe.")
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Récupérer les énigmes
        context['enigmes'] = self.object.enigmes.all()
        # Récupérer les équipes triées par date de création
        context['equipes'] = self.object.equipe_set.all().order_by('-date_creation')
        # Ajouter un flag pour savoir si la classe est modifiable
        context['peut_modifier'] = not self.object.equipe_set.exists()
        return context

class ClasseUpdateView(LoginRequiredMixin, UpdateView):
    model = Classe
    form_class = FormulaireCreationClasse
    template_name = 'enigmes/modifier_classe.html'
    # success_url = reverse_lazy('liste_classes')

    
    def get_success_url(self):
        return reverse_lazy('detail_classe', kwargs={'code_classe': self.object.code})
    
    def get_object(self, queryset=None):
        # Récupérer l'objet et vérifier que l'enseignant est bien le propriétaire
        obj = get_object_or_404(Classe, code=self.kwargs['code_classe'])
        if obj.enseignant != self.request.user:
            raise HttpResponseForbidden("Vous n'avez pas le droit de modifier cette classe.")
        return obj
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['enseignant'] = self.request.user
        return kwargs
        
    def dispatch(self, request, *args, **kwargs):
        # Vérifier si des équipes existent avant d'autoriser la modification
        classe = self.get_object()
        if classe.equipe_set.exists():
            messages.error(request, "Impossible de modifier cette classe car des équipes y sont déjà associées.")
            return HttpResponseForbidden("Modification impossible : des équipes existent déjà pour cette classe.")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, "La classe a été modifiée avec succès.")
        return super().form_valid(form)


class ClasseDeleteView(LoginRequiredMixin, DeleteView):
    model = Classe
    template_name = 'enigmes/supprimer_classe.html'
    success_url = reverse_lazy('liste_classes')
    
    def get_object(self, queryset=None):
        # Récupérer l'objet et vérifier que l'enseignant est bien le propriétaire
        obj = get_object_or_404(Classe, code=self.kwargs['code_classe'])
        if obj.enseignant != self.request.user:
            raise HttpResponseForbidden("Vous n'avez pas le droit de supprimer cette classe.")
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Ajouter des informations supplémentaires au contexte
        context['enigmes'] = self.object.enigmes.all()
        context['equipes'] = self.object.equipe_set.all()
        context['nb_equipes'] = self.object.equipe_set.count()
        return context
    
    def form_valid(self, form):
        # Stocker les informations avant la suppression
        nom_classe = self.object.nom
        
        # Appeler la méthode parente qui effectue la suppression
        response = super().form_valid(form)
        
        # Ajouter le message de succès
        messages.success(
            self.request,
            f'La classe "{nom_classe}" a été supprimée avec succès, '
            f'ainsi que toutes les équipes associées.'
        )
        
        return response
    
    # def delete(self, request, *args, **kwargs):
    #     # Récupérer l'objet avant suppression
    #     self.object = self.get_object()
        
    #     # Nom de la classe avant suppression
    #     nom_classe = self.object.nom
    #     # Nombre d'équipes avant suppression
    #     nb_equipes = self.object.equipe_set.count()
        
    #     # Supprimer toutes les équipes associées (fait à la suppression de la classe)
    #     # self.object.equipe_set.all().delete()
        
    #     # Supprimer la classe (et toutes les équipes associées grace à on_delete=models.CASCADE)
    #     success_url = self.get_success_url()
    #     self.object.delete()
        
    #     # Ajouter un message de confirmation avec le nombre d'équipes supprimées
    #     messages.success(request, 
    #         f"La classe {nom_classe} a été supprimée avec succès. "
    #         f"{nb_equipes} équipe(s) ont été supprimées en même temps."
    #     )
    #     print('ici')
        
    #     return HttpResponseRedirect(success_url)


@login_required
def liste_classes(request):
    classes = Classe.objects.filter(enseignant=request.user)
    peut_modifier_classe = {classe.id : not classe.equipe_set.exists() for classe in classes}
    return render(request, 'enigmes/mes_classes.html', {'classes': classes, 'peut_modifier_classe': peut_modifier_classe})

@login_required
@require_POST
def activer_classe_dans_mes_classes(request, code_classe):
    classe = Classe.objects.get(code=code_classe, enseignant=request.user)
    classe.est_active = True
    classe.save()
    peut_modifier_classe = not classe.equipe_set.exists()
    
    # Rendre le template partiel de la classe
    context = {'classe': classe, 'peut_modifier_classe': peut_modifier_classe}
    html = render_to_string('enigmes/partials/classe_partial.html', context)
    return HttpResponse(html)

@login_required
@require_POST
def desactiver_classe_dans_mes_classes(request, code_classe):
    classe = Classe.objects.get(code=code_classe, enseignant=request.user)
    classe.est_active = False
    classe.save()
    peut_modifier_classe = not classe.equipe_set.exists()
    
    # Rendre le template partiel de la classe
    context = {'classe': classe, 'peut_modifier_classe': peut_modifier_classe}
    html = render_to_string('enigmes/partials/classe_partial.html', context)
    return HttpResponse(html)

@login_required
@require_POST
def activer_classe(request, code_classe):
    classe = Classe.objects.get(code=code_classe, enseignant=request.user)
    classe.est_active = True
    classe.save()
    peut_modifier_classe = not classe.equipe_set.exists()
    
    # Rendre le template partiel de la classe
    context = {'classe': classe, 'peut_modifier_classe': peut_modifier_classe}
    html = render_to_string('enigmes/partials/detail_classe_partial.html', context)
    return HttpResponse(html)

@login_required
@require_POST
def desactiver_classe(request, code_classe):
    classe = Classe.objects.get(code=code_classe, enseignant=request.user)
    classe.est_active = False
    classe.save()
    peut_modifier_classe = not classe.equipe_set.exists()
    
    # Rendre le template partiel de la classe
    context = {'classe': classe, 'peut_modifier_classe': peut_modifier_classe}
    html = render_to_string('enigmes/partials/detail_classe_partial.html', context)
    return HttpResponse(html)


##### CONCOURS #####

def demarrer_concours(request):
    if request.method == "POST":
        form = FormulaireCodeClasse(request.POST)
        if form.is_valid():
            # on supprime l'équipe de la session pour pouvoir en créer une nouvelle
            if 'equipe_id' in request.session:
                del request.session['equipe_id']
            
            code_classe = form.cleaned_data['code_classe']
            try:
                classe = Classe.objects.get(code=code_classe)
                if not classe.est_active:
                    form.add_error('code_classe', "Le concours est inactif.")
                else:
                    return redirect('creer_ou_reprendre_equipe', classe_id=classe.id)
            except Classe.DoesNotExist:
                form.add_error('code_classe', "Code incorrect.")
    else:
        form = FormulaireCodeClasse()
    
    return render(request, 'enigmes/demarrer_concours.html', {'form': form})


def creer_ou_reprendre_equipe(request, classe_id):
    if 'equipe_id' in request.session:
        return redirect('liste_enigmes_classe')
    
    classe = Classe.objects.get(id=classe_id)

    
    
    if request.method == "POST":
        form = FormulaireEquipe(request.POST)
        if form.is_valid():
            code_equipe = form.cleaned_data['code_equipe']
            nom = form.cleaned_data['nom']
            
            if code_equipe:
                # Reprendre une équipe existante                
                try:
                    equipe = Equipe.objects.get(code_equipe=code_equipe, classe=classe)
                    # Stocker l'équipe dans la session
                    request.session['equipe_id'] = equipe.id
                    
                    # si la classe est inactive, on redirige l'équipe vers la liste des énigmes avec un message
                    if not classe.est_active:
                        messages.warning(request, "Attention, le concours n'est plus actif. Vous ne pouvez plus consulter ou répondre aux énigmes.")
                    return redirect('liste_enigmes_classe')
                
                except Equipe.DoesNotExist:
                    form.add_error('code_equipe', "Aucune équipe trouvée avec ce code.")
            elif nom:
                # si la classe est inactive, on ne peut pas créer de nouvelle équipe
                if not classe.est_active:
                    messages.warning(request, "Le concours n'est plus actif. Vous ne pouvez pas créer d'équipe.")
                    return redirect('demarrer_concours')
                # Créer une nouvelle équipe
                equipe = Equipe.objects.create(nom=nom, classe=classe)
                code_equipe = equipe.code_equipe
                # Stocker l'équipe dans la session
                request.session['equipe_id'] = equipe.id
                return render(request, 'enigmes/equipe_creee.html', {'equipe': equipe, 'code_equipe': code_equipe})
    
    else:
        form = FormulaireEquipe()

    return render(request, 'enigmes/creer_ou_reprendre_equipe.html', {'form': form, 'classe': classe})


def reprendre_equipe(request):
    if 'equipe_id' in request.session:
        print(request.session.get('equipe_id'))
        equipe = Equipe.objects.get(id=request.session['equipe_id'])
        if not equipe.classe.est_active:
            messages.warning(request, "Le concours n'est plus actif. Vous ne pouvez plus consulter ou répondre aux énigmes.")
        return redirect('liste_enigmes_classe')
    
    if request.method == "POST":
        form = FormulaireRepriseEquipe(request.POST)
        if form.is_valid():
            code_equipe = form.cleaned_data['code_equipe']
            try:
                equipe = Equipe.objects.get(code_equipe=code_equipe)
                # Stocker l'équipe dans la session
                request.session['equipe_id'] = equipe.id
                if not equipe.classe.est_active:
                    messages.warning(request, "Le concours n'est plus actif. Vous ne pouvez plus consulter ou répondre aux énigmes.")
                return redirect('liste_enigmes_classe')
            except Equipe.DoesNotExist:
                form.add_error('code_equipe', "Aucune équipe trouvée avec ce code.")
            # code_equipe = form.cleaned_data['code_equipe']
            
            # if code_equipe:
            #     # Reprendre une équipe existante
            #     try:
            #         equipe = Equipe.objects.get(code_equipe=code_equipe, classe=classe)
            #         # Stocker l'équipe dans la session
            #         request.session['equipe_id'] = equipe.id
            #         return redirect('liste_enigmes_classe')
            #     except Equipe.DoesNotExist:
            #         form.add_error('code_equipe', "Aucune équipe trouvée avec ce code.")    
    else:
        form = FormulaireRepriseEquipe()

    return render(request, 'enigmes/reprendre_equipe.html', {'form': form})


def quitter_concours(request):
    if 'equipe_id' in request.session:
        del request.session['equipe_id']
    return redirect('demarrer_concours')

@equipe_requise
def liste_enigmes_classe(request):
    """Liste des énigmes d'une classe."""
    # Récupérer l'ID de l'équipe depuis la session
    equipe_id = request.session.get('equipe_id')

    if not equipe_id:
        # Si l'équipe n'est pas trouvée dans la session, rediriger vers l'accueil
        return redirect('demarrer_concours')
    
    equipe = get_object_or_404(Equipe, id=equipe_id)
    classe_est_active = equipe.classe.est_active
    enigmes = equipe.classe.enigmes.all()
    
    
    # Récupérer les progrès de l'équipe
    progression = ProgressionEquipe.objects.filter(equipe=equipe)
    # enigmes_resolues = [p.enigme for p in progression if p.partie2_resolue]

    # Créer un dictionnaire pour stocker les informations de progression pour chaque énigme
    progression_dict = {
        p.enigme.id: {
            'partie1_resolue': p.partie1_resolue,
            'code_partie1': p.code_partie1,
            'partie2_tentee': p.code_partie2 is not None,
            'code_partie2': p.code_partie2
        }
        for p in progression
    }
        
    return render(request, 'enigmes/liste_enigmes_classe.html', {
        'classe_est_active': classe_est_active,
        'enigmes': enigmes,
        'equipe': equipe,
        # 'enigmes_resolues': enigmes_resolues,
        'progression_dict': progression_dict
    })
    
    # return render(request, 'enigmes/liste_enigmes_classe.html', {'enigmes': enigmes, 'equipe': equipe, 'enigmes_resolues': enigmes_resolues})


def normaliser_chaine(chaine):
    # # Supprimer les espaces
    # chaine = chaine.replace(" ", "")
    # Supprimer les espaces en début et en fin
    chaine = chaine.strip()
    # Convertir en minuscules
    chaine = chaine.lower()
    # Supprimer les accents
    chaine = ''.join(
        c for c in unicodedata.normalize('NFD', chaine)
        if unicodedata.category(c) != 'Mn'
    )
    return chaine

def comparer_chaines(reponse, proposition):
    # Normaliser les deux chaînes
    reponse_normalisee = normaliser_chaine(reponse)
    proposition_normalisee = normaliser_chaine(proposition)
    # Comparer les chaînes normalisées
    return reponse_normalisee == proposition_normalisee


@equipe_requise
def resoudre_enigme(request, enigme_id):
    equipe_id = request.session.get('equipe_id')
    
    if not equipe_id:
        # Rediriger vers l'accueil si l'équipe n'est pas dans la session
        return redirect('demarrer_concours')
    

    equipe = get_object_or_404(Equipe, id=equipe_id)
    
    # Si la classe n'est pas active, on redirige avec HX-Redirect pour les requêtes HTMX
    if not equipe.classe.est_active:
        messages.warning(request, "Attention, le concours n'est plus actif. Vous ne pouvez plus consulter ou répondre aux énigmes.")
        if request.headers.get('HX-Request'):
            response = HttpResponse()
            response['HX-Redirect'] = reverse('liste_enigmes_classe')
            return response
        return redirect('liste_enigmes_classe')
    
    enigme = get_object_or_404(Enigme, id=enigme_id)
    enigmes = equipe.classe.enigmes.all()
    numero_enigme_en_cours = list(enigmes).index(enigme) + 1
    progression, created = ProgressionEquipe.objects.get_or_create(equipe=equipe, enigme=enigme)
    # Vérifier si une réponse a déjà été soumise pour la partie 2
    if progression.partie2_resolue or (progression.date_reponse_partie2 is not None):
        enigme_partie2_markdown = render_markdown_file(enigme.partie2_markdown_path)
        return render(request, 'enigmes/resoudre_enigme.html', {
            'enigme': enigme,
            'numero_enigme_en_cours': numero_enigme_en_cours,
            'equipe': equipe,
            'enigmes': enigmes,
            'partie1_resolue': True,
            'partie_resolue': True,
            'enigme_partie2_markdown' : enigme_partie2_markdown,
        })

    

    # Gestion de la soumission des formulaires
    if request.method == "POST":
        if 'code_partie1' in request.POST:
            form1 = FormulairePartie1(request.POST)
            if form1.is_valid():
                code_partie1 = form1.cleaned_data['code_partie1']
                # Vérifier si le code de la partie 1 est correct
                if comparer_chaines(enigme.code_partie1, code_partie1):
                    # Enregistrer la réponse correcte et la date
                    progression.partie1_resolue = True
                    progression.code_partie1 = code_partie1
                    progression.date_reponse_partie1 = timezone.now()
                    progression.save()

                    # # Afficher le formulaire de la partie 2
                    # form2 = FormulairePartie2()
                    # enigme_partie2_markdown = render_markdown_file(enigme.partie2_markdown_path)
                    # return render(request, 'enigmes/resoudre_enigme.html', {
                    #     'enigme': enigme, 
                    #     'form2': form2, 
                    #     'equipe': equipe, 
                    #     'partie1_resolue': True,
                    #     'enigme_partie2_markdown' : enigme_partie2_markdown,
                    # }, status=200)

                    # Retourner le fragment HTML pour la partie 2
                    form2 = FormulairePartie2()
                    enigme_partie2_markdown = render_markdown_file(enigme.partie2_markdown_path)
                    html = render_to_string('enigmes/partials/partie2.html', {
                        'form2': form2,
                        'enigme': enigme,
                        'enigme_partie2_markdown': enigme_partie2_markdown
                    })
                    # Renvoyer la réponse avec l'attribut HX-Reswap
                    response = HttpResponse(html)
                    response['HX-Reswap'] = 'outerHTML'
                    response['HX-Retarget'] = '#zone-partie1'
                    return response

                else:
                    # # Afficher un message d'erreur si le code est incorrect
                    # return render(request, 'enigmes/resoudre_enigme.html', {
                    #     'enigme': enigme, 
                    #     'form1': form1, 
                    #     'equipe': equipe, 
                    #     'error': "Le code est incorrect."
                    # })

                    progression.code_partie1 = code_partie1
                    progression.date_reponse_partie1 = timezone.now()
                    progression.save()
                    # Retourner un fragment d'erreur si le code est incorrect
                    message_erreur = render_to_string('enigmes/partials/error.html', {
                        'error': "Le code est incorrect."
                    })
                    return HttpResponse(message_erreur)
        
        elif 'code_partie2' in request.POST:
            form2 = FormulairePartie2(request.POST)
            if form2.is_valid():
                code_partie2 = form2.cleaned_data['code_partie2']
                # Enregistrer la réponse à la partie 2 et la date
                progression.code_partie2 = code_partie2
                progression.date_reponse_partie2 = timezone.now()  # Enregistrer la date de réponse

                # Vérifier si le code de la partie 2 est correct
                if comparer_chaines(enigme.code_partie2, code_partie2):
                    progression.partie2_resolue = True
                progression.save()
                messages.info(request, "Votre réponse a bien été transmise. Vous pouvez poursuivre avec une nouvelle énigme.")
                return redirect('liste_enigmes_classe')

    else:  # requête GET
        # Si la partie 1 est déjà résolue, afficher le formulaire pour la partie 2
        if progression.partie1_resolue:
            form2 = FormulairePartie2()
            enigme_partie2_markdown = render_markdown_file(enigme.partie2_markdown_path)
            return render(request, 'enigmes/resoudre_enigme.html', {
                'enigme': enigme,
                'numero_enigme_en_cours': numero_enigme_en_cours,
                'enigmes': enigmes,
                'form2': form2, 
                'equipe': equipe, 
                'partie1_resolue': True,
                'enigme_partie2_markdown' : enigme_partie2_markdown,
            })
        else:

            form1 = FormulairePartie1()

            return render(request, 'enigmes/resoudre_enigme.html', {
                'enigme': enigme,
                'numero_enigme_en_cours': numero_enigme_en_cours,
                'enigmes': enigmes,
                'form1': form1, 
                'equipe': equipe
            })


##### RÉSULTATS #####

def formate_duree(seconds):
    """Formate une durée en secondes en format HH:MM:SS"""
    if seconds is None:
        return "-"
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    
    if hours > 0:
        return f"{int(hours)} h {int(minutes):02d} m {int(seconds):02d} s"
    elif minutes > 0:
        return f"{int(minutes)} m {int(seconds):02d} s"
    else:
        return f"{int(seconds)} s"

@login_required
def voir_reponses_classe(request, code_classe):
    # Récupère la classe avec l'enseignant préchargé
    classe = get_object_or_404(
        Classe.objects.select_related('enseignant'),
        code=code_classe
    )
    
    # Vérifie que l'enseignant connecté est bien celui de la classe
    if request.user != classe.enseignant:
        return HttpResponseForbidden("Vous n'avez pas accès à cette classe.")
    
    # Récupère toutes les énigmes de la classe avec leurs progressions préchargées
    enigmes = (classe.enigmes.all()
        .prefetch_related(
            Prefetch(
                'progressionequipe_set',
                queryset=ProgressionEquipe.objects.select_related('equipe')
                .filter(equipe__classe=classe)
                .order_by('equipe__nom')
            )
        )
        .order_by('pk')  # Ou un autre ordre si vous préférez
    )
    
    # Prépare les données pour chaque énigme
    resultats_par_enigme = []
    
    for enigme in enigmes:
        # Liste toutes les équipes et leurs réponses pour cette énigme
        reponses_equipes = []
        for progression in enigme.progressionequipe_set.all():
            # Calcul des durées pour chaque partie
            duree_partie1 = None
            if progression.date_reponse_partie1:
                duree_partie1 = (progression.date_reponse_partie1 - progression.equipe.date_creation).total_seconds()
            
            duree_partie2 = None
            if progression.date_reponse_partie2:
                duree_partie2 = (progression.date_reponse_partie2 - progression.equipe.date_creation).total_seconds()
            
            reponses_equipes.append({
                'equipe': progression.equipe,
                'partie1': {
                    'code': progression.code_partie1,
                    'est_correcte': progression.partie1_resolue,
                    'duree': formate_duree(duree_partie1) if duree_partie1 else None,
                    'date': progression.date_reponse_partie1
                },
                'partie2': {
                    'code': progression.code_partie2,
                    'est_correcte': progression.partie2_resolue,
                    'duree': formate_duree(duree_partie2) if duree_partie2 else None,
                    'date': progression.date_reponse_partie2
                }
            })
            
        resultats_par_enigme.append({
            'enigme': enigme,
            'reponses_equipes': reponses_equipes,
            # 'stats': {
            #     'nb_partie1_resolue': sum(1 for r in reponses_equipes if r['partie1']['est_correcte']),
            #     'nb_partie2_resolue': sum(1 for r in reponses_equipes if r['partie2']['est_correcte']),
            # }
        })

    
    # Récupère toutes les énigmes de la classe
    enigmes = classe.enigmes.all().order_by('pk')

    # Récupère toutes les équipes de la classe avec leurs progressions préchargées
    equipes = (classe.equipe_set.all()
        .prefetch_related(
            Prefetch(
                'progressionequipe_set',
                queryset=ProgressionEquipe.objects.select_related('enigme')
                .order_by('enigme__pk')
            )
        )
        .order_by('nom')
    )

    # Préparation des résultats par équipe
    resultats_par_equipe = []
    for equipe in equipes:
        reponses_enigmes = []
        score_total = 0
        duree_totale = 0
        nb_reponses = 0
        nb_partie2_resolue = 0
        derniere_reponse = None
        temps_derniere_reponse = None
        # Créer un dictionnaire des progressions existantes indexé par l'id de l'énigme
        progressions_equipe = {
            prog.enigme.id: prog
            for prog in equipe.progressionequipe_set.all()
        }

        # Parcourir toutes les énigmes de la classe
        for enigme in enigmes:
            progression = progressions_equipe.get(enigme.id)

            # Si une progression existe pour cette énigme
            if progression:
                points = 0
                if progression.partie1_resolue:
                    points += 1
                    duree_partie1 = (progression.date_reponse_partie1 - progression.equipe.date_creation).total_seconds()
                    duree_totale += duree_partie1
                    nb_reponses += 1
                    if derniere_reponse is None or progression.date_reponse_partie1 > derniere_reponse:
                        derniere_reponse = progression.date_reponse_partie1
                if progression.partie2_resolue:
                    points += 3
                    duree_partie2 = (progression.date_reponse_partie2 - progression.equipe.date_creation).total_seconds()
                    duree_totale += duree_partie2
                    nb_reponses += 1
                    nb_partie2_resolue += 1
                    if derniere_reponse is None or progression.date_reponse_partie2 > derniere_reponse:
                        derniere_reponse = progression.date_reponse_partie2
                score_total += points

                reponses_enigmes.append({
                    'enigme': enigme,
                    'points': points,
                    'partie1': {
                        'code': progression.code_partie1,
                        'est_correcte': progression.partie1_resolue,
                        'date': progression.date_reponse_partie1
                    },
                    'partie2': {
                        'code': progression.code_partie2,
                        'est_correcte': progression.partie2_resolue,
                        'date': progression.date_reponse_partie2
                    }
                })
                if derniere_reponse:
                    temps_derniere_reponse = (derniere_reponse - progression.equipe.date_creation)
            # Si aucune progression n'existe pour cette énigme
            else:
                reponses_enigmes.append({
                    'enigme': enigme,
                    'points': 0,
                    'partie1': {
                        'code': None,
                        'est_correcte': False,
                        'date': None
                    },
                    'partie2': {
                        'code': None,
                        'est_correcte': False,
                        'date': None
                    }
                })

        # duree_moyenne = duree_totale / nb_reponses if nb_reponses > 0 else None
        
        
        temps_formate_derniere_reponse = None
        if temps_derniere_reponse:
            temps_formate_derniere_reponse = formate_duree(temps_derniere_reponse.total_seconds())
        resultats_par_equipe.append({
            'equipe': equipe,
            'reponses_enigmes': reponses_enigmes,
            'score_total': score_total,
            'nb_partie2_resolue': nb_partie2_resolue,
            # 'duree_moyenne': formate_duree(duree_moyenne),
            'temps_derniere_reponse': temps_derniere_reponse,
            'temps_formate_derniere_reponse': temps_formate_derniere_reponse
        })

    # Trier les équipes par score total décroissant, puis par nombre de réponses correctes pour la partie 2 décroissant, puis par durée moyenne croissante
    classement = sorted(
        resultats_par_equipe, 
        key=lambda x: (
            -x['score_total'],
            -x['nb_partie2_resolue'],
            x['temps_derniere_reponse'] if x['temps_derniere_reponse'] is not None else float('inf')
        )
    )

    print(classement)

    # Si aucune équipe n'a de points
    if classement == [] or classement[0]['score_total'] == 0:
        classement = None
    
    # # Trier les équipes par score total décroissant
    # resultats_par_equipe.sort(key=lambda x: x['score_total'], reverse=True)

    context = {
        'classe': classe,
        'resultats_par_enigme': resultats_par_enigme,
        'resultats_par_equipe': resultats_par_equipe,
        'classement': classement,
    }
    
    return render(request, 'enigmes/reponses_classe.html', context)

##### ENIGMES #####

@login_required
def liste_enigmes(request):
    enigmes = Enigme.objects.all()
    return render(request, 'enigmes/liste_enigmes.html', {'enigmes': enigmes})

@login_required
def apercu_enigme(request, enigme_id):
    enigme = get_object_or_404(Enigme, pk=enigme_id)
    numero_enigme_en_cours = enigme.id + 1
    enigmes = Enigme.objects.all()
    enigme_partie2_markdown = render_markdown_file(enigme.partie2_markdown_path)
    return render(request, 'enigmes/apercu_enigme.html', {
        'enigme': enigme,
        # 'numero_enigme_en_cours': numero_enigme_en_cours,
        'enigmes': enigmes,
        'enigme_partie2_markdown': enigme_partie2_markdown,
    })




# def detail_enigme(request, enigme_id):
#     enigme = get_object_or_404(Enigme, pk=enigme_id)
#     if request.method == 'POST':
#         formulaire = FormulairePartie1(request.POST)
#         if formulaire.is_valid():
#             code = formulaire.cleaned_data['code']
#             # Vérifier le code et mettre à jour le progrès de l'équipe
#     else:
#         formulaire = FormulairePartie1()
#     enigme_partie2_markdown = render_markdown_file(enigme.partie2_markdown_path)
#     context = {
#         'enigme': enigme,
#         'chemin_enigme_partie1_pdf': enigme.partie1_pdf_path,
#         'enigme_partie2_markdown' : enigme_partie2_markdown,
#         'formulaire': formulaire
#     }
#     return render(request, 'enigmes/detail_enigme.html', context)


