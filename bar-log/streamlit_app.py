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

# Si une URL de type ?products_tab=...&edit_product=... ou ...&delete_product=...
# (clic ligne "Modifier/Supprimer"), on force l'entree sur la page Produits
# uniquement au demarrage de session.
query_edit_product = st.query_params.get("edit_product")
query_delete_product = st.query_params.get("delete_product")
query_products_tab = st.query_params.get("products_tab")
if isinstance(query_edit_product, list):
    query_edit_product = query_edit_product[0] if query_edit_product else None
if isinstance(query_delete_product, list):
    query_delete_product = query_delete_product[0] if query_delete_product else None
if isinstance(query_products_tab, list):
    query_products_tab = query_products_tab[0] if query_products_tab else None
if query_edit_product or query_delete_product:
    st.session_state["main_navigation"] = "Produits"
elif "main_navigation" not in st.session_state and query_products_tab:
    st.session_state["main_navigation"] = "Produits"

# Sidebar custom:
# - branding + description
# - champ recherche (UI uniquement ici, non branche a un filtre pour le moment)
# - menu radio de navigation
# - bloc support.
with st.sidebar:
    st.markdown(
        """
        <div class='sidebar-top'>
          <div>
            <div class='sidebar-brand'>BarStock</div>
            <div class='sidebar-sub'>Gestion de stock</div>
          </div>
          <span class='sidebar-chevron material-symbols-outlined'>double_arrow</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.text_input("Search", placeholder="Rechercher", label_visibility="collapsed")
    st.markdown("<div class='sidebar-section'>Menu</div>", unsafe_allow_html=True)
    choice = st.radio(
        "Navigation",
        list(PAGES.keys()),
        label_visibility="collapsed",
        # Cle explicite pour stabiliser la valeur de navigation entre reruns.
        key="main_navigation",
    )
    st.markdown(
        """
        <div class='sidebar-support-wrap'>
          <div class='sidebar-section'>Support</div>
          <div class='sidebar-help'>
            <span class='material-symbols-outlined'>help</span>
            <span>Aide et assistance</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Resolution + execution:
# - get(...) ajoute une securite (fallback sur dashboard si la cle est absente).
# - la fonction de page appelle ensuite data_access.py et ui.py selon son besoin.
page_renderer = PAGES.get(choice, render_dashboard)
page_renderer()
