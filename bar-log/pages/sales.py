"""
Page "Ventes": saisie des ventes et historique.

Interaction:
- lit les produits/categories via data_access.py,
- ajoute des lignes de vente dans une liste temporaire (session_state),
- persiste les lignes en base via create_receipt() + add_sale_stockable(),
- affiche un tableau historique personnalise (HTML/CSS) proche de la maquette.
"""

from datetime import date
from decimal import Decimal
from html import escape
from textwrap import dedent

import streamlit as st

from data_access import add_sale_stockable, create_receipt, list_categories, list_products, list_sales
from ui import build_category_map, build_product_map, fmt_fcfa


def _to_decimal(value):
    """Convertit une valeur en Decimal avec fallback robuste."""
    try:
        return Decimal(str(value))
    except Exception:
        return Decimal("0")


def _fmt_fcfa_compact(value):
    """Format monetaire compact (sans decimales) pour le tableau historique."""
    number = int(_to_decimal(value).quantize(Decimal("1")))
    return f"{number:,}".replace(",", " ") + " FCFA"


def _fmt_signed_fcfa(value):
    """Format monetaire avec signe explicite pour la marge."""
    number = int(_to_decimal(value).quantize(Decimal("1")))
    prefix = "+" if number > 0 else ""
    return f"{prefix}{number:,}".replace(",", " ") + " FCFA"


def _category_color_class(category_name):
    """Retourne une classe CSS de badge selon la categorie."""
    name = (category_name or "").lower()
    if "liqueur" in name:
        return "sales-pill-blue"
    if "sirop" in name:
        return "sales-pill-green"
    if "sucrerie" in name:
        return "sales-pill-yellow"
    if "vin" in name:
        return "sales-pill-red"
    if "whisky" in name:
        return "sales-pill-purple"
    return "sales-pill-gray"


def _icon_for_sale(type_vente):
    """Retourne une icone produit selon le type de vente."""
    if (type_vente or "").lower() == "verre":
        return "wine_bar", "sales-icon-red"
    return "local_bar", "sales-icon-orange"


def _build_history_table_html(sales_df):
    """
    Construit le HTML du tableau historique.

    Le rendu HTML permet un style proche de la maquette (icones, badges, couleurs).
    """
    rows_html = []
    total_montant = Decimal("0")
    total_marge = Decimal("0")
    records = sales_df.to_dict("records")

    for row in records:
        montant = _to_decimal(row.get("montant"))
        marge = _to_decimal(row.get("marge"))
        total_montant += montant
        total_marge += marge

        article = escape(str(row.get("article") or "-"))
        categorie = str(row.get("categorie") or "Sans categorie")
        categorie_safe = escape(categorie)
        badge_class = _category_color_class(categorie)

        id_value = row.get("id_produit") or row.get("id_vente") or "-"
        id_text = escape(str(id_value))
        date_text = escape(str(row.get("date_vente") or ""))
        qty_text = escape(str(row.get("quantite") or 0))
        type_vente = str(row.get("type_vente") or "")
        type_text = escape(type_vente.title() if type_vente else "-")
        montant_text = escape(_fmt_fcfa_compact(montant))
        marge_text = escape(_fmt_signed_fcfa(marge))

        icon_name, icon_color_class = _icon_for_sale(type_vente)
        marge_class = "sales-marge-positive" if marge >= 0 else "sales-marge-negative"

        rows_html.append(
            dedent(
                f"""
                <tr>
                  <td class="sales-col-date">{date_text}</td>
                  <td>
                    <div class="sales-product-cell">
                      <div class="sales-product-icon {icon_color_class}">
                        <span class="material-symbols-outlined">{icon_name}</span>
                      </div>
                      <div>
                        <div class="sales-product-name">{article}</div>
                        <div class="sales-product-sub">ID: {id_text}</div>
                      </div>
                    </div>
                  </td>
                  <td><span class="sales-pill {badge_class}">{categorie_safe}</span></td>
                  <td class="sales-col-center">{qty_text}</td>
                  <td>{type_text}</td>
                  <td class="sales-col-right">{montant_text}</td>
                  <td class="sales-col-right {marge_class}">{marge_text}</td>
                </tr>
                """
            ).strip()
        )

    total_marge_class = "sales-marge-positive" if total_marge >= 0 else "sales-marge-negative"
    count_text = f"Affichage de 1 a {len(records)} sur {len(records)} resultats"

    return dedent(
        f"""
        <div class="sales-history-card">
          <div class="sales-history-scroll">
            <table class="sales-history-table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Produit</th>
                  <th>Categorie</th>
                  <th class="sales-col-center">Qte</th>
                  <th>Type</th>
                  <th class="sales-col-right">Montant</th>
                  <th class="sales-col-right">Marge</th>
                </tr>
              </thead>
              <tbody>
                {''.join(rows_html)}
              </tbody>
              <tfoot>
                <tr>
                  <td colspan="5" class="sales-col-right">Total journee:</td>
                  <td class="sales-col-right">{escape(_fmt_fcfa_compact(total_montant))}</td>
                  <td class="sales-col-right {total_marge_class}">{escape(_fmt_signed_fcfa(total_marge))}</td>
                </tr>
              </tfoot>
            </table>
          </div>
          <div class="sales-history-footer">{escape(count_text)}</div>
        </div>
        """
    ).strip()


def render_sales():
    """Rend la page ventes (saisie + historique)."""
    st.markdown("<div class='sales-page-title'>Ventes du jour</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='sales-muted'>Enregistrez les sorties de stock et suivez les ventes quotidiennes.</div>",
        unsafe_allow_html=True,
    )

    products_df = list_products()
    categories_df = list_categories()
    all_sales_df = list_sales()
    if categories_df.empty:
        st.info("Ajoutez des categories avant de saisir une vente")
        return

    if "receipt_items" not in st.session_state:
        st.session_state["receipt_items"] = []
    if "sale_quantite_text" not in st.session_state:
        st.session_state["sale_quantite_text"] = "1"

    if st.session_state.get("sale_reset"):
        st.session_state["sale_product"] = None
        st.session_state["sale_quantite_text"] = "1"
        st.session_state["sale_unit_price"] = 0.0
        st.session_state["sale_unite"] = "bouteille"
        st.session_state["sale_unite_display"] = "bouteille"
        st.session_state["sale_reset"] = False

    product_map = build_product_map(products_df) if not products_df.empty else {}

    selected_product = None
    selected_key = None
    prix_unitaire = st.session_state.get("sale_unit_price", 0.0)
    quantite = 1
    unite_vente = st.session_state.get("sale_unite", "bouteille")

    entry_col_sizes = [1.25, 2.6, 1.0, 1.0, 1.2, 0.35]

    with st.container(border=True, key="sales_entry_form"):
        label_cols = st.columns(entry_col_sizes, gap="small")
        labels = ["Date", "Produit", "Quantite", "Unite", "Prix vente (FCFA)"]
        for index, label_text in enumerate(labels):
            label_cols[index].markdown(
                f"<div class='sales-entry-label'>{label_text}</div>",
                unsafe_allow_html=True,
            )

        entry_cols = st.columns(entry_col_sizes, gap="small", vertical_alignment="center")
        with entry_cols[0]:
            sale_day = st.date_input(
                "Date",
                value=date.today(),
                key="sale_day",
                label_visibility="collapsed",
                width="stretch",
            )
        with entry_cols[1]:
            if products_df.empty:
                st.selectbox(
                    "Produit",
                    ["Aucun produit disponible"],
                    index=0,
                    key="sale_product_empty",
                    disabled=True,
                    label_visibility="collapsed",
                    width="stretch",
                )
                selected_key = None
            else:
                selected_key = st.selectbox(
                    "Produit",
                    list(product_map.keys()),
                    index=None,
                    placeholder="Selectionner un produit",
                    key="sale_product",
                    label_visibility="collapsed",
                    width="stretch",
                )
        with entry_cols[2]:
            qty_text = st.text_input(
                "Quantite",
                key="sale_quantite_text",
                label_visibility="collapsed",
                width="stretch",
            )
            try:
                quantite = int(qty_text)
            except Exception:
                quantite = 0
            if quantite <= 0:
                quantite = 0

        if selected_key and selected_key in product_map:
            selected_product = product_map[selected_key]
            loaded_unite = str(selected_product.get("unite_vente") or "bouteille").lower()
            if loaded_unite not in {"bouteille", "verre"}:
                loaded_unite = "bouteille"
            price_col = "prix_vente_verre" if loaded_unite == "verre" else "prix_vente_bouteille"
            loaded_price = float(selected_product.get(price_col) or 0)
            unite_vente = loaded_unite
            prix_unitaire = loaded_price
            st.session_state["sale_unite"] = loaded_unite
            st.session_state["sale_unit_price"] = loaded_price
        else:
            st.session_state["sale_unit_price"] = 0.0
            prix_unitaire = 0.0

        with entry_cols[3]:
            st.session_state["sale_unite_display"] = unite_vente
            st.selectbox(
                "Unite",
                ["bouteille", "verre"],
                index=0 if unite_vente == "bouteille" else 1,
                key="sale_unite_display",
                disabled=True,
                label_visibility="collapsed",
                width="stretch",
            )
        with entry_cols[4]:
            st.text_input(
                "Prix vente (FCFA)",
                value=fmt_fcfa(prix_unitaire).replace(",", " "),
                disabled=True,
                label_visibility="collapsed",
                width="stretch",
            )
        with entry_cols[5]:
            add_clicked = st.button(
                " ",
                key="sale_add_btn",
                icon=":material/add:",
                use_container_width=True,
            )

    if products_df.empty:
        st.info("Ajoutez un produit avant de saisir une vente")

    if add_clicked:
        if products_df.empty:
            st.error("Aucun produit disponible")
        elif selected_product is None:
            st.error("Selectionnez un produit")
        elif quantite <= 0:
            st.error("La quantite doit etre un nombre entier superieur a 0")
        elif prix_unitaire <= 0:
            st.error("Prix de vente non defini pour ce produit")
        else:
            st.session_state["receipt_items"].append(
                {
                    "product_id": selected_product["id_produit"],
                    "quantite": quantite,
                    "date_vente": sale_day,
                    "unite_vente": unite_vente,
                }
            )
            st.session_state["sale_reset"] = True
            st.rerun()

    receipt_items = st.session_state["receipt_items"]
    product_lookup = {row["id_produit"]: row for row in products_df.to_dict("records")}
    draft_total = Decimal("0")
    draft_marge = Decimal("0")
    for item in receipt_items:
        product = product_lookup.get(item["product_id"])
        if not product:
            continue
        prix_achat = _to_decimal(product.get("prix_achat"))
        if item["unite_vente"] == "verre":
            prix_vente = _to_decimal(product.get("prix_vente_verre"))
        else:
            prix_vente = _to_decimal(product.get("prix_vente_bouteille"))
        qty = _to_decimal(item["quantite"])
        draft_total += prix_vente * qty
        draft_marge += (prix_vente - prix_achat) * qty

    summary_cols = st.columns([1.2, 1.2, 4], vertical_alignment="center")
    with summary_cols[0]:
        save_clicked = st.button(
            "Enregistrer",
            key="sale_save_btn",
            use_container_width=True,
            disabled=not receipt_items,
        )
    with summary_cols[1]:
        clear_clicked = st.button(
            "Vider",
            key="sale_clear_btn",
            use_container_width=True,
            disabled=not receipt_items,
        )
    with summary_cols[2]:
        if receipt_items:
            st.markdown(
                (
                    "<div class='sales-draft-summary'>"
                    f"{len(receipt_items)} ligne(s) en attente - "
                    f"Total: <strong>{fmt_fcfa(draft_total)}</strong> - "
                    f"Marge estimee: <strong>{fmt_fcfa(draft_marge)}</strong>"
                    "</div>"
                ),
                unsafe_allow_html=True,
            )

    if clear_clicked:
        st.session_state["receipt_items"] = []
        st.rerun()

    if save_clicked:
        try:
            receipt_id = create_receipt()
            for item in st.session_state["receipt_items"]:
                add_sale_stockable(
                    item["product_id"],
                    item["quantite"],
                    item["date_vente"],
                    item["unite_vente"],
                    receipt_id,
                )
        except Exception as exc:
            st.error(f"Enregistrement impossible: {exc}")
        else:
            st.session_state["receipt_items"] = []
            st.session_state["sale_reset"] = True
            st.success("Ventes enregistrees")
            st.rerun()

    st.markdown(
        (
            "<div class='sales-history-head'>"
            "<span class='material-symbols-outlined'>history</span>"
            "<span>Historique</span>"
            "</div>"
        ),
        unsafe_allow_html=True,
    )

    category_map = build_category_map(categories_df)
    default_start = date.today().replace(day=1)
    default_end = date.today()
    if not all_sales_df.empty and "date_vente" in all_sales_df.columns:
        default_start_value = all_sales_df["date_vente"].min()
        default_end_value = all_sales_df["date_vente"].max()
        default_start = (
            default_start_value.date()
            if hasattr(default_start_value, "date")
            else default_start_value
        )
        default_end = (
            default_end_value.date()
            if hasattr(default_end_value, "date")
            else default_end_value
        )

    filter_cols = st.columns([1.4, 1.4, 1.8], vertical_alignment="bottom")
    start_date = filter_cols[0].date_input(
        "Periode debut",
        value=default_start,
        key="vente_start",
    )
    end_date = filter_cols[1].date_input("Periode fin", value=default_end, key="vente_end")
    category_filter = filter_cols[2].selectbox(
        "Categorie",
        ["Toutes categories"] + list(category_map.keys()),
        key="vente_category",
    )

    category_id = None
    if category_filter != "Toutes categories":
        category_id = category_map[category_filter]["id_categorie"]

    sales_df = list_sales(start_date, end_date, None, category_id)
    if sales_df.empty:
        st.info("Aucune vente sur la periode")
        return

    st.markdown(_build_history_table_html(sales_df), unsafe_allow_html=True)
