"""
Page "Entrees de stock".

Interaction:
- utilise list_products() pour proposer les articles existants,
- utilise add_stock_entry() pour creer l'entree + mettre a jour le stock,
- utilise list_entries() pour afficher l'historique filtre.
"""

import math
from datetime import date
from html import escape
from textwrap import dedent

import streamlit as st

from data_access import add_stock_entry, list_entries, list_products
from ui import build_product_map, render_page_title


def _entry_category_class(category_name):
    """Retourne la classe CSS de badge selon la categorie."""
    name = (category_name or "").lower()
    if "liqueur" in name:
        return "entries-pill-blue"
    if "sirop" in name:
        return "entries-pill-green"
    if "sucrerie" in name or "boisson" in name or "soft" in name:
        return "entries-pill-yellow"
    if "vin" in name:
        return "entries-pill-red"
    if "whisky" in name:
        return "entries-pill-purple"
    return "entries-pill-gray"


def _entry_icon_for_category(category_name):
    """Retourne une icone et une classe couleur selon la categorie produit."""
    name = (category_name or "").lower()
    if "liqueur" in name:
        return "local_bar", "entries-icon-orange"
    if "sirop" in name:
        return "liquor", "entries-icon-green"
    if "sucrerie" in name or "boisson" in name or "soft" in name:
        return "local_drink", "entries-icon-yellow"
    if "vin" in name:
        return "wine_bar", "entries-icon-red"
    if "whisky" in name:
        return "local_bar", "entries-icon-purple"
    return "inventory_2", "entries-icon-gray"


def _build_entries_table_html(entries_df):
    """Construit le tableau HTML de l'historique des entrees."""
    rows_html = []
    rows = entries_df.to_dict("records")

    for row in rows:
        date_text = escape(str(row.get("date_entree") or ""))
        product_name = escape(str(row.get("nom_produit") or "-"))
        category = str(row.get("categorie") or "Sans categorie")
        category_safe = escape(category)
        qty_text = escape(str(row.get("quantite") or 0))

        badge_class = _entry_category_class(category)
        icon_name, icon_class = _entry_icon_for_category(category)

        rows_html.append(
            dedent(
                f"""
                <tr>
                  <td>{date_text}</td>
                  <td>
                    <div class="entries-product-cell">
                      <div class="entries-product-icon {icon_class}">
                        <span class="material-symbols-outlined">{icon_name}</span>
                      </div>
                      <div class="entries-product-name">{product_name}</div>
                    </div>
                  </td>
                  <td><span class="entries-pill {badge_class}">{category_safe}</span></td>
                  <td class="entries-col-right">{qty_text}</td>
                </tr>
                """
            ).strip()
        )

    if not rows_html:
        rows_html.append(
            "<tr><td colspan='4' class='entries-empty'>Aucune entree sur la periode</td></tr>"
        )

    return dedent(
        f"""
        <div class="entries-history-table-wrap">
          <table class="entries-history-table">
            <thead>
              <tr>
                <th>DATE</th>
                <th>PRODUIT</th>
                <th>CATEGORIE</th>
                <th class="entries-col-right">QUANTITE</th>
              </tr>
            </thead>
            <tbody>
              {''.join(rows_html)}
            </tbody>
          </table>
        </div>
        """
    ).strip()


def render_entries():
    """Rend le formulaire de saisie et l'historique des entrees de stock."""
    render_page_title("Entrees de stock", "Approvisionnements et historique")
    products_df = list_products()
    product_map = build_product_map(products_df) if not products_df.empty else {}

    # Reinitialisation controlee des widgets apres un enregistrement reussi.
    if st.session_state.get("entry_reset"):
        st.session_state["entry_product"] = None
        st.session_state["entry_quantite"] = 1
        st.session_state["entry_date"] = date.today()
        st.session_state["entry_prix_achat"] = 0.0
        st.session_state["entry_unite"] = "bouteille"
        st.session_state["entry_prix_vente"] = 0.0
        st.session_state["entry_reset"] = False

    if st.session_state.get("entry_added"):
        st.success("Entree enregistree")
        st.session_state["entry_added"] = False

    selected = None
    quantite = st.session_state.get("entry_quantite", 1)
    date_entree = st.session_state.get("entry_date", date.today())
    unite_vente = st.session_state.get("entry_unite", "bouteille")
    prix_achat = float(st.session_state.get("entry_prix_achat", 0.0))
    prix_vente = float(st.session_state.get("entry_prix_vente", 0.0))
    submitted = False

    left_col, right_col = st.columns([1.05, 2.2], gap="large")

    with left_col:
        with st.container(border=True, key="entries_form_card"):
            st.markdown(
                (
                    "<div class='entries-card-title'>"
                    "<span class='material-symbols-outlined'>add_circle</span>"
                    "<span>Nouvelle entree</span>"
                    "</div>"
                ),
                unsafe_allow_html=True,
            )
            if products_df.empty:
                st.info("Ajoutez un produit avant de saisir une entree")
                st.selectbox(
                    "Produit",
                    ["Selectionner un produit"],
                    index=0,
                    disabled=True,
                    key="entry_product_empty",
                    width="stretch",
                )
                quantity_cols = st.columns([1.1, 1], gap="small")
                quantity_cols[0].number_input(
                    "Quantite",
                    min_value=1,
                    step=1,
                    value=1,
                    disabled=True,
                    key="entry_quantite_empty",
                    width="stretch",
                )
                quantity_cols[1].selectbox(
                    "Unite",
                    ["bouteille", "verre"],
                    index=0,
                    disabled=True,
                    key="entry_unite_empty",
                    width="stretch",
                )
                st.date_input(
                    "Date d'entree",
                    value=date.today(),
                    disabled=True,
                    key="entry_date_empty",
                    width="stretch",
                )
                price_cols = st.columns(2, gap="small")
                price_cols[0].number_input(
                    "Prix Achat",
                    min_value=0.0,
                    value=0.0,
                    step=0.01,
                    format="%.2f",
                    disabled=True,
                    key="entry_prix_achat_empty",
                    width="stretch",
                )
                price_cols[1].number_input(
                    "Prix Vente",
                    min_value=0.0,
                    value=0.0,
                    step=0.01,
                    format="%.2f",
                    disabled=True,
                    key="entry_prix_vente_empty",
                    width="stretch",
                )
                st.button(
                    "Enregistrer l'entree",
                    key="entry_submit_btn",
                    width="stretch",
                    disabled=True,
                )
            else:
                selected = st.selectbox(
                    "Produit",
                    list(product_map.keys()),
                    index=None,
                    placeholder="Selectionner un produit",
                    key="entry_product",
                    width="stretch",
                )

                quantity_cols = st.columns([1.1, 1], gap="small")
                quantite = quantity_cols[0].number_input(
                    "Quantite",
                    min_value=1,
                    step=1,
                    key="entry_quantite",
                    width="stretch",
                )
                unite_vente = quantity_cols[1].selectbox(
                    "Unite",
                    ["bouteille", "verre"],
                    key="entry_unite",
                    width="stretch",
                )

                date_entree = st.date_input(
                    "Date d'entree",
                    value=date.today(),
                    key="entry_date",
                    width="stretch",
                )

                price_cols = st.columns(2, gap="small")
                prix_achat = price_cols[0].number_input(
                    "Prix Achat",
                    min_value=0.0,
                    step=0.01,
                    key="entry_prix_achat",
                    width="stretch",
                )
                prix_vente = price_cols[1].number_input(
                    "Prix Vente",
                    min_value=0.0,
                    step=0.01,
                    key="entry_prix_vente",
                    width="stretch",
                )

                submitted = st.button(
                    "Enregistrer l'entree",
                    key="entry_submit_btn",
                    width="stretch",
                )

    with right_col:
        with st.container(border=True, key="entries_filter_card"):
            st.markdown("<div class='entries-filter-title'>Filtrer l'historique</div>", unsafe_allow_html=True)

            filter_cols = st.columns([1, 1, 1.25], gap="small")
            start_date = filter_cols[0].date_input(
                "Debut",
                value=date.today().replace(day=1),
                key="entree_start",
                width="stretch",
            )
            end_date = filter_cols[1].date_input(
                "Fin",
                value=date.today(),
                key="entree_end",
                width="stretch",
            )
            product_filter = filter_cols[2].selectbox(
                "Produit",
                ["Tous les produits"] + list(product_map.keys()),
                key="entree_product",
                width="stretch",
            )

        product_id = None
        if product_filter != "Tous les produits":
            product_id = product_map[product_filter]["id_produit"]
        entries_df = list_entries(start_date, end_date, product_id)

        page_size = 5
        total_entries = len(entries_df)
        total_pages = max(1, math.ceil(total_entries / page_size))
        page_key = "entries_history_page"
        filters_key = (
            str(start_date),
            str(end_date),
            str(product_id if product_id is not None else "all"),
        )

        if st.session_state.get("entries_history_filters") != filters_key:
            st.session_state["entries_history_filters"] = filters_key
            st.session_state[page_key] = 1

        current_page = st.session_state.get(page_key, 1)
        if current_page < 1:
            current_page = 1
        if current_page > total_pages:
            current_page = total_pages
        st.session_state[page_key] = current_page

        start_index = (current_page - 1) * page_size
        end_index = min(start_index + page_size, total_entries)
        page_df = entries_df.iloc[start_index:end_index] if total_entries else entries_df

        with st.container(border=True, key="entries_history_card"):
            st.markdown(
                (
                    "<div class='entries-history-head'>"
                    "<span>Historique des entrees</span>"
                    "<span>Voir tout</span>"
                    "</div>"
                ),
                unsafe_allow_html=True,
            )
            st.markdown(_build_entries_table_html(page_df), unsafe_allow_html=True)

            footer_cols = st.columns([5, 0.45, 0.45], vertical_alignment="center")
            footer_cols[0].markdown(
                (
                    "<div class='entries-history-count'>"
                    f"Affichage de {start_index + 1 if total_entries else 0} a {end_index} "
                    f"sur {total_entries} resultats"
                    "</div>"
                ),
                unsafe_allow_html=True,
            )

            prev_clicked = footer_cols[1].button(
                "‹",
                key="entries_hist_prev",
                width="stretch",
                disabled=current_page <= 1,
            )
            next_clicked = footer_cols[2].button(
                "›",
                key="entries_hist_next",
                width="stretch",
                disabled=current_page >= total_pages,
            )

            if prev_clicked:
                st.session_state[page_key] = current_page - 1
                st.rerun()
            if next_clicked:
                st.session_state[page_key] = current_page + 1
                st.rerun()

    if submitted:
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
