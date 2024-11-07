from pathlib import Path
from django.conf import settings
from django.shortcuts import render
import markdown2
import re
import markdown

def render_markdown_file(file_path):
    """Lire un fichier markdown et remplacer les chemins d'images pour utiliser Django static."""
    static_dir = Path(settings.STATICFILES_DIRS[0])
    markdown_file = static_dir / file_path
    
    if not markdown_file.exists() or not markdown_file.is_file():
        raise FileNotFoundError(f"Le fichier {file_path} n'existe pas.")

    with markdown_file.open('r', encoding='utf-8') as file:
        content = file.read()

    # Remplacer les chemins des images par des chemins Django static
    content = re.sub(
        r'src="data/([A-Za-z0-9_\-\.]+)"',
        r'src="/static/enigmes/markdown/data/\1"',
        content
    )

    # Idem mais pour les chemins des liens
    content = re.sub(
        r'href="data/([A-Za-z0-9_\-\.]+)"',
        r'href="/static/enigmes/markdown/data/\1"',
        content
    )

    # Convertir le markdown en HTML
    html_content = markdown.markdown(content, extensions=['fenced_code', 'md_in_html', 'tables'])

    # Entourer chaque table d'une div avec la classe "table-wrapper"
    html_content = re.sub(
        r'(<table.*?>.*?</table>)', 
        r'<div class="table-wrapper">\1</div>',
        html_content,
        flags=re.DOTALL
    )

    return html_content

