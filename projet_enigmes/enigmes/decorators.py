from functools import wraps
from django.shortcuts import redirect

def equipe_requise(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        print("Décorateur appelé")  # Ajoutez cette ligne pour vérifier si le décorateur est appelé

        if 'equipe_id' not in request.session:
            print('redirection en cours')
            return redirect('demarrer_concours')
        return view_func(request, *args, **kwargs)
    return _wrapped_view