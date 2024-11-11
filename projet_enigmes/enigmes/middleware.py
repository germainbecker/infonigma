from django.http import Http404

class BlockMarkdownAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Bloquer l'accès direct aux fichiers markdown via l'URL
        if '/markdown/' in request.path or request.path.endswith('.md'):
            raise Http404("Fichier non trouvé")
        return self.get_response(request)