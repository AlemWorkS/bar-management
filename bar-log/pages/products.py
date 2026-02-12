"""
Page "Produits": CRUD sur le catalogue.

Interaction:
- streamlit_app.py selectionne cette page via le menu sidebar.
- data_access.py fournit list/create/update/delete produit/categorie.
- ui.py fournit les helpers visuels et de mapping utilises ici.
"""

import math
from decimal import Decimal
from html import escape
from textwrap import dedent

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
)


def _to_decimal(value):
    """Convertit une valeur numerique en Decimal de maniere robuste."""
    try:
        return Decimal(str(value))
    except Exception:
        return Decimal("0")


def _fmt_int(value):
    """Formate un montant en entier avec separateur espace."""
    number = int(_to_decimal(value).quantize(Decimal("1")))
    return f"{number:,}".replace(",", " ")


def _product_category_class(category_name):
    """Retourne la classe CSS de badge selon la categorie."""
    name = (category_name or "").lower()
    if "whisky" in name:
        return "products-pill-yellow"
    if "vin" in name:
        return "products-pill-red"
    if "liqueur" in name:
        return "products-pill-blue"
    if "sirop" in name or "boisson" in name or "soft" in name:
        return "products-pill-green"
    if "sucrerie" in name:
        return "products-pill-pink"
    return "products-pill-gray"


def _stock_class(stock_value):
    """Retourne la classe CSS de couleur de stock."""
    try:
        stock = int(stock_value)
    except Exception:
        stock = 0
    if stock <= 0:
        return "products-stock-red"
    if stock <= 10:
        return "products-stock-amber"
    return "products-stock-green"


def _fmt_product_id(raw_id):
    """Normalise l'ID produit au format de la maquette (PR000001)."""
    value = str(raw_id or "").strip()
    if not value:
        return "-"
    if value.upper().startswith("PR"):
        return value.upper()
    if value.isdigit():
        return f"PR{int(value):06d}"
    return value


def _build_products_list_html(products_df):
    """Construit le HTML du tableau liste des produits."""
    rows_html = []
    for row in products_df.to_dict("records"):
        product_id = escape(_fmt_product_id(row.get("id_produit")))
        product_name = escape(str(row.get("nom_produit") or "-"))
        category = str(row.get("categorie") or "Sans categorie")
        category_safe = escape(category)
        category_class = _product_category_class(category)
        prix_achat = escape(_fmt_int(row.get("prix_achat")))
        prix_btl = escape(_fmt_int(row.get("prix_vente_bouteille")))
        prix_verre = escape(_fmt_int(row.get("prix_vente_verre")))
        stock_raw = row.get("stock_actuel") or 0
        stock_safe = escape(str(stock_raw))
        stock_class = _stock_class(stock_raw)
        unite = escape(str(row.get("unite_vente") or "-"))

        rows_html.append(
            dedent(
                f"""
                <tr>
                  <td class="products-col-id">{product_id}</td>
                  <td class="products-col-name">{product_name}</td>
                  <td><span class="products-pill {category_class}">{category_safe}</span></td>
                  <td class="products-col-number">{prix_achat}</td>
                  <td class="products-col-number">{prix_btl}</td>
                  <td class="products-col-number">{prix_verre}</td>
                  <td class="products-col-stock {stock_class}">{stock_safe}</td>
                  <td class="products-col-unit">{unite}</td>
                </tr>
                """
            ).strip()
        )

    if not rows_html:
        rows_html.append(
            "<tr><td colspan='8' class='products-list-empty'>Aucun produit</td></tr>"
        )

    return dedent(
        f"""
        <div class="products-list-card">
          <table class="products-list-table">
            <thead>
              <tr>
                <th>ID<br>PRODUIT</th>
                <th>PRODUIT</th>
                <th>CATEGORIE</th>
                <th>PRIX<br>ACHAT</th>
                <th>PRIX<br>VENTE BTL</th>
                <th>PRIX<br>VENTE VERRE</th>
                <th>STOCK<br>ACTUEL</th>
                <th>UNITE</th>
              </tr>
            </thead>
            <tbody>
              {''.join(rows_html)}
            </tbody>
          </table>
        </div>
        """
    ).strip()


def _stock_bar_width(stock_value):
    """Retourne une largeur de barre (0-100) pour visualiser le stock."""
    try:
        stock = max(0, int(stock_value))
    except Exception:
        stock = 0
    return min(100, int((stock / 30) * 100)) if stock > 0 else 0


def _build_products_edit_html(
    products_df, selected_id=None, target_tab="Modifier", query_key="edit_product"
):
    """Construit le HTML du tableau de selection pour les onglets action (Modifier/Supprimer)."""

    def row_cell_button(product_id, inner_html):
        safe_id = escape(str(product_id), quote=True)
        safe_tab = escape(str(target_tab), quote=True)
        safe_query_key = escape(str(query_key), quote=True)
        return (
            "<form method='get' class='products-edit-row-form'>"
            f"<input type='hidden' name='products_tab' value='{safe_tab}'/>"
            f"<input type='hidden' name='{safe_query_key}' value='{safe_id}'/>"
            f"<button type='submit' class='products-edit-row-link'>{inner_html}</button>"
            "</form>"
        )

    rows_html = []
    selected_id_text = str(selected_id) if selected_id is not None else ""

    for row in products_df.to_dict("records"):
        product_id_raw = row.get("id_produit")
        product_id_text = str(product_id_raw)
        is_selected = product_id_text == selected_id_text
        radio_class = (
            "products-edit-radio products-edit-radio-selected"
            if is_selected
            else "products-edit-radio"
        )

        product_id = escape(_fmt_product_id(product_id_raw))
        product_name = escape(str(row.get("nom_produit") or "-"))
        category = str(row.get("categorie") or "Sans categorie")
        category_safe = escape(category)
        category_class = _product_category_class(category)
        prix_achat = escape(_fmt_int(row.get("prix_achat")))
        unite = str(row.get("unite_vente") or "bouteille").lower()
        if unite == "verre":
            prix_vente_value = row.get("prix_vente_verre")
        else:
            prix_vente_value = row.get("prix_vente_bouteille")
        prix_vente = escape(_fmt_int(prix_vente_value))
        stock_raw = row.get("stock_actuel") or 0
        stock_safe = escape(str(stock_raw))
        stock_class = _stock_class(stock_raw)
        stock_width = _stock_bar_width(stock_raw)
        unite_safe = escape(unite)
        radio_html = f'<span class="{radio_class}"></span>'
        category_html = f'<span class="products-pill {category_class}">{category_safe}</span>'
        stock_html = (
            '<div class="products-edit-stock-wrap">'
            f'<span class="products-edit-stock-num {stock_class}">{stock_safe}</span>'
            '<div class="products-edit-stock-track">'
            f'<div class="products-edit-stock-fill {stock_class}" style="width:{stock_width}%"></div>'
            "</div>"
            "</div>"
        )

        rows_html.append(
            dedent(
                f"""
                <tr>
                  <td class="products-edit-radio-col">{row_cell_button(product_id_text, radio_html)}</td>
                  <td class="products-edit-id">{row_cell_button(product_id_text, product_id)}</td>
                  <td class="products-edit-name">{row_cell_button(product_id_text, product_name)}</td>
                  <td>{row_cell_button(product_id_text, category_html)}</td>
                  <td class="products-edit-number">{row_cell_button(product_id_text, prix_achat)}</td>
                  <td class="products-edit-number">{row_cell_button(product_id_text, prix_vente)}</td>
                  <td>{row_cell_button(product_id_text, stock_html)}</td>
                  <td class="products-col-unit">{row_cell_button(product_id_text, unite_safe)}</td>
                </tr>
                """
            ).strip()
        )

    if not rows_html:
        rows_html.append(
            "<tr><td colspan='8' class='products-list-empty'>Aucun produit</td></tr>"
        )

    return dedent(
        f"""
        <div class="products-edit-card">
          <table class="products-edit-table">
            <thead>
              <tr>
                <th></th>
                <th>ID Produit</th>
                <th>Produit</th>
                <th>Categorie</th>
                <th>Prix Achat</th>
                <th>Prix Vente</th>
                <th>Stock</th>
                <th>Unite</th>
              </tr>
            </thead>
            <tbody>
              {''.join(rows_html)}
            </tbody>
          </table>
        </div>
        """
    ).strip()


def _sync_edit_price_from_unit():
    """Aligne le champ prix de vente visible avec l'unite choisie."""
    unit = str(st.session_state.get("edit_unite_vente") or "bouteille").lower()
    if unit == "verre":
        st.session_state["edit_prix_vente"] = float(st.session_state.get("edit_prix_vente_verre", 0.0))
    else:
        st.session_state["edit_prix_vente"] = float(
            st.session_state.get("edit_prix_vente_bouteille", 0.0)
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

    tabs_labels = ["Liste", "Ajouter", "Modifier", "Supprimer"]
    query_tab = st.query_params.get("products_tab")
    if isinstance(query_tab, list):
        query_tab = query_tab[0] if query_tab else None
    query_tab = str(query_tab).strip() if query_tab is not None else None

    query_edit = st.query_params.get("edit_product")
    if isinstance(query_edit, list):
        query_edit = query_edit[0] if query_edit else None
    query_edit = str(query_edit).strip() if query_edit is not None else None

    query_delete = st.query_params.get("delete_product")
    if isinstance(query_delete, list):
        query_delete = query_delete[0] if query_delete else None
    query_delete = str(query_delete).strip() if query_delete is not None else None

    default_tab = "Liste"
    if query_edit:
        default_tab = "Modifier"
    if query_delete:
        default_tab = "Supprimer"
    if query_tab in tabs_labels:
        default_tab = query_tab

    tab_list, tab_add, tab_edit, tab_delete = st.tabs(tabs_labels, default=default_tab)

    with tab_list:
        page_size = 6
        total_products = len(products_df)
        total_pages = max(1, math.ceil(total_products / page_size))
        page_key = "products_list_page"

        current_page = st.session_state.get(page_key, 1)
        if current_page < 1:
            current_page = 1
        if current_page > total_pages:
            current_page = total_pages
        st.session_state[page_key] = current_page

        start_index = (current_page - 1) * page_size
        end_index = min(start_index + page_size, total_products)
        page_df = products_df.iloc[start_index:end_index] if total_products else products_df

        st.markdown(_build_products_list_html(page_df), unsafe_allow_html=True)

        with st.container(key="products_list_footer"):
            left_col, prev_col, next_col = st.columns([5, 1, 1], vertical_alignment="center")
            left_col.markdown(
                (
                    "<div class='products-list-foot-text'>"
                    f"Affichage de {start_index + 1 if total_products else 0} a {end_index} "
                    f"sur {total_products} produits"
                    "</div>"
                ),
                unsafe_allow_html=True,
            )

            if prev_col.button(
                "Precedent",
                key="products_list_prev",
                width="stretch",
                disabled=current_page <= 1,
            ):
                st.session_state[page_key] = current_page - 1
                st.rerun()

            if next_col.button(
                "Suivant",
                key="products_list_next",
                width="stretch",
                disabled=current_page >= total_pages,
            ):
                st.session_state[page_key] = current_page + 1
                st.rerun()

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
                nom = st.text_input("Nom du produit", placeholder="Ex: Vin Rouge Bordeaux")
                categorie_key = st.selectbox("Categorie", category_keys)
                col_left, col_right = st.columns(2)
                prix_achat = col_left.number_input(
                    "Prix d'achat",
                    min_value=0.0,
                    value=0.0,
                    step=0.01,
                    format="%.2f",
                )
                prix_vente = col_right.number_input(
                    "Prix de vente",
                    min_value=0.0,
                    value=0.0,
                    step=0.01,
                    format="%.2f",
                )
                col_left, col_right = st.columns(2)
                stock_initial = col_left.number_input(
                    "Stock initial",
                    min_value=0,
                    value=0,
                    step=1,
                )
                unite_vente = col_right.selectbox("Unite", ["bouteille", "verre"])
                quantite_ml = st.number_input(
                    "Quantité contenu en mL", min_value=10, step=1
                ) # Declarer la quantité contenu dans la bouteille
                submitted = st.form_submit_button("Ajouter")

        # Traitement submit + validation metier.
        if submitted:
            if categories_df.empty:
                st.error("Aucune categorie stockable disponible")
            elif not nom:
                st.error("Nom du produit requis")
            else:
                category = category_map[categorie_key]
                prix_vente_bouteille = prix_vente if unite_vente == "bouteille" else 0
                prix_vente_verre = prix_vente if unite_vente == "verre" else 0
                create_product(
                    nom,
                    category["id_categorie"],
                    prix_achat=prix_achat,
                    prix_vente_bouteille=prix_vente_bouteille,
                    prix_vente_verre=prix_vente_verre,
                    stock_actuel=stock_initial,
                    unite_vente=unite_vente,
                    quantite_ml=quantite_ml
                )
                st.session_state["product_added"] = True
                st.rerun()

    with tab_edit:
        if products_df.empty or categories_df.empty:
            st.info("Aucun produit a modifier")
        else:
            if st.session_state.get("product_updated"):
                st.success("Produit modifie")
                st.session_state["product_updated"] = False

            query_selected = st.query_params.get("edit_product")
            if isinstance(query_selected, list):
                query_selected = query_selected[0] if query_selected else None
            query_selected = str(query_selected).strip() if query_selected is not None else None

            selected_product = None
            selected_id = None
            if query_selected:
                for row in products_df.to_dict("records"):
                    raw_id = str(row.get("id_produit") or "").strip()
                    if not raw_id:
                        continue
                    if raw_id == query_selected or _fmt_product_id(raw_id) == query_selected.upper():
                        selected_product = row
                        selected_id = row["id_produit"]
                        break

            st.markdown(_build_products_edit_html(products_df, selected_id), unsafe_allow_html=True)

            if selected_product is not None and st.session_state.get("edit_loaded_id") != selected_id:
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
                st.session_state["edit_quantite_ml"] = selected_product[
                        "quantite_ml"
                    ]
                st.session_state["edit_categorie_id"] = selected_product["id_categorie"]
                _sync_edit_price_from_unit()

            if selected_product is None:
                st.session_state.pop("edit_loaded_id", None)
                st.session_state.pop("edit_prix_vente", None)

            if st.session_state.get("edit_loaded_id"):
                category_map = build_category_map(categories_df)
                category_keys = list(category_map.keys())
                default_cat_key = get_category_key(
                    category_map, st.session_state.get("edit_categorie_id")
                )
                if default_cat_key is None:
                    default_cat_key = category_keys[0]
                cat_index = category_keys.index(default_cat_key)

                with st.container(border=True, key="products_edit_form_card"):
                    with st.form("edit_product", border=False):
                        nom = st.text_input(
                            "Nom du produit",
                            key="edit_nom",
                            placeholder="Ex: Vin Rouge Bordeaux",
                            width="stretch",
                        )
                        categorie_key = st.selectbox(
                            "Categorie",
                            category_keys,
                            index=cat_index,
                            width="stretch",
                        )
                        col_left, col_right = st.columns(2, gap="large")
                        prix_achat = col_left.number_input(
                            "Prix d'achat",
                            min_value=0.0,
                            step=0.01,
                            key="edit_prix_achat",
                            width="stretch",
                        )
                        prix_vente = col_right.number_input(
                            "Prix de vente",
                            min_value=0.0,
                            step=0.01,
                            key="edit_prix_vente",
                            width="stretch",
                        )
                        col_left, col_right = st.columns(2, gap="large")
                        stock_actuel = col_left.number_input(
                            "Stock actuel",
                            min_value=0,
                            step=1,
                            key="edit_stock",
                            width="stretch",
                        )
                        unite_vente = col_right.selectbox(
                            "Unite",
                            ["bouteille", "verre"],
                            key="edit_unite_vente",
                            width="stretch",
                        )
                        quantite_ml = st.number_input(
                            "Quantité en mL",
                            min_value=0, step=1,
                            key="edit_quantite_ml",placeholder=0
                    )
                        submitted = st.form_submit_button(
                            "Mettre a jour",
                            key="edit_submit_btn",
                            width="content",
                        )

                if submitted:
                    if not nom:
                        st.error("Nom du produit requis")
                    else:
                        category = category_map[categorie_key]
                        if unite_vente == "verre":
                            prix_vente_verre = prix_vente
                            prix_vente_bouteille = float(
                                st.session_state.get("edit_prix_vente_bouteille", 0.0)
                            )
                        else:
                            prix_vente_bouteille = prix_vente
                            prix_vente_verre = float(
                                st.session_state.get("edit_prix_vente_verre", 0.0)
                            )

                        update_product(
                            st.session_state["edit_loaded_id"],
                            nom,
                            category["id_categorie"],
                            prix_achat,
                            prix_vente_bouteille,
                            prix_vente_verre,
                            stock_actuel,
                            unite_vente,
                            quantite_ml
                        )
                        st.session_state["product_updated"] = True
                        st.session_state.pop("edit_loaded_id", None)
                        st.session_state.pop("edit_prix_vente", None)
                        try:
                            st.query_params["products_tab"] = "Modifier"
                        except Exception:
                            pass
                        try:
                            del st.query_params["edit_product"]
                        except Exception:
                            pass
                        st.rerun()
            else:
                st.markdown(
                    (
                        "<div class='products-edit-info'>"
                        "<span class='material-symbols-outlined'>info</span>"
                        "<span>Selectionnez une ligne du tableau pour voir les details ou modifier un produit.</span>"
                        "</div>"
                    ),
                    unsafe_allow_html=True,
                )

    with tab_delete:
        if products_df.empty:
            st.info("Aucun produit a supprimer")
        else:
            if st.session_state.get("product_deleted"):
                st.success("Produit supprime")
                st.session_state["product_deleted"] = False

            query_selected = st.query_params.get("delete_product")
            if isinstance(query_selected, list):
                query_selected = query_selected[0] if query_selected else None
            query_selected = (
                str(query_selected).strip() if query_selected is not None else None
            )

            selected_product = None
            selected_id = None
            if query_selected:
                for row in products_df.to_dict("records"):
                    raw_id = str(row.get("id_produit") or "").strip()
                    if not raw_id:
                        continue
                    if raw_id == query_selected or _fmt_product_id(raw_id) == query_selected.upper():
                        selected_product = row
                        selected_id = row["id_produit"]
                        break

            st.markdown(
                _build_products_edit_html(
                    products_df,
                    selected_id=selected_id,
                    target_tab="Supprimer",
                    query_key="delete_product",
                ),
                unsafe_allow_html=True,
            )

            if selected_product is None:
                st.markdown(
                    (
                        "<div class='products-edit-info'>"
                        "<span class='material-symbols-outlined'>info</span>"
                        "<span>Selectionnez une ligne du tableau pour supprimer un produit.</span>"
                        "</div>"
                    ),
                    unsafe_allow_html=True,
                )
            else:
                product_name = escape(str(selected_product.get("nom_produit") or "-"))
                product_id = escape(_fmt_product_id(selected_product.get("id_produit")))
                st.markdown(
                    (
                        "<div class='products-delete-hint'>"
                        "<span class='material-symbols-outlined'>warning</span>"
                        f"<span>Produit selectionne: <strong>{product_name}</strong> ({product_id}). "
                        "Cette action est irreversible.</span>"
                        "</div>"
                    ),
                    unsafe_allow_html=True,
                )
                confirm = st.checkbox(
                    "Confirmer la suppression du produit selectionne",
                    key=f"delete_confirm_{selected_id}",
                )
                if st.button("Supprimer le produit", key="delete_product_button"):
                    if not confirm:
                        st.warning("Cochez la confirmation avant de supprimer.")
                    else:
                        try:
                            delete_product(selected_product["id_produit"])
                            st.session_state["product_deleted"] = True
                            st.query_params["products_tab"] = "Supprimer"
                            try:
                                del st.query_params["delete_product"]
                            except Exception:
                                pass
                            st.rerun()
                        except Exception as exc:
                            # Ex: contraintes SQL si references existantes.
                            st.error(f"Suppression impossible: {exc}")
