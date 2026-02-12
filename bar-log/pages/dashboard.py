"""
Page "Tableau de bord".

Interaction:
- Appelee depuis streamlit_app.py via le mapping PAGES.
- Lit les KPI et listes via data_access.py.
- Reutilise les composants d'affichage communs de ui.py.
"""

from datetime import date
from decimal import Decimal
from html import escape
from textwrap import dedent

import streamlit as st

from data_access import get_charge_total, get_sales_totals, list_low_stock
from ui import fmt_fcfa, render_page_title


def _dashboard_category_class(category_name):
    """Retourne la classe CSS de badge selon la categorie."""
    name = (category_name or "").lower()
    if "liqueur" in name:
        return "dashboard-pill-blue"
    if "boisson" in name or "sucrerie" in name or "soft" in name:
        return "dashboard-pill-green"
    if "vin" in name:
        return "dashboard-pill-red"
    return "dashboard-pill-gray"


def _build_low_stock_table_html(low_stock_df):
    """Construit le tableau HTML de stock faible (style maquette)."""
    rows = low_stock_df.to_dict("records")
    body_rows = []

    if not rows:
        body_rows.append(
            "<tr><td colspan='4' class='dashboard-low-stock-empty'>Aucun produit sous le seuil</td></tr>"
        )
    else:
        for row in rows:
            product_id = escape(str(row.get("id_produit") or "-"))
            product_name = escape(str(row.get("nom_produit") or "-"))
            category = str(row.get("categorie") or "Sans categorie")
            stock = escape(str(row.get("stock_actuel") or 0))
            category_safe = escape(category)
            badge_class = _dashboard_category_class(category)

            body_rows.append(
                dedent(
                    f"""
                    <tr>
                      <td class="dashboard-low-stock-id">{product_id}</td>
                      <td>{product_name}</td>
                      <td><span class="dashboard-pill {badge_class}">{category_safe}</span></td>
                      <td class="dashboard-low-stock-value">{stock}</td>
                    </tr>
                    """
                ).strip()
            )

    return dedent(
        f"""
        <div class="dashboard-low-stock-wrap">
          <table class="dashboard-low-stock-table">
            <thead>
              <tr>
                <th>ID_PRODUIT</th>
                <th>NOM_PRODUIT</th>
                <th>CATEGORIE</th>
                <th class="dashboard-low-stock-right">STOCK_ACTUEL</th>
              </tr>
            </thead>
            <tbody>
              {''.join(body_rows)}
            </tbody>
          </table>
          <div class="dashboard-low-stock-foot">
            Affichage des produits dont le stock est inferieur au seuil defini.
          </div>
        </div>
        """
    ).strip()


def render_dashboard():
    """
    Rend la vue synthese du jour:
    - KPI ventes/marge/net,
    - tableau des produits en stock faible.
    """
    render_page_title("Tableau de bord", "Vue globale du jour")
    today = date.today()

    # Lecture des donnees de la journee depuis la couche SQL.
    totals = get_sales_totals(today, today)
    total_ventes = totals["total_ventes"] if totals else 0
    marge = totals["marge"] if totals else 0
    total_charges = get_charge_total(today, today)
    net = Decimal(str(marge)) - Decimal(str(total_charges))

    # Affichage des KPI financiers.
    col1, col2, col4 = st.columns(3)
    col1.metric("Ventes du jour", fmt_fcfa(total_ventes))
    col2.metric("Marge du jour", fmt_fcfa(marge))
    col4.metric("Net du jour", fmt_fcfa(net))

    # Monitoring stock: un seuil utilisateur pilote la requete list_low_stock().
    st.subheader("Stock faible")
    with st.container(border=True, key="dashboard_low_stock_card"):
        threshold = st.number_input(
            "Seuil stock faible",
            min_value=0,
            value=5,
            step=1,
            width="stretch",
        )
        low_stock_df = list_low_stock(threshold)
        st.markdown(_build_low_stock_table_html(low_stock_df), unsafe_allow_html=True)
