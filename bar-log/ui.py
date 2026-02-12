"""
Utilitaires UI partages par toutes les pages.

Objectif de ce module:
- eviter de dupliquer le rendu commun (theme, titres, format FCFA, tables),
- standardiser les conventions d'affichage de toute l'application,
- fournir des helpers de mapping utilises dans les formulaires/pages.

Interaction avec les autres modules:
- streamlit_app.py appelle apply_theme() une seule fois au demarrage.
- pages/*.py appellent render_page_title(), show_dataframe(), fmt_fcfa() etc.
- les fonctions de mapping recoivent des DataFrame venant de data_access.py.
"""

from decimal import Decimal
from pathlib import Path

import streamlit as st


def apply_theme():
    """Charge styles.css et l'injecte globalement dans Streamlit."""
    css_path = Path(__file__).resolve().parent / "styles.css"
    if not css_path.exists():
        # Pas de CSS -> on laisse Streamlit afficher le style par defaut.
        return
    css = css_path.read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def render_page_title(title, subtitle=None):
    """
    Rend un titre de page uniforme.

    Ce composant est utilise par les pages metier pour garder le meme
    pattern visuel partout (titre + sous-titre facultatif).
    """
    st.markdown(f"<div class='page-title'>{title}</div>", unsafe_allow_html=True)
    if subtitle:
        st.markdown(
            f"<div class='page-subtitle'>{subtitle}</div>",
            unsafe_allow_html=True,
        )


def fmt_fcfa(value):
    """
    Formate une valeur monetaire en FCFA.

    Utilise Decimal pour eviter des artefacts d'arrondi float.
    """
    try:
        return f"{Decimal(str(value)):,.2f} FCFA"
    except Exception:
        # Fallback defensif: l'UI affiche toujours une valeur lisible.
        return "0.00 FCFA"


def show_dataframe(df, empty_message):
    """
    Affiche un DataFrame avec un comportement uniforme.

    - si vide: message d'information clair,
    - sinon: tableau Streamlit plein largeur sans index.
    """
    if df.empty:
        st.info(empty_message)
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)


def build_product_map(products_df):
    """
    Construit un mapping label -> row produit.

    Utilise par les selectbox de pages/entries.py et pages/sales.py:
    le label est lisible pour l'utilisateur, la valeur row contient l'id SQL.
    """
    return {
        f"{row['nom_produit']} (#{row['id_produit']})": row
        for row in products_df.to_dict("records")
    }


def build_category_map(categories_df):
    """
    Construit un mapping label -> row categorie.

    Utilise par pages/products.py et pages/sales.py pour convertir
    une selection utilisateur en id_categorie pour data_access.py.
    """
    return {
        f"{row['libelle']} (#{row['id_categorie']})": row
        for row in categories_df.to_dict("records")
    }


def filter_products_by_category(products_df, category_id):
    """Retourne les produits d'une categorie, sans casser si df vide."""
    if products_df.empty:
        return products_df
    return products_df[products_df["id_categorie"] == category_id]


def render_product_table(products_df, key):
    """
    Rend un tableau produit selectionnable et retourne la row choisie.

    Cette fonction sert surtout dans pages/products.py (edit/delete):
    - on affiche un tableau user-friendly (colonnes renommees),
    - on laisse Streamlit gerer la selection d'une seule ligne,
    - on renvoie ensuite la ligne originale (avec colonnes techniques).
    """
    if products_df.empty:
        st.info("Aucun produit")
        return None

    # Copie d'affichage: on ne modifie jamais le DataFrame source.
    display_df = products_df.copy()
    if "id_categorie" in display_df.columns:
        # Cache l'id technique dans la vue utilisateur.
        display_df = display_df.drop(columns=["id_categorie"])
    display_df = display_df.rename(
        columns={
            "id_produit": "ID produit",
            "nom_produit": "Produit",
            "categorie": "Categorie",
            "prix_achat": "Prix achat",
            "prix_vente_bouteille": "Prix vente bouteille",
            "prix_vente_verre": "Prix vente verre",
            "stock_actuel": "Stock actuel",
            "unite_vente": "Unite vente",
        }
    )

    event = st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row",
        key=key,
    )
    if not event.selection.rows:
        return None

    # Translate index visuel -> row du DataFrame source.
    row_index = event.selection.rows[0]
    return products_df.iloc[row_index].to_dict()


def get_category_key(category_map, category_id):
    """
    Trouve la cle selectbox correspondant a un id_categorie.

    Utilise pour preselectionner la categorie dans le formulaire edit produit.
    """
    for key, row in category_map.items():
        if row["id_categorie"] == category_id:
            return key
    return None
