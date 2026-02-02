"""
Point d'entree Streamlit de l'application BarStock.

Role de ce fichier:
- configurer l'application Streamlit (titre, layout),
- appliquer le theme commun (charge depuis ui.py -> styles.css),
- declarer le routage entre les items du menu et les pages,
- construire la sidebar,
- appeler la fonction de rendu de la page selectionnee.

Dependances principales:
- ui.apply_theme(): injecte le CSS global.
- pages.*.render_*(): fonctions d'affichage de chaque module metier.
"""

import streamlit as st

from ui import apply_theme
from pages.dashboard import render_dashboard
from pages.products import render_products
from pages.entries import render_entries
from pages.sales import render_sales
from pages.charges import render_charges
from pages.reports import render_reports

# Configuration globale Streamlit. Elle doit etre appelee tres tot.
st.set_page_config(page_title="Gestion Stock Bar", layout="wide")

# Le theme est centralise dans ui.py pour que toutes les pages partagent
# exactement le meme rendu (couleurs, typo, sidebar, tables, etc.).
apply_theme()

# Table de routage principale:
# la cle (texte du menu) est ce que voit l'utilisateur,
# la valeur est la fonction "render_*" importee depuis un fichier de page.
PAGES = {
    "Tableau de bord": render_dashboard,
    "Produits": render_products,
    "Entrees": render_entries,
    "Ventes": render_sales,
    "Charges": render_charges,
    "Rapports": render_reports,
}

# Sidebar custom:
# - branding + description
# - champ recherche (UI uniquement ici, non branche a un filtre pour le moment)
# - menu radio de navigation
# - bloc support.
with st.sidebar:
    st.markdown("<div class='sidebar-brand'>BarStock</div>", unsafe_allow_html=True)
    st.markdown("<div class='sidebar-sub'>Gestion de stock</div>", unsafe_allow_html=True)
    st.text_input("Search", placeholder="Rechercher", label_visibility="collapsed")
    st.markdown("<div class='sidebar-section'>Menu</div>", unsafe_allow_html=True)
    choice = st.radio(
        "Navigation",
        list(PAGES.keys()),
        label_visibility="collapsed",
        # Cle explicite pour stabiliser la valeur de navigation entre reruns.
        key="main_navigation",
    )
    st.markdown("<div class='sidebar-section'>Support</div>", unsafe_allow_html=True)
    st.caption("Aide et assistance")

# Resolution + execution:
# - get(...) ajoute une securite (fallback sur dashboard si la cle est absente).
# - la fonction de page appelle ensuite data_access.py et ui.py selon son besoin.
page_renderer = PAGES.get(choice, render_dashboard)
page_renderer()
