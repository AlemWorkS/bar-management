"""
Page "Tableau de bord".

Interaction:
- Appelee depuis streamlit_app.py via le mapping PAGES.
- Lit les KPI et listes via data_access.py.
- Reutilise les composants d'affichage communs de ui.py.
"""

from datetime import date
from decimal import Decimal

import streamlit as st

from data_access import get_charge_total, get_sales_totals, list_low_stock
from ui import fmt_fcfa, render_page_title, show_dataframe


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
    threshold = st.number_input("Seuil stock faible", min_value=0, value=5, step=1)
    low_stock_df = list_low_stock(threshold)
    show_dataframe(low_stock_df, "Aucun produit sous le seuil")
