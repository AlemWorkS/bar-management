"""
Page "Rapports": vue analytique de la periode.

Interaction:
- consomme les agregations de data_access.py (totaux ventes/charges),
- execute aussi 2 requetes SQL analytiques via fetch_df() pour les tableaux,
- reutilise ui.py pour titre, format monetaire et affichage dataframe.
"""

from datetime import date
from decimal import Decimal

import streamlit as st

from data_access import fetch_df, get_charge_total, get_sales_totals
from ui import fmt_fcfa, render_page_title, show_dataframe


def render_reports():
    """Rend les KPI de periode + les agragations par jour et par mois."""
    render_page_title("Rapports", "Synthese des ventes et marges")

    # Filtre principal de la page.
    start_date, end_date = st.date_input(
        "Periode", value=(date.today().replace(day=1), date.today())
    )

    # KPI de haut de page.
    totals = get_sales_totals(start_date, end_date)
    total_ventes = totals["total_ventes"] if totals else 0
    marge = totals["marge"] if totals else 0
    total_charges = get_charge_total(start_date, end_date)
    net = Decimal(str(marge)) - Decimal(str(total_charges))

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total ventes", fmt_fcfa(total_ventes))
    col2.metric("Marge", fmt_fcfa(marge))
    col3.metric("Charges", fmt_fcfa(total_charges))
    col4.metric("Net", fmt_fcfa(net))

    # Serie temporelle journaliere.
    st.subheader("Ventes par jour")
    daily_df = fetch_df(
        """
        SELECT v.date_vente,
               SUM(v.montant) AS total_ventes,
               SUM(v.montant - (COALESCE(p.prix_achat, 0) * v.quantite)) AS marge
        FROM vente v
        LEFT JOIN produit p ON v.id_produit = p.id_produit
        WHERE v.date_vente BETWEEN %s AND %s
        GROUP BY v.date_vente
        ORDER BY v.date_vente
        """,
        (start_date, end_date),
    )
    show_dataframe(daily_df, "Aucune vente sur la periode")

    # Serie temporelle mensuelle.
    st.subheader("Ventes par mois")
    monthly_df = fetch_df(
        """
        SELECT DATE_FORMAT(v.date_vente, '%Y-%m') AS mois,
               SUM(v.montant) AS total_ventes,
               SUM(v.montant - (COALESCE(p.prix_achat, 0) * v.quantite)) AS marge
        FROM vente v
        LEFT JOIN produit p ON v.id_produit = p.id_produit
        WHERE v.date_vente BETWEEN %s AND %s
        GROUP BY DATE_FORMAT(v.date_vente, '%Y-%m')
        ORDER BY mois
        """,
        (start_date, end_date),
    )
    show_dataframe(monthly_df, "Aucune vente sur la periode")

