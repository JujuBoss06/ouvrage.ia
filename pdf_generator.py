# pdf_generator.py

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.colors import HexColor
from pdfrw import PdfReader, PdfWriter, PageMerge
import textwrap
import os
from utils import replace_newlines_in_text

# Fonction pour découper le texte en lignes qui tiennent dans la largeur spécifiée
def wrap_text(c, text, width):
    # Mesurer la largeur du texte en fonction de la police et de la taille actuelles
    font_size = c._fontsize
    font_name = c._fontname
    
    # Largeur en points pour une lettre "M" (caractère standard de largeur moyenne)
    max_width_per_line = c.stringWidth('M', font_name, font_size)
    
    # Calcule la largeur approximative en nombre de caractères par ligne
    num_chars_per_line = int(width // max_width_per_line)
    
    # Découper le texte en plusieurs lignes avec un maximum de caractères par ligne
    return textwrap.wrap(text, width=num_chars_per_line)

def generate_pdf(template_path, output_path, positions_data, variables):

        # Remplacer les \n par \u000A dans les textes de positions_data
    positions_data = replace_newlines_in_text(positions_data)

    # Lire le template PDF pour obtenir le nombre de pages
    template_pdf = PdfReader(template_path)
    num_pages = len(template_pdf.pages)

    # Créer un PDF temporaire avec le même nombre de pages
    temp_pdf_path = 'temp_overlay.pdf'
    c = canvas.Canvas(temp_pdf_path, pagesize=letter)

    # Obtenir la hauteur de la page
    page_width, page_height = A4

    # Créer un mapping des numéros de pages aux éléments à dessiner
    pages_content = {}  # clé : numéro de page, valeur : liste d'éléments
    for item in positions_data:
        page_num = int(item.get('pages', '0'))
        if page_num not in pages_content:
            pages_content[page_num] = []
        pages_content[page_num].append(item)

    # Générer le contenu pour chaque page
    for page_num in range(num_pages):
        # Vérifier s'il y a des éléments pour cette page
        items = pages_content.get(page_num, [])
        if items:
            for item in items:
                # Extraire les données
                text = item.get('text')
                x = item.get('x')
                y = item.get('y')
                width = item.get('width')  # Chaque placeholder a son propre width
                height = item.get('height')
                alignment = item.get('alignment', 'left')
                color = item.get('color', '#000000')
                size = item.get('size', 12)
                font_name = item.get('fontName', 'Helvetica')
                font_bold = item.get('fontBold', False)

                if font_bold:
                    font_name += '-Bold'

                # Remplacer les variables dans le texte
                if text in variables:
                    text = variables[text]
                else:
                    text = variables.get(text, text)

                # Convertir la couleur hexadécimale en objet couleur
                color = HexColor(color)

                # Définir la police et la taille
                c.setFont(font_name, size)
                c.setFillColor(color)

                # Ajuster le positionnement en fonction de l'origine de ReportLab
                y = page_height - y  # Inverser l'axe vertical

                # Découper le texte pour qu'il tienne dans la largeur spécifiée pour chaque placeholder
                wrapped_text_lines = wrap_text(c, str(text), width)
                line_height = 32   #c._leading  # La hauteur d'une ligne de texte (espace entre les lignes)
                for line in wrapped_text_lines:
                    if alignment == 'center':
                        c.drawCentredString(x + width / 2, y, line)
                    elif alignment == 'right':
                        c.drawRightString(x + width, y, line)
                    else:
                        c.drawString(x, y, line)

                    # Déplacer le `y` vers le bas pour la ligne suivante
                    y -= int(line_height)

            # Ajouter l'organigramme PNG à la page 12
        if page_num == 11:  # Python compte à partir de 0, donc la page 12 est indexée par 11
            image_width = 520  # Largeur de l'image
            image_height = 400  # Hauteur de l'image
             # Calcul des coordonnées pour centrer l'image
            image_x = (page_width - image_width) / 2  # Centrer horizontalement
            image_y = (page_height - image_height) / 2  # Centrer verticalement
            c.drawImage('organigramme.png', image_x, image_y, image_width, image_height)


        # Passer à la page suivante
        c.showPage()

    # Finaliser le PDF temporaire
    c.save()

    # Lire le PDF temporaire
    overlay_pdf = PdfReader(temp_pdf_path)

    # Fusionner les deux PDFs
    for page_num in range(num_pages):
        template_page = template_pdf.pages[page_num]
        if page_num < len(overlay_pdf.pages):
            overlay_page = overlay_pdf.pages[page_num]
            merger = PageMerge(template_page)
            merger.add(overlay_page).render()

    # Écrire le PDF final
    PdfWriter().write(output_path, template_pdf)

    # Supprimer le fichier temporaire
    os.remove(temp_pdf_path)

