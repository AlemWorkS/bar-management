"""
Page "Produits": CRUD sur le catalogue.

Interaction:
- streamlit_app.py selectionne cette page via le menu sidebar.
- data_access.py fournit list/create/update/delete produit/categorie.
- ui.py fournit les helpers visuels et de mapping utilises ici.
"""

import streamlit as st

from data_access import (
    create_product,
    delete_product,
    list_categories,
    list_products,
    update_product,
)
from ui import (
    build_category_map,
    get_category_key,
    render_page_title,
    render_product_table,
    show_dataframe,
)


def render_products():
    """
    Rend les 4 onglets de gestion produit:
    - Liste
    - Ajouter
    - Modifier
    - Supprimer
    """
    render_page_title("Produits", "Catalogue et gestion du stock")

    # Chargement initial des donnees depuis la base.
    products_df = list_products()
    # Seules les categories "stockables" sont autorisees pour les produits.
    categories_df = list_categories(stockable=True)

    tab_list, tab_add, tab_edit, tab_delete = st.tabs(
        ["Liste", "Ajouter", "Modifier", "Supprimer"]
    )

    with tab_list:
        # Transformation visuelle uniquement (pas d'impact DB).
        display_df = products_df.copy()
        if "id_categorie" in display_df.columns:
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
        show_dataframe(display_df, "Aucun produit")

    with tab_add:
        # Message post-action apres rerun.
        if st.session_state.get("product_added"):
            st.success("Produit ajoute")
            st.session_state["product_added"] = False

        # Mapping label -> row categorie pour convertir la selection en id SQL.
        category_map = None
        category_keys = []
        if not categories_df.empty:
            category_map = build_category_map(categories_df)
            category_keys = list(category_map.keys())

        with st.form("add_product", clear_on_submit=True):
            if categories_df.empty:
                st.info("Ajoutez des categories stockables avant de creer un produit")
                submitted = st.form_submit_button("Ajouter")
            else:
                nom = st.text_input("Nom du produit")
                categorie_key = st.selectbox("Categorie", category_keys)
                submitted = st.form_submit_button("Ajouter")

        # Traitement submit + validation metier.
        if submitted:
            if categories_df.empty:
                st.error("Aucune categorie stockable disponible")
            elif not nom:
                st.error("Nom du produit requis")
            else:
                category = category_map[categorie_key]
                create_product(nom, category["id_categorie"])
                st.session_state["product_added"] = True
                st.rerun()

    with tab_edit:
        # Si catalogue vide, pas d'edition possible.
        if products_df.empty or categories_df.empty:
            st.info("Aucun produit a modifier")
        else:
            if st.session_state.get("product_updated"):
                st.success("Produit modifie")
                st.session_state["product_updated"] = False

            # Etape 1: selection d'une ligne source.
            selected_product = render_product_table(products_df, key="edit_product_table")
            if selected_product is None:
                st.info("Selectionnez une ligne du tableau")
            else:
                # Etape 2: charger la ligne choisie dans session_state.
                if st.button("Charger pour modifier", key="load_product_edit"):
                    st.session_state["edit_loaded_id"] = selected_product["id_produit"]
                    st.session_state["edit_nom"] = selected_product["nom_produit"]
                    st.session_state["edit_prix_achat"] = float(selected_product["prix_achat"])
                    st.session_state["edit_prix_vente_bouteille"] = float(
                        selected_product["prix_vente_bouteille"]
                    )
                    st.session_state["edit_prix_vente_verre"] = float(
                        selected_product["prix_vente_verre"]
                    )
                    st.session_state["edit_stock"] = int(selected_product["stock_actuel"])
                    st.session_state["edit_unite_vente"] = selected_product["unite_vente"]
                    st.session_state["edit_categorie_id"] = selected_product["id_categorie"]
                    st.rerun()

            # Etape 3: afficher le formulaire si un produit est charge.
            if st.session_state.get("edit_loaded_id"):
                category_map = build_category_map(categories_df)
                category_keys = list(category_map.keys())
                default_cat_key = get_category_key(
                    category_map, st.session_state.get("edit_categorie_id")
                )
                if default_cat_key is None:
                    default_cat_key = category_keys[0]
                cat_index = category_keys.index(default_cat_key)

                with st.form("edit_product"):
                    nom = st.text_input("Nom du produit", key="edit_nom")
                    categorie_key = st.selectbox("Categorie", category_keys, index=cat_index)
                    prix_achat = st.number_input(
                        "Prix achat", min_value=0.0, step=0.01, key="edit_prix_achat"
                    )
                    prix_vente_bouteille = st.number_input(
                        "Prix vente bouteille",
                        min_value=0.0,
                        step=0.01,
                        key="edit_prix_vente_bouteille",
                    )
                    prix_vente_verre = st.number_input(
                        "Prix vente verre", min_value=0.0, step=0.01, key="edit_prix_vente_verre"
                    )
                    stock_actuel = st.number_input(
                        "Stock actuel", min_value=0, step=1, key="edit_stock"
                    )
                    unite_vente = st.selectbox(
                        "Unite de vente", ["bouteille", "verre"], key="edit_unite_vente"
                    )
                    submitted = st.form_submit_button("Mettre a jour")

                if submitted:
                    if not nom:
                        st.error("Nom du produit requis")
                    else:
                        category = category_map[categorie_key]
                        update_product(
                            st.session_state["edit_loaded_id"],
                            nom,
                            category["id_categorie"],
                            prix_achat,
                            prix_vente_bouteille,
                            prix_vente_verre,
                            stock_actuel,
                            unite_vente,
                        )
                        st.session_state["product_updated"] = True
                        st.session_state.pop("edit_loaded_id", None)
                        st.rerun()

    with tab_delete:
        if products_df.empty:
            st.info("Aucun produit a supprimer")
        else:
            if st.session_state.get("product_deleted"):
                st.success("Produit supprime")
                st.session_state["product_deleted"] = False

            selected_product = render_product_table(products_df, key="delete_product_table")
            if selected_product is None:
                st.info("Selectionnez une ligne du tableau")
            else:
                # Confirmation explicite pour eviter les suppressions accidentelles.
                confirm = st.radio(
                    "Confirmer la suppression ?",
                    ["Non", "Oui"],
                    index=0,
                    horizontal=True,
                    key="delete_confirm",
                )
                if st.button("Supprimer", key="delete_product_button"):
                    if confirm != "Oui":
                        st.warning("Suppression annulee")
                    else:
                        try:
                            delete_product(selected_product["id_produit"])
                            st.session_state["product_deleted"] = True
                            st.rerun()
                        except Exception as exc:
                            # Ex: contraintes SQL si references existantes.
                            st.error(f"Suppression impossible: {exc}")
