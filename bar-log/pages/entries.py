"""
Page "Entrees de stock".

Interaction:
- utilise list_products() pour proposer les articles existants,
- utilise add_stock_entry() pour creer l'entree + mettre a jour le stock,
- utilise list_entries() pour afficher l'historique filtre,
- utilise ui.py pour rendu titre/table et mapping produit.
"""

from datetime import date

import streamlit as st

from data_access import add_stock_entry, list_entries, list_products
from ui import build_product_map, render_page_title, show_dataframe


def render_entries():
    """Rend le formulaire de saisie et l'historique des entrees de stock."""
    render_page_title("Entrees de stock", "Approvisionnements et historique")
    products_df = list_products()

    # Reinitialisation controlee des widgets apres un enregistrement reussi.
    if st.session_state.get("entry_reset"):
        st.session_state["entry_product"] = None
        st.session_state["entry_quantite"] = 1
        st.session_state["entry_date"] = date.today()
        st.session_state["entry_prix_achat"] = 0.0
        st.session_state["entry_unite"] = "bouteille"
        st.session_state["entry_prix_vente"] = 0.0
        st.session_state["entry_reset"] = False

    # Message de confirmation post-rerun.
    if st.session_state.get("entry_added"):
        st.success("Entree enregistree")
        st.session_state["entry_added"] = False

    # Bloc de creation d'une entree.
    with st.form("add_entry", clear_on_submit=True):
        if products_df.empty:
            st.info("Ajoutez un produit avant de saisir une entree")
            submitted = st.form_submit_button("Enregistrer")
        else:
            # Mapping label -> row pour recuperer id_produit au submit.
            product_map = build_product_map(products_df)
            selected = st.selectbox(
                "Produit",
                list(product_map.keys()),
                index=None,
                placeholder="Selectionner ou rechercher le produit",
                key="entry_product",
            )
            quantite = st.number_input(
                "Quantite", min_value=1, step=1, key="entry_quantite"
            )
            date_entree = st.date_input("Date entree", value=date.today(), key="entry_date")
            prix_achat = st.number_input(
                "Prix achat", min_value=0.0, step=0.01, key="entry_prix_achat"
            )
            unite_vente = st.selectbox("Unite de vente", ["bouteille", "verre"], key="entry_unite")
            prix_vente = st.number_input(
                "Prix vente", min_value=0.0, step=0.01, key="entry_prix_vente"
            )
            submitted = st.form_submit_button("Enregistrer")

        if submitted:
            # Validations avant ecriture en base.
            if products_df.empty:
                st.error("Aucun produit disponible")
            elif selected is None:
                st.error("Selectionnez un produit")
            elif prix_achat <= 0 or prix_vente <= 0:
                st.error("Prix d'achat et prix de vente obligatoires")
            else:
                product = product_map[selected]
                add_stock_entry(
                    product["id_produit"],
                    quantite,
                    date_entree,
                    prix_achat,
                    prix_vente,
                    unite_vente,
                )
                st.session_state["entry_added"] = True
                st.session_state["entry_reset"] = True
                st.rerun()

    # Bloc historique avec filtres.
    st.subheader("Historique")
    if products_df.empty:
        st.info("Aucun produit")
        return

    product_map = build_product_map(products_df)
    col1, col2, col3 = st.columns(3)
    start_date = col1.date_input("Debut", value=date.today().replace(day=1), key="entree_start")
    end_date = col2.date_input("Fin", value=date.today(), key="entree_end")
    product_filter = col3.selectbox("Produit", ["Tous"] + list(product_map.keys()), key="entree_product")

    product_id = None
    if product_filter != "Tous":
        product_id = product_map[product_filter]["id_produit"]

    entries_df = list_entries(start_date, end_date, product_id)
    show_dataframe(entries_df, "Aucune entree sur la periode")
