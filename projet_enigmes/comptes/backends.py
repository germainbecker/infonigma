from django.contrib.auth.backends import ModelBackend

class CustomModelBackend(ModelBackend):
    """
    ATTENTION : Correspond exactement à django.contrib.auth.backends.AllowAllUsersModelBackend donc inutile

    Surcharge de la classe ModelBackend.
    But : pour que tous les utilisateurs (actifs et inactifs) puissent s'authentifier dans la vue LoginView
    faisant appel au formulaire AuthenticationForm. Permet de gérer le message d'erreur pour les utilisateurs inactifs.

    Car la vue LoginView fait appel à ModelBackend pour authentifier un utilisateur
    et que le modèle par défaut ne permet pas de tester l'authentification si l'utilisateur est inactif.
    La modif permet d'autoriser l'authentification même pour un inactif et en cas d'authentification 
    réussie on vérifie ensuite l'attribut is_active pour gérer le message d'erreur. 
    """
    
    def user_can_authenticate(self, user):
        """Renvoie True que l'utilisateur user soit actif ou non.
        Par défaut, la fonction renvoyait False si user.is_active=False."""
        
        return True