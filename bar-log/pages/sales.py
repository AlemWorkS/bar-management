"""
Page "Ventes".

Interaction principale:
- lit les produits/categories via data_access.list_products/list_categories,
- construit une "liste de ticket" locale dans st.session_state,
- persiste le ticket en base via create_receipt + add_sale_stockable,
- affiche l'historique via data_access.list_sales,
- utilise ui.py pour formattage FCFA et mappings selectbox.
"""

from datetime import date
from decimal import Decimal

import pandas as pd
import streamlit as st

from data_access import add_sale_stockable, create_receipt, list_categories, list_products, list_sales
from ui import build_category_map, build_product_map, fmt_fcfa


def render_sales():
    """Rend la saisie des ventes du jour puis l'historique filtre."""
    st.markdown(
        "<div class='breadcrumb'>Tableau de bord / <span class='active'>Ventes</span></div>",
        unsafe_allow_html=True,
    )

    # Donnees de reference depuis la DB.
    products_df = list_products()
    categories_df = list_categories()

    # Liste temporaire du ticket courant (non persistee tant que non validee).
    if "receipt_items" not in st.session_state:
        st.session_state["receipt_items"] = []

    # Reinitialisation de widgets apres ajout de ligne.
    if st.session_state.get("sale_reset"):
        st.session_state["sale_product"] = None
        st.session_state["sale_quantite"] = 1
        st.session_state["sale_unit_price"] = 0.0
        st.session_state["sale_unite"] = "bouteille"
        st.session_state["sale_unite_display"] = "bouteille"
        st.session_state["sale_reset"] = False

    # Sans categories, on ne peut pas enregistrer de ventes coherentes.
    if categories_df.empty:
        st.info("Ajoutez des categories avant de saisir une vente")
        return

    # Mapping label -> row produit pour les selectbox.
    product_map = build_product_map(products_df) if not products_df.empty else {}

    # Bandeau d'entete + bouton de validation globale du ticket.
    header_left, header_right = st.columns([3, 1], vertical_alignment="bottom")
    with header_left:
        st.markdown("## Ventes du jour")
        st.markdown(
            "<div class='sales-muted'>Enregistrez les sorties de stock et suivez les ventes quotidiennes.</div>",
            unsafe_allow_html=True,
        )
    with header_right:
        st.markdown("<div style='height: 1.6rem'></div>", unsafe_allow_html=True)
        save_clicked = st.button(
            "Enregistrer les ventes",
            use_container_width=True,
            disabled=not st.session_state["receipt_items"],
        )

    # Libelles categories pour affichage du tableau ticket.
    category_labels = {
        row["id_categorie"]: f"{row['libelle']} (#{row['id_categorie']})"
        for row in categories_df.to_dict("records")
    }

    # Variables de travail alimentant le formulaire "ajout ligne ticket".
    selected_product = None
    selected_key = None
    prix_unitaire = st.session_state.get("sale_unit_price", 0.0)
    quantite = st.session_state.get("sale_quantite", 1)
    unite_vente = st.session_state.get("sale_unite", "bouteille")

    # Carte de saisie d'une ligne de vente.
    st.markdown("<div class='sales-card'>", unsafe_allow_html=True)
    cols = st.columns([2, 4, 2, 2, 2, 0.8], vertical_alignment="bottom")
    with cols[0]:
        sale_day = st.date_input("Date", value=date.today(), key="sale_day")
    with cols[1]:
        if products_df.empty:
            st.info("Ajoutez un produit avant de saisir une vente")
            selected_key = None
        else:
            selected_key = st.selectbox(
                "Produit",
                list(product_map.keys()),
                index=None,
                placeholder="Selectionner un produit",
                key="sale_product",
            )
    with cols[2]:
        quantite = st.number_input("Quantite", min_value=1, step=1, key="sale_quantite")
    with cols[3]:
        # L'unite/prix affiches sont derives du produit selectionne.
        if selected_key:
            selected_product = product_map[selected_key]
            unite_vente = selected_product.get("unite_vente", "bouteille")
            st.session_state["sale_unite"] = unite_vente
            if unite_vente == "verre":
                prix_unitaire = float(selected_product.get("prix_vente_verre") or 0)
            else:
                prix_unitaire = float(selected_product.get("prix_vente_bouteille") or 0)
            st.session_state["sale_unit_price"] = prix_unitaire
        else:
            st.session_state["sale_unit_price"] = 0.0
            prix_unitaire = 0.0

        st.session_state["sale_unite_display"] = unite_vente
        st.selectbox(
            "Unite",
            ["bouteille", "verre"],
            index=0 if unite_vente == "bouteille" else 1,
            key="sale_unite_display",
            disabled=True,
        )
    with cols[4]:
        st.number_input(
            "Prix vente (FCFA)",
            value=float(prix_unitaire),
            step=0.01,
            disabled=True,
        )
    with cols[5]:
        add_clicked = st.button("+", key="sale_add_btn")
    st.markdown("</div>", unsafe_allow_html=True)

    # Ajout d'une ligne dans le ticket temporaire.
    if add_clicked:
        if products_df.empty:
            st.error("Aucun produit disponible")
        elif selected_product is None:
            st.error("Selectionnez un produit")
        elif prix_unitaire <= 0:
            st.error("Prix de vente non defini pour ce produit")
        else:
            st.session_state["receipt_items"].append(
                {
                    "product_id": selected_product["id_produit"],
                    "product_label": selected_key,
                    "quantite": quantite,
                    "date_vente": sale_day,
                    "unite_vente": unite_vente,
                }
            )
            st.session_state["sale_reset"] = True
            st.rerun()

    # Calcul d'un recap ticket (montant/marge) avant persistence.
    receipt_items = st.session_state["receipt_items"]
    display_items = []
    total_montant = Decimal("0")
    total_quantite = 0
    total_marge = Decimal("0")
    product_lookup = {row["id_produit"]: row for row in products_df.to_dict("records")}

    for item in receipt_items:
        product = product_lookup.get(item["product_id"])
        prix_achat = Decimal(str(product.get("prix_achat") or 0))
        prix_vente_btl = Decimal(str(product.get("prix_vente_bouteille") or 0))
        if item["unite_vente"] == "verre":
            prix_vente = Decimal(str(product.get("prix_vente_verre") or 0))
        else:
            prix_vente = prix_vente_btl

        qty = Decimal(item["quantite"])
        cout_total_vente = (prix_vente * qty).quantize(Decimal("0.01"))
        marge_ligne = cout_total_vente - (prix_achat * qty)

        article = product["nom_produit"] if product else item["product_label"]
        categorie = category_labels.get(product.get("id_categorie"), "")

        display_items.append(
            {
                "Produit": article,
                "Categorie": categorie,
                "Quantite": item["quantite"],
                "Unite": item["unite_vente"],
                "Montant": float(cout_total_vente),
                "Marge": float(marge_ligne),
            }
        )
        total_montant += cout_total_vente
        total_quantite += item["quantite"]
        total_marge += marge_ligne

    # Ligne total ajoutee uniquement si le ticket contient au moins une ligne.
    if display_items:
        display_items.append(
            {
                "Produit": "Total du jour",
                "Categorie": "",
                "Quantite": total_quantite,
                "Unite": "",
                "Montant": float(total_montant),
                "Marge": float(total_marge),
            }
        )

    # Affichage du ticket temporaire + actions de purge.
    if display_items:
        st.markdown("<div class='sales-card'>", unsafe_allow_html=True)
        table_df = pd.DataFrame(
            display_items,
            columns=["Produit", "Categorie", "Quantite", "Unite", "Montant", "Marge"],
        )
        for col in ["Montant", "Marge"]:
            if col in table_df.columns:
                table_df[col] = table_df[col].apply(fmt_fcfa)
        st.dataframe(table_df, use_container_width=True, hide_index=True)

        action_col, total_col = st.columns([1, 2])
        if action_col.button("Vider la liste", key="clear_receipt_items"):
            st.session_state["receipt_items"] = []
            st.rerun()

        total_col.markdown(
            f"**Total Ventes**: {fmt_fcfa(total_montant)} | **Marge estimee**: {fmt_fcfa(total_marge)}"
        )
        st.markdown("</div>", unsafe_allow_html=True)

    # Validation definitive: ecriture du recu + des lignes de vente en base.
    if save_clicked:
        receipt_id = create_receipt()
        for item in st.session_state["receipt_items"]:
            add_sale_stockable(
                item["product_id"],
                item["quantite"],
                item["date_vente"],
                item["unite_vente"],
                receipt_id,
            )
        st.session_state["receipt_items"] = []
        st.session_state["sale_reset"] = True
        st.success("Ventes enregistrees")
        st.rerun()

    # ----------------------------
    # Historique des ventes
    # ----------------------------
    st.markdown("<div class='sales-section-title'>Historique</div>", unsafe_allow_html=True)
    if categories_df.empty:
        st.info("Aucune categorie")
        return

    product_map = build_product_map(products_df) if not products_df.empty else {}
    category_map = build_category_map(categories_df)
    hist_left, hist_right = st.columns([3, 2], vertical_alignment="center")
    with hist_left:
        period_cols = st.columns(2)
        start_date = period_cols[0].date_input(
            "Periode debut", value=date.today().replace(day=1), key="vente_start"
        )
        end_date = period_cols[1].date_input("Periode fin", value=date.today(), key="vente_end")
    with hist_right:
        filter_cols = st.columns(2)
        category_filter = filter_cols[0].selectbox(
            "Categorie", ["Toutes"] + list(category_map.keys()), key="vente_category"
        )
        product_filter = filter_cols[1].selectbox(
            "Produit", ["Tous"] + list(product_map.keys()), key="vente_product"
        )

    product_id = None
    if product_filter != "Tous":
        product_id = product_map[product_filter]["id_produit"]
    category_id = None
    if category_filter != "Toutes":
        category_id = category_map[category_filter]["id_categorie"]

    sales_df = list_sales(start_date, end_date, product_id, category_id)
    if sales_df.empty:
        st.info("Aucune vente sur la periode")
        return

    # Normalisation des noms de colonnes pour l'UI.
    display_sales = sales_df.rename(
        columns={
            "date_vente": "Date",
            "article": "Produit",
            "categorie": "Categorie",
            "quantite": "Qte",
            "type_vente": "Type",
            "montant": "Montant",
            "marge": "Marge",
        }
    )
    display_sales = display_sales[["Date", "Produit", "Categorie", "Qte", "Type", "Montant", "Marge"]]
    for col in ["Montant", "Marge"]:
        display_sales[col] = display_sales[col].apply(fmt_fcfa)

    st.markdown("<div class='sales-card'>", unsafe_allow_html=True)
    st.dataframe(display_sales, use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)
