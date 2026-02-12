from datetime import date, datetime
from decimal import Decimal

import pandas as pd
import streamlit as st

from db import db_cursor

st.set_page_config(page_title="Gestion Stock Bar", layout="wide")


# --- Theme (entete, sidebar, main, footer) ---
def apply_theme():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&family=Space+Grotesk:wght@500;600&display=swap');

        /* Base globale */
        :root {
          --bg: #f4f6fb;
          --card: #ffffff;
          --border: #e5e7ef;
          --text: #1b1f2a;
          --muted: #7b8397;
          --accent: #ff7a00;
          --accent-soft: #fff1e6;
        }

        html, body, [class*="stApp"] {
          background: var(--bg);
          color: var(--text);
          font-family: "DM Sans", sans-serif;
        }

        /* Entete (titres de page) */
        h1, h2, h3, h4, h5, h6, .page-title {
          font-family: "Space Grotesk", sans-serif;
          color: var(--text);
        }

        .page-title {
          font-size: 28px;
          font-weight: 600;
          margin: 0 0 4px 0;
        }

        .page-subtitle {
          color: var(--muted);
          font-size: 13px;
          margin-bottom: 16px;
          margin-top: 16px;
        }

        /* Main (contenu central) */
        div.block-container {
          padding-top: 56px;
          padding-bottom: 28px;
        }

        /* Inputs desactives lisibles */
        input:disabled,
        textarea:disabled,
        select:disabled,
        [data-testid="stNumberInput"] input:disabled,
        [data-testid="stTextInput"] input:disabled {
          color: var(--text) !important;
          -webkit-text-fill-color: var(--text) !important;
          opacity: 1 !important;
        }

        /* Sidebar */
        section[data-testid="stSidebar"] {
          background: #f1f3f8;
          border-right: 1px solid var(--border);
          color: var(--text);
        }

        /* Bouton de rappel de la sidebar */
        button[data-testid="collapsedControl"] {
          background: transparent !important;
          border: none !important;
          box-shadow: none !important;
          opacity: 1 !important;
          visibility: visible !important;
        }

        button[data-testid="collapsedControl"] svg {
          color: var(--text) !important;
          opacity: 1 !important;
        }

        button[data-testid="collapsedControl"]:hover,
        button[data-testid="collapsedControl"]:active,
        button[data-testid="collapsedControl"]:focus {
          background: #111827;
          border-color: #111827;
        }

        div[data-testid="stSidebarCollapsedControl"] {
          opacity: 1 !important;
          visibility: visible !important;
          pointer-events: auto !important;
        }

        /* Bouton de repli de la sidebar (toujours visible) */
        section[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] {
          display: inline-flex !important;
          opacity: 1 !important;
          visibility: visible !important;
          pointer-events: auto !important;
        }

        section[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] button {
          background: transparent !important;
          border: none !important;
          opacity: 1 !important;
          visibility: visible !important;
        }

        section[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] svg {
          color: var(--text) !important;
          opacity: 1 !important;
          visibility: visible !important;
        }

        /* Header Streamlit toujours visible (evite le masquage au survol) */
        header,
        div[data-testid="stHeader"] {
          opacity: 1 !important;
          visibility: visible !important;
          pointer-events: auto !important;
          transform: none !important;
        }

        div[data-testid="stToolbar"] {
          display: flex !important;
          opacity: 1 !important;
          visibility: visible !important;
          pointer-events: auto !important;
          transform: none !important;
        }

        header.stAppHeader,
        div[data-testid="stHeader"] {
          background: transparent !important;
          color: var(--text) !important;
        }

        header div[data-testid="stSidebarCollapsedControl"] {
          display: flex !important;
          opacity: 1 !important;
          visibility: visible !important;
          pointer-events: auto !important;
          transform: none !important;
          z-index: 1000;
        }

        header div[data-testid="stSidebarCollapsedControl"] button {
          display: flex !important;
          opacity: 1 !important;
          visibility: visible !important;
          background: transparent !important;
          border: none !important;
        }

        header div[data-testid="stSidebarCollapsedControl"] svg {
          color: var(--text) !important;
          fill: var(--text) !important;
          stroke: var(--text) !important;
        }

        div[data-testid="stHeader"] [data-testid="stSidebarCollapsedControl"] {
          display: flex !important;
          opacity: 1 !important;
          visibility: visible !important;
          pointer-events: auto !important;
          transform: none !important;
          z-index: 1000;
        }

        div[data-testid="stHeader"] [data-testid="stSidebarCollapsedControl"] button {
          display: flex !important;
          opacity: 1 !important;
          visibility: visible !important;
          background: transparent !important;
          border: none !important;
        }

        div[data-testid="stHeader"] [data-testid="stSidebarCollapsedControl"] svg {
          color: var(--text) !important;
          fill: var(--text) !important;
          stroke: var(--text) !important;
        }

        button[data-testid="stSidebarToggleButton"],
        [data-testid="stSidebarToggleButton"] {
          display: flex !important;
          opacity: 1 !important;
          visibility: visible !important;
          background: transparent !important;
          border: none !important;
          box-shadow: none !important;
        }

        button[data-testid="stSidebarToggleButton"] svg,
        [data-testid="stSidebarToggleButton"] svg {
          color: var(--text) !important;
          fill: var(--text) !important;
          stroke: var(--text) !important;
        }

        button[data-testid="stExpandSidebarButton"] {
          display: inline-flex !important;
          opacity: 1 !important;
          visibility: visible !important;
          background: transparent !important;
          border: none !important;
          box-shadow: none !important;
        }

        button[data-testid="stExpandSidebarButton"] span,
        button[data-testid="stExpandSidebarButton"] svg {
          color: var(--text) !important;
          fill: var(--text) !important;
          stroke: var(--text) !important;
          opacity: 1 !important;
        }

        button[title="Open sidebar"],
        button[title="Show sidebar"],
        button[aria-label="Open sidebar"],
        button[aria-label="Show sidebar"] {
          display: flex !important;
          opacity: 1 !important;
          visibility: visible !important;
          background: transparent !important;
          border: none !important;
          box-shadow: none !important;
        }

        button[title="Open sidebar"] svg,
        button[title="Show sidebar"] svg,
        button[aria-label="Open sidebar"] svg,
        button[aria-label="Show sidebar"] svg {
          color: var(--text) !important;
          fill: var(--text) !important;
          stroke: var(--text) !important;
        }

        .sidebar-brand {
          font-family: "Space Grotesk", sans-serif;
          font-size: 18px;
          font-weight: 600;
          padding: 8px 0 2px 0;
        }

        .sidebar-sub {
          color: var(--muted);
          font-size: 12px;
          margin-bottom: 16px;
        }

        .sidebar-section {
          color: var(--muted);
          font-size: 11px;
          text-transform: uppercase;
          letter-spacing: 0.06em;
          margin: 14px 0 6px 0;
        }

        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] span,
        section[data-testid="stSidebar"] p {
          color: var(--text);
        }

        section[data-testid="stSidebar"] input::placeholder {
          color: var(--muted);
        }

        section[data-testid="stSidebar"] .sidebar-sub,
        section[data-testid="stSidebar"] .sidebar-section {
          color: var(--muted);
        }

        section[data-testid="stSidebar"] div[role="radiogroup"] > label {
          background: transparent;
          border-radius: 10px;
          padding: 6px 8px;
          margin-bottom: 4px;
        }

        section[data-testid="stSidebar"] label[data-baseweb="radio"] > div {
          border-radius: 10px;
        }

        section[data-testid="stSidebar"] label[data-baseweb="radio"] input:checked + div {
          background: var(--accent-soft);
          border-left: 3px solid var(--accent);
        }

        /* Cartes / indicateurs */
        div[data-testid="stMetric"] {
          background: var(--card);
          border: 1px solid var(--border);
          border-radius: 14px;
          padding: 14px 16px;
          box-shadow: 0 1px 0 rgba(16, 24, 40, 0.04);
        }

        div[data-testid="stMetric"] label {
          color: var(--text);
        }

        div[data-testid="stMetric"] [data-testid="stMetricValue"] {
          font-size: 22px;
          font-weight: 600;
          color: var(--text);
        }

        div[data-testid="stDataFrame"],
        div[data-testid="stForm"] {
          background: var(--card);
          border: 1px solid var(--border);
          border-radius: 14px;
          padding: 8px;
        }

        div[data-testid="stDataFrame"] {
          padding: 10px;
        }

        /* Onglets */
        div[data-testid="stTabs"] button[role="tab"] {
          background: #ffffff;
          margin-top: 10px;
          border: 1px solid var(--border);
          border-radius: 10px;
          padding: 10px 16px;
          margin-right: 6px;
          color: var(--text);
          line-height: 1.3;
          height: auto;
          min-height: 38px;
          align-items: center;
          overflow: visible;
          display: inline-flex;
          justify-content: center;
        }

        div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
          background: var(--accent);
          color: #ffffff;
          border-color: var(--accent);
        }

        div[data-testid="stTabs"] {
          overflow: visible;
        }

        div[data-testid="stTabs"] [data-baseweb="tab-list"] {
          overflow: visible;
          padding-bottom: 2px;
        }

        /* Boutons */
        button[kind="primary"] {
          background: var(--accent);
          border-color: var(--accent);
          color: #ffffff;
          border-radius: 10px;
          padding: 6px 14px;
        }

        button[kind="primary"]:hover,
        button[kind="primary"]:active,
        button[kind="primary"]:focus {
          background: var(--accent);
          border-color: var(--accent);
          color: #ffffff;
        }

        button[kind="secondary"] {
          border-radius: 10px;
          border: 1px solid var(--border);
        }

        button[kind="secondary"]:hover,
        button[kind="secondary"]:active,
        button[kind="secondary"]:focus {
          border: 1px solid var(--border);
          background: #ffffff;
          color: var(--text);
        }

        /* Champs et formulaires */
        div[data-baseweb="input"] > div,
        div[data-baseweb="select"] > div {
          border-radius: 10px;
          border-color: var(--border);
        }

        div[data-baseweb="input"] > div {
          background: #ffffff !important;
        }

        div[data-baseweb="select"] > div {
          background: #ffffff !important;
        }

        div[data-baseweb="select"] div[role="combobox"] {
          background: #ffffff !important;
        }

        /* Listes deroulantes */
        div[data-baseweb="select"] span,
        div[data-baseweb="select"] input {
          color: var(--text);
        }

        div[data-baseweb="select"] svg {
          color: var(--muted);
        }

        div[data-baseweb="popover"] ul,
        div[data-baseweb="menu"] ul,
        ul[role="listbox"] {
          background: #ffffff;
          color: var(--text);
          border: 1px solid var(--border);
        }

        div[data-baseweb="popover"] li,
        div[data-baseweb="menu"] li,
        ul[role="listbox"] li {
          color: var(--text);
        }

        div[data-baseweb="select"] [role="option"] {
          color: var(--text) !important;
        }

        div[data-testid="stTextInput"] input,
        div[data-testid="stNumberInput"] input {
          background: #ffffff;
        }

        div[data-testid="stForm"] label,
        div[data-testid="stTextInput"] label,
        div[data-testid="stNumberInput"] label,
        div[data-testid="stSelectbox"] label,
        div[data-testid="stDateInput"] label,
        div[data-testid="stTextArea"] label,
        div[data-testid="stRadio"] label,
        div[data-testid="stCheckbox"] label,
        div[data-testid="stMultiSelect"] label {
          color: var(--text) !important;
        }

        div[data-baseweb="input"] input,
        div[data-baseweb="textarea"] textarea,
        div[data-testid="stTextInput"] input,
        div[data-testid="stNumberInput"] input,
        div[data-testid="stDateInput"] input {
          color: var(--text);
          background: #ffffff !important;
          caret-color: var(--text);
        }

        div[data-baseweb="input"] input::placeholder,
        div[data-baseweb="textarea"] textarea::placeholder {
          color: var(--muted);
        }

        div[data-baseweb="select"] * {
          color: var(--text);
        }

        button[kind="primary"] {
          color: #ffffff;
        }

        button[kind="secondary"] {
          color: var(--text);
          background: #ffffff;
        }

        div[data-testid="stNumberInput"] button {
          color: #ffffff;
        }

        div[data-testid="stFormSubmitButton"] button,
        div[data-testid="stButton"] button {
          background: #111827;
          border-color: #111827;
          color: #ffffff;
        }

        div[data-testid="stFormSubmitButton"] button:hover,
        div[data-testid="stFormSubmitButton"] button:active,
        div[data-testid="stFormSubmitButton"] button:focus,
        div[data-testid="stButton"] button:hover,
        div[data-testid="stButton"] button:active,
        div[data-testid="stButton"] button:focus {
          background: #111827;
          border-color: #111827;
          color: #ffffff;
        }

        /* Radios (Oui / Non) */
        div[data-testid="stRadio"] label,
        div[data-testid="stRadio"] span {
          color: var(--text) !important;
        }

        div[data-testid="stRadio"] div[role="radiogroup"] > label {
          color: var(--text) !important;
          opacity: 1 !important;
        }

        div[data-testid="stRadio"] * {
          color: var(--text) !important;
        }

        /* Footer (reserve) */
        </style>
        """,
        unsafe_allow_html=True,
    )


# --- Entete de page (main) ---
def render_page_title(title, subtitle=None):
    st.markdown(f"<div class='page-title'>{title}</div>", unsafe_allow_html=True)
    if subtitle:
        st.markdown(
            f"<div class='page-subtitle'>{subtitle}</div>",
            unsafe_allow_html=True,
        )


# --- Acces aux donnees ---
def fetch_df(query, params=None):
    with db_cursor() as (_, cur):
        cur.execute(query, params or ())
        rows = cur.fetchall()
    return pd.DataFrame(rows)


def fetch_one(query, params=None):
    with db_cursor() as (_, cur):
        cur.execute(query, params or ())
        return cur.fetchone()


def exec_query(query, params=None):
    with db_cursor() as (_, cur):
        cur.execute(query, params or ())


def list_categories(stockable=None):
    query = "SELECT id_categorie, libelle, stockable FROM categorie"
    filters = []
    params = []
    if stockable is not None:
        filters.append("stockable = %s")
        params.append(1 if stockable else 0)
    if filters:
        query += " WHERE " + " AND ".join(filters)
    query += " ORDER BY libelle"
    return fetch_df(query, params)


def list_receipts(limit=50):
    return fetch_df(
        """
        SELECT id_recu, date_recu, nom_client
        FROM recu
        ORDER BY id_recu DESC
        LIMIT %s
        """,
        (limit,),
    )


def create_receipt(nom_client=None):
    with db_cursor() as (_, cur):
        cur.execute(
            """
            INSERT INTO recu (date_recu, nom_client)
            VALUES (%s, %s)
            """,
            (datetime.now(), nom_client),
        )
        return cur.lastrowid


def list_products():
    return fetch_df(
        """
        SELECT p.id_produit,
               p.nom_produit,
               c.libelle AS categorie,
               p.prix_achat,
               p.prix_vente_bouteille,
               p.prix_vente_verre,
               p.stock_actuel,
               p.unite_vente,
               p.id_categorie,
               p.quantite_ml
        FROM produit p
        JOIN categorie c ON p.id_categorie = c.id_categorie
        ORDER BY p.nom_produit
        """
    )


def create_product(nom, id_categorie, mesure):
    exec_query(
        """
        INSERT INTO produit (
            nom_produit,
            id_categorie,
            prix_achat,
            prix_vente_bouteille,
            prix_vente_verre,
            stock_actuel,
            unite_vente,
            quantite_ml
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (nom, id_categorie, 0, 0, 0, 0, "bouteille", mesure),
    )


def update_product(
    product_id,
    nom,
    id_categorie,
    prix_achat,
    prix_vente_bouteille,
    prix_vente_verre,
    stock_actuel,
    unite_vente,
    quantite_ml
):
    exec_query(
        """
        UPDATE produit
        SET nom_produit = %s,
            id_categorie = %s,
            prix_achat = %s,
            prix_vente_bouteille = %s,
            prix_vente_verre = %s,
            stock_actuel = %s,
            unite_vente = %s,
            quantite_ml = %s
        WHERE id_produit = %s
        """,
        (
            nom,
            id_categorie,
            prix_achat,
            prix_vente_bouteille,
            prix_vente_verre,
            stock_actuel,
            unite_vente,
            quantite_ml,
            product_id
            
        ),
    )

# OPERATION TABLE VERRE_DE_MESURE


def list_verres():
    return fetch_df(
        """
        SELECT v.id,
               v.libelle,
               v.mesure
        FROM verre_de_mesure v
        """
    )


def create_verre(libelle, description):
    exec_query(
        """
        INSERT INTO verre_de_mesure (
            libelle,
            description
            
        )
        VALUES (%s, %s)
        """,
        (libelle,description),
    )


def update_verre(
    id,
    libelle,
    description,
    
):
    exec_query(
        """
        UPDATE verre_de_mesure
        SET libelle = %s,
            description = %s
        WHERE id = %s
        """,
        (
            id,
            libelle,
            description
            
        ),
    )



def delete_product(product_id):
    exec_query("DELETE FROM produit WHERE id_produit = %s", (product_id,))


def add_stock_entry(
    product_id, quantite, date_entree, prix_achat, prix_vente, unite_vente
):
    with db_cursor() as (_, cur):
        cur.execute(
            """
            INSERT INTO entree_stock (date_entree, quantite, id_produit)
            VALUES (%s, %s, %s)
            """,
            (date_entree, quantite, product_id),
        )
        if unite_vente == "verre":
            cur.execute(
                """
                UPDATE produit
                SET stock_actuel = stock_actuel + %s,
                    prix_achat = %s,
                    prix_vente_verre = %s,
                    unite_vente = %s
                WHERE id_produit = %s
                """,
                (quantite, prix_achat, prix_vente, unite_vente, product_id),
            )
        else:
            cur.execute(
                """
                UPDATE produit
                SET stock_actuel = stock_actuel + %s,
                    prix_achat = %s,
                    prix_vente_bouteille = %s,
                    unite_vente = %s
                WHERE id_produit = %s
                """,
                (quantite, prix_achat, prix_vente, unite_vente, product_id),
            )


def add_sale_stockable(product_id, quantite, date_vente, type_vente, receipt_id):
    with db_cursor() as (_, cur):
        cur.execute(
            """
            SELECT stock_actuel,
                   prix_vente_bouteille,
                   prix_vente_verre,
                   id_categorie
            FROM produit
            WHERE id_produit = %s
            FOR UPDATE
            """,
            (product_id,),
        )
        row = cur.fetchone()
        if not row:
            raise ValueError("Produit introuvable")
        if row["stock_actuel"] < quantite:
            raise ValueError("Stock insuffisant")

        if type_vente == "verre":
            prix_vente = row["prix_vente_verre"]
        else:
            prix_vente = row["prix_vente_bouteille"]
        if prix_vente <= 0:
            raise ValueError("Prix de vente non defini pour cette unite")
        montant = (prix_vente * Decimal(quantite)).quantize(Decimal("0.01"))
        cur.execute(
            """
            INSERT INTO vente (
                date_vente,
                quantite,
                montant,
                nom_preparation,
                type_vente,
                id_produit,
                id_categorie,
                id_recu
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                date_vente,
                quantite,
                montant,
                None,
                type_vente,
                product_id,
                row["id_categorie"],
                receipt_id,
            ),
        )
        cur.execute(
            """
            UPDATE produit
            SET stock_actuel = stock_actuel - %s
            WHERE id_produit = %s
            """,
            (quantite, product_id),
        )


def add_sale_non_stockable(
    category_id,
    nom_preparation,
    quantite,
    prix_vente,
    date_vente,
    type_vente,
    receipt_id,
):
    montant = (Decimal(str(prix_vente)) * Decimal(quantite)).quantize(
        Decimal("0.01")
    )
    exec_query(
        """
        INSERT INTO vente (
            date_vente,
            quantite,
            montant,
            nom_preparation,
            type_vente,
            id_produit,
            id_categorie,
            id_recu
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            date_vente,
            quantite,
            montant,
            nom_preparation,
            type_vente,
            None,
            category_id,
            receipt_id,
        ),
    )


def add_charge(type_charge, montant, date_charge):
    exec_query(
        """
        INSERT INTO charge (type_charge, montant, date_charge)
        VALUES (%s, %s, %s)
        """,
        (type_charge, montant, date_charge),
    )


def update_charge(charge_id, type_charge, montant, date_charge):
    exec_query(
        """
        UPDATE charge
        SET type_charge = %s,
            montant = %s,
            date_charge = %s
        WHERE id_charge = %s
        """,
        (type_charge, montant, date_charge, charge_id),
    )


def delete_charge(charge_id):
    exec_query("DELETE FROM charge WHERE id_charge = %s", (charge_id,))


def list_entries(start_date=None, end_date=None, product_id=None):
    query = (
        """
        SELECT e.id_entree,
               e.date_entree,
               e.quantite,
               p.nom_produit,
               c.libelle AS categorie
        FROM entree_stock e
        JOIN produit p ON e.id_produit = p.id_produit
        JOIN categorie c ON p.id_categorie = c.id_categorie
        """
    )
    filters = []
    params = []
    if start_date:
        filters.append("e.date_entree >= %s")
        params.append(start_date)
    if end_date:
        filters.append("e.date_entree <= %s")
        params.append(end_date)
    if product_id:
        filters.append("e.id_produit = %s")
        params.append(product_id)
    if filters:
        query += " WHERE " + " AND ".join(filters)
    query += " ORDER BY e.date_entree DESC, e.id_entree DESC"
    return fetch_df(query, params)


def list_sales(start_date=None, end_date=None, product_id=None, category_id=None):
    query = (
        """
        SELECT v.id_vente,
               v.date_vente,
               v.quantite,
               v.montant,
               v.type_vente,
               v.id_recu,
               c.libelle AS categorie,
               CASE
                   WHEN v.id_produit IS NOT NULL THEN p.nom_produit
                   ELSE v.nom_preparation
               END AS article,
               CASE
                   WHEN v.type_vente = 'verre' THEN 
                       (v.montant - (COALESCE(p.prix_achat, 0) / NULLIF(6, 0) * v.quantite))
                   ELSE
                       (v.montant - COALESCE(p.prix_achat, 0) * v.quantite)
               END AS marge
        FROM vente v
        JOIN categorie c ON v.id_categorie = c.id_categorie
        LEFT JOIN produit p ON v.id_produit = p.id_produit
        """
    )
    filters = []
    params = []
    if start_date:
        filters.append("v.date_vente >= %s")
        params.append(start_date)
    if end_date:
        filters.append("v.date_vente <= %s")
        params.append(end_date)
    if product_id:
        filters.append("v.id_produit = %s")
        params.append(product_id)
    if category_id:
        filters.append("v.id_categorie = %s")
        params.append(category_id)
    if filters:
        query += " WHERE " + " AND ".join(filters)
    query += " ORDER BY v.date_vente DESC, v.id_vente DESC"
    return fetch_df(query, params)


def list_charges(start_date=None, end_date=None):
    query = "SELECT id_charge, type_charge, montant, date_charge FROM charge"
    filters = []
    params = []
    if start_date:
        filters.append("date_charge >= %s")
        params.append(start_date)
    if end_date:
        filters.append("date_charge <= %s")
        params.append(end_date)
    if filters:
        query += " WHERE " + " AND ".join(filters)
    query += " ORDER BY date_charge DESC, id_charge DESC"
    return fetch_df(query, params)


def get_sales_totals(start_date, end_date):
    return fetch_one(
        """
        SELECT
            COALESCE(SUM(v.montant), 0) AS total_ventes,
            GREATEST(
                COALESCE(SUM(v.montant - (COALESCE(p.prix_achat, 0) * v.quantite)), 0),
                0
            ) AS marge
        FROM vente v
        LEFT JOIN produit p ON v.id_produit = p.id_produit
        WHERE v.date_vente BETWEEN %s AND %s
        """,
        (start_date, end_date),
    )


def get_charge_total(start_date, end_date):
    row = fetch_one(
        """
        SELECT COALESCE(SUM(montant), 0) AS total_charges
        FROM charge
        WHERE date_charge BETWEEN %s AND %s
        """,
        (start_date, end_date),
    )
    return row["total_charges"] if row else 0


def list_low_stock(threshold):
    return fetch_df(
        """
        SELECT p.id_produit,
               p.nom_produit,
               c.libelle AS categorie,
               p.stock_actuel
        FROM produit p
        JOIN categorie c ON p.id_categorie = c.id_categorie
        WHERE p.stock_actuel <= %s
        ORDER BY p.stock_actuel ASC, p.nom_produit
        """,
        (threshold,),
    )


# --- Helpers UI (main) ---
def show_dataframe(df, empty_message):
    if df.empty:
        st.info(empty_message)
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)


def build_product_map(products_df):
    return {
        f"{row['nom_produit']} (#{row['id_produit']})": row
        for row in products_df.to_dict("records")
    }


def build_category_map(categories_df):
    return {
        f"{row['libelle']} (#{row['id_categorie']})": row
        for row in categories_df.to_dict("records")
    }


def filter_products_by_category(products_df, category_id):
    if products_df.empty:
        return products_df
    return products_df[products_df["id_categorie"] == category_id]


def render_product_table(products_df, key):
    if products_df.empty:
        st.info("Aucun produit")
        return None
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
    row_index = event.selection.rows[0]
    return products_df.iloc[row_index].to_dict()


def get_category_key(category_map, category_id):
    for key, row in category_map.items():
        if row["id_categorie"] == category_id:
            return key
    return None


# --- Pages (main) ---
def render_dashboard():
    render_page_title("Tableau de bord", "Vue globale du jour")
    today = date.today()

    totals = get_sales_totals(today, today)
    total_ventes = totals["total_ventes"] if totals else 0
    marge = totals["marge"] if totals else 0
    total_charges = get_charge_total(today, today)
    net = Decimal(str(marge)) - Decimal(str(total_charges))

    col1, col2, col4 = st.columns(3)
    col1.metric("Ventes du jour", f"{total_ventes:,.2f}")
    col2.metric("Marge du jour", f"{marge:,.2f}")
    col4.metric("Net du jour", f"{net:,.2f}")

    st.subheader("Stock faible")
    threshold = st.number_input(
        "Seuil stock faible", min_value=0, value=5, step=1
    )
    low_stock_df = list_low_stock(threshold)
    show_dataframe(low_stock_df, "Aucun produit sous le seuil")


def render_products():
    render_page_title("Produits", "Catalogue et gestion du stock")
    products_df = list_products()
    categories_df = list_categories(stockable=True)

    tab_list, tab_add, tab_edit, tab_delete = st.tabs(
        ["Liste", "Ajouter", "Modifier", "Supprimer"]
    )

    with tab_list:
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
                "quantite_ml": "Quantité en mL"
            }
        )
        show_dataframe(display_df, "Aucun produit")

    with tab_add:
        if st.session_state.get("product_added"):
            st.success("Produit ajouté")
            st.session_state["product_added"] = False
        category_map = None
        category_keys = []
        if not categories_df.empty:
            category_map = build_category_map(categories_df)
            category_keys = list(category_map.keys())
        with st.form("add_product", clear_on_submit=True):
            if categories_df.empty:
                st.info("Ajoutez des catégories stockables avant de créer un produit")
                submitted = st.form_submit_button("Ajouter")
            else:
                nom = st.text_input("Nom du produit")
                categorie_key = st.selectbox("Catégorie", category_keys)
                quantite_ml = st.number_input(
                    "Quantité contenu en mL", min_value=10, step=1
                ) # Declarer la quantité contenu dans la bouteille
                submitted = st.form_submit_button("Ajouter")
        if submitted:
            if categories_df.empty:
                st.error("Aucune catégorie stockable disponible")
            elif not nom:
                st.error("Nom du produit requis")
            else:
                category = category_map[categorie_key]
                create_product(nom, category["id_categorie"], quantite_ml) # Enregistrer le produit
                st.session_state["product_added"] = True
                st.rerun()

    with tab_edit:
        if products_df.empty or categories_df.empty:
            st.info("Aucun produit à modifier")
        else:
            if st.session_state.get("product_updated"):
                st.success("Produit modifie")
                st.session_state["product_updated"] = False
            selected_product = render_product_table(
                products_df, key="edit_product_table"
            )
            if selected_product is None:
                st.info("Selectionnez une ligne du tableau")
            else:
                if st.button("Charger pour modifier", key="load_product_edit"):
                    st.session_state["edit_loaded_id"] = selected_product["id_produit"]
                    st.session_state["edit_nom"] = selected_product["nom_produit"]
                    st.session_state["edit_prix_achat"] = float(
                        selected_product["prix_achat"]
                    )
                    st.session_state["edit_prix_vente_bouteille"] = float(
                        selected_product["prix_vente_bouteille"]
                    )
                    st.session_state["edit_prix_vente_verre"] = float(
                        selected_product["prix_vente_verre"]
                    )
                    st.session_state["edit_stock"] = int(
                        selected_product["stock_actuel"]
                    )
                    st.session_state["edit_unite_vente"] = selected_product[
                        "unite_vente"
                    ]
                    st.session_state["edit_quantite_ml"] = selected_product[
                        "quantite_ml"
                    ]
                    st.session_state["edit_categorie_id"] = selected_product[
                        "id_categorie"
                    ]
                    st.rerun()

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
                    nom = st.text_input(
                        "Nom du produit", key="edit_nom"
                    )
                    categorie_key = st.selectbox(
                        "Categorie", category_keys, index=cat_index
                    )
                    prix_achat = st.number_input(
                        "Prix achat", min_value=0.0, step=0.01,placeholder=0.0,
                        key="edit_prix_achat",
                    )
                    prix_vente_bouteille = st.number_input(
                        "Prix vente bouteille", min_value=0.0, step=0.01,
                        key="edit_prix_vente_bouteille",placeholder=0.0
                    )
                    prix_vente_verre = st.number_input(
                        "Prix vente par verre de 50mL", min_value=0.0, step=0.01,
                        key="edit_prix_vente_verre",placeholder=0.0
                    ) # Declaration du prix de vente par unité de 50mL
                    stock_actuel = st.number_input(
                        "Stock actuel", min_value=0, step=1,
                        key="edit_stock",placeholder=0
                    )
                    unite_vente = st.selectbox(
                        "Unite de vente",
                        ["bouteille", "verre"],
                        key="edit_unite_vente",
                    )
                    quantite_ml = st.number_input(
                        "Quantité en mL",
                         min_value=0, step=1,
                        key="edit_quantite_ml",placeholder=0
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
                            quantite_ml
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
            selected_product = render_product_table(
                products_df, key="delete_product_table"
            )
            if selected_product is None:
                st.info("Selectionnez une ligne du tableau")
            else:
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
                            st.error(f"Suppression impossible: {exc}")


def render_entries():
    render_page_title("Entrees de stock", "Approvisionnements et historique")
    products_df = list_products()

    with st.form("add_entry"):
        if products_df.empty:
            st.info("Ajoutez un produit avant de saisir une entree")
            submitted = st.form_submit_button("Enregistrer")
        else:
            product_map = build_product_map(products_df)
            selected = st.selectbox(
                "Produit",
                list(product_map.keys()),
                index=None,
                placeholder="Selectionner ou rechercher le produit",
                key="entry_product",
            )
            quantite = st.number_input("Quantite", min_value=1, step=1)
            date_entree = st.date_input("Date entree", value=date.today())
            prix_achat = st.number_input(
                "Prix achat", min_value=0.0, step=0.01
            )
            prix_vente = st.number_input(
                "Prix vente", min_value=0.0, step=0.01
            )
            unite_vente = st.selectbox(
                "Unite de vente", ["bouteille", "verre"]
            )
            submitted = st.form_submit_button("Enregistrer")
            if submitted:
                if selected is None:
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
                    st.success("Entree enregistree")

    st.subheader("Historique")
    if products_df.empty:
        st.info("Aucun produit")
        return

    product_map = build_product_map(products_df)
    col1, col2, col3 = st.columns(3)
    start_date = col1.date_input("Debut", value=date.today().replace(day=1), key="entree_start")
    end_date = col2.date_input("Fin", value=date.today(), key="entree_end")
    product_filter = col3.selectbox(
        "Produit", ["Tous"] + list(product_map.keys()), key="entree_product"
    )
    product_id = None
    if product_filter != "Tous":
        product_id = product_map[product_filter]["id_produit"]

    entries_df = list_entries(start_date, end_date, product_id)
    show_dataframe(entries_df, "Aucune entree sur la periode")


def render_sales():
    st.markdown("## Ventes du jour")
    st.caption("Suivi des sorties")
    products_df = list_products()
    categories_df = list_categories()

    if "receipt_items" not in st.session_state:
        st.session_state["receipt_items"] = []

    if st.session_state.get("sale_reset"):
        st.session_state["sale_product"] = None
        st.session_state["sale_quantite"] = 1
        st.session_state["sale_unit_price"] = 0.0
        st.session_state["sale_unite"] = "bouteille"
        st.session_state["sale_unite_display"] = "bouteille"
        st.session_state["sale_reset"] = False

    if categories_df.empty:
        st.info("Ajoutez des categories avant de saisir une vente")
        return

    product_map = build_product_map(products_df) if not products_df.empty else {}

    header_left, header_right = st.columns([2, 1], vertical_alignment="bottom")
    with header_left:
        sale_day = st.date_input("Date", value=date.today(), key="sale_day")
    with header_right:
        st.markdown("<div style='height: 1.6rem'></div>", unsafe_allow_html=True)
        save_clicked = st.button(
            "Enregistrer les ventes",
            use_container_width=True,
            disabled=not st.session_state["receipt_items"],
        )

    category_labels = {
        row["id_categorie"]: f"{row['libelle']} (#{row['id_categorie']})"
        for row in categories_df.to_dict("records")
    }

    selected_product = None
    selected_key = None
    prix_unitaire = st.session_state.get("sale_unit_price", 0.0)
    quantite = st.session_state.get("sale_quantite", 1)
    unite_vente = st.session_state.get("sale_unite", "bouteille")

    cols = st.columns([5, 1.2, 1.5, 1.5, 1.2], vertical_alignment="bottom")
    if products_df.empty:
        cols[0].info("Ajoutez un produit avant de saisir une vente")
        add_clicked = cols[4].button("Ajouter", disabled=True)
    else:
        selected_key = cols[0].selectbox(
            "Produit",
            list(product_map.keys()),
            index=None,
            placeholder="Selectionner un produit",
            key="sale_product",
        )
        quantite = cols[1].number_input(
            "Quantite", min_value=1, step=1, key="sale_quantite"
        )
        if selected_key:
            selected_product = product_map[selected_key]
            unite_vente = selected_product.get("unite_vente", "bouteille")
            st.session_state["sale_unite"] = unite_vente
            if unite_vente == "verre":
                prix_unitaire = float(
                    selected_product.get("prix_vente_verre") or 0
                )
            else:
                prix_unitaire = float(
                    selected_product.get("prix_vente_bouteille") or 0
                )
            st.session_state["sale_unit_price"] = prix_unitaire
        else:
            st.session_state["sale_unit_price"] = 0.0
            prix_unitaire = 0.0

        st.session_state["sale_unite_display"] = unite_vente
        cols[2].selectbox(
            "Unite",
            ["bouteille", "verre"],
            index=0 if unite_vente == "bouteille" else 1,
            key="sale_unite_display",
            disabled=True,
        )
        cols[3].number_input(
            "Prix de vente",
            value=float(prix_unitaire),
            step=0.01,
            disabled=True,
        )
        cols[4].markdown("<div style='height: 1.6rem'></div>", unsafe_allow_html=True)
        add_clicked = cols[4].button("Ajouter")

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

    receipt_items = st.session_state["receipt_items"]
    display_items = []
    total_montant = Decimal("0")
    total_quantite = 0
    total_all = Decimal("0")
    product_lookup = {
        row["id_produit"]: row for row in products_df.to_dict("records")
    }
    for item in receipt_items:
        product = product_lookup.get(item["product_id"])
        prix_achat_btl = Decimal(str(product.get("prix_achat") or 0))
        prix_vente_btl = Decimal(str(product.get("prix_vente_bouteille") or 0))
        prix_vente_reel_verre = Decimal(str(product.get("prix_vente_verre") or 0))
        marge_ligne = Decimal("0")
        prix_vente = 0

        # CALCUL MARGE

        verre_de_mesure_ml = int(50)
        quantite_btl_ml = int(str(product.get("quantite_ml")) or 1)
        nombre_verre_total_moyen = int(quantite_btl_ml/verre_de_mesure_ml)
        # Le coût d'un seul verre est le prix d'achat bouteille divisé par le rendement
        prix_vente_moyen_verre = (prix_vente_btl / nombre_verre_total_moyen).quantize(Decimal("0.01"))

        quantite = Decimal(item["quantite"])

        montant_vente = (prix_vente_reel_verre * quantite).quantize(Decimal("0.01"))
        montant_moyen_vente_verre = (prix_vente_moyen_verre * quantite).quantize(Decimal("0.01"))

            
        if item["unite_vente"] == "verre":
            marge_ligne = montant_vente - montant_moyen_vente_verre

        else:
            montant_vente = (prix_vente * Decimal(item["quantite"])).quantize(Decimal("0.01"))
            marge_ligne = montant_vente - (prix_achat_btl * item["quantite"])


        # Calculs finaux pour le tableau
        
        total_all += montant_vente
        article = product["nom_produit"] if product else item["product_label"]
        categorie = category_labels.get(product.get("id_categorie"), "")

        display_items.append(
            {
                "Produit": article,
                "Categorie": categorie,
                "Quantite": item["quantite"],
                "Prix d'achat bouteille": float(prix_achat_btl),
                "Prix de vente bouteille": float(prix_vente_btl),
                "Prix de vente verre": float(prix_vente_reel_verre),
                "Prix de vente moyen verre": float(prix_vente_moyen_verre),
                "Unite": item["unite_vente"],
                "Montant vente": float(montant_vente),
                "Montant moyen vente": float(montant_moyen_vente_verre),

                "Marge": float(marge_ligne), # Nouvelle colonne
            }
        )
        total_montant += montant_vente
        total_quantite += item["quantite"]

    if display_items:
        display_items.append(
            {
                "Produit": "Total du jour",
                "Categorie": "",
                "Quantite": "",
                "Prix d'achat bouteille": "",
                "Prix de vente bouteille" : "",
                "Prix de vente verre" : "",
                "Prix de vente moyen verre": "",
                "Unite": "",
                "Montant vente": float(total_montant),
                "Montant moyen vente" : "",
                "Marge": float(marge_ligne)
            }
        )
    table_df = pd.DataFrame(
        display_items,
        columns=[
            "Produit",
            "Categorie",
            "Quantite",
            "Prix d'achat bouteille",
            "Prix de vente bouteille",
            "Prix de vente verre",
            "Prix de vente moyen verre",
            "Unite",
            "Montant vente",
            "Montant moyen vente",
            "Marge",
        ],
    )
    st.dataframe(table_df, use_container_width=True, hide_index=True)

    if receipt_items:
        # Calcul de la marge totale de la liste actuelle
        total_marge_session = sum(Decimal(str(i["Marge"])) for i in display_items if i["Produit"] != "Total du jour")
        
        action_col, total_col = st.columns([1, 2])
        if action_col.button("Vider la liste", key="clear_receipt_items"):
            st.session_state["receipt_items"] = []
            st.rerun()
        
        total_col.markdown(
            f"**Total Ventes**: {total_all:,.2f} | **Marge estimée**: {total_marge_session:,.2f}"
        )

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

    st.subheader("Historique")
    if categories_df.empty:
        st.info("Aucune categorie")
        return

    product_map = build_product_map(products_df) if not products_df.empty else {}
    category_map = build_category_map(categories_df)
    col1, col2, col3, col4 = st.columns(4)
    start_date = col1.date_input("Debut", value=date.today().replace(day=1), key="vente_start")
    end_date = col2.date_input("Fin", value=date.today(), key="vente_end")
    category_filter = col3.selectbox(
        "Categorie", ["Toutes"] + list(category_map.keys()), key="vente_category"
    )
    product_filter = col4.selectbox(
        "Produit", ["Tous"] + list(product_map.keys()), key="vente_product"
    )
    product_id = None
    if product_filter != "Tous":
        product_id = product_map[product_filter]["id_produit"]
    category_id = None
    if category_filter != "Toutes":
        category_id = category_map[category_filter]["id_categorie"]

    sales_df = list_sales(start_date, end_date, product_id, category_id)
    show_dataframe(sales_df, "Aucune vente sur la periode")


def render_charges():
    render_page_title("Charges", "Loyer, factures, charges fixes")

    tab_list, tab_add, tab_edit, tab_delete = st.tabs(
        ["Liste", "Ajouter", "Modifier", "Supprimer"]
    )

    with tab_list:
        col1, col2 = st.columns(2)
        start_date = col1.date_input("Debut", value=date.today().replace(day=1), key="charge_start")
        end_date = col2.date_input("Fin", value=date.today(), key="charge_end")
        charges_df = list_charges(start_date, end_date)
        show_dataframe(charges_df, "Aucune charge sur la periode")

    with tab_add:
        with st.form("add_charge"):
            type_charge = st.text_input("Type charge")
            montant = st.number_input("Montant", min_value=0.0, step=0.01)
            date_charge = st.date_input("Date charge", value=date.today())
            submitted = st.form_submit_button("Ajouter")
        if submitted:
            if not type_charge:
                st.error("Type charge requis")
            else:
                add_charge(type_charge, montant, date_charge)
                st.success("Charge ajoutee")

    with tab_edit:
        charges_df = list_charges()
        if charges_df.empty:
            st.info("Aucune charge a modifier")
        else:
            charge_map = {
                f"{row['type_charge']} (#{row['id_charge']})": row
                for row in charges_df.to_dict("records")
            }
            selected = st.selectbox(
                "Charge", list(charge_map.keys()), key="edit_charge_select"
            )
            charge = charge_map[selected]
            with st.form("edit_charge"):
                type_charge = st.text_input(
                    "Type charge", value=charge["type_charge"]
                )
                montant = st.number_input(
                    "Montant", min_value=0.0, step=0.01,
                    value=float(charge["montant"]),
                )
                date_charge = st.date_input(
                    "Date charge", value=charge["date_charge"]
                )
                submitted = st.form_submit_button("Mettre a jour")
            if submitted:
                if not type_charge:
                    st.error("Type charge requis")
                else:
                    update_charge(
                        charge["id_charge"], type_charge, montant, date_charge
                    )
                    st.success("Charge modifiee")

    with tab_delete:
        charges_df = list_charges()
        if charges_df.empty:
            st.info("Aucune charge a supprimer")
        else:
            charge_map = {
                f"{row['type_charge']} (#{row['id_charge']})": row
                for row in charges_df.to_dict("records")
            }
            selected = st.selectbox(
                "Charge", list(charge_map.keys()), key="delete_charge_select"
            )
            charge = charge_map[selected]
            confirm = st.checkbox("Confirmer la suppression", key="confirm_charge")
            if st.button("Supprimer", key="delete_charge_button"):
                if not confirm:
                    st.error("Confirmation requise")
                else:
                    delete_charge(charge["id_charge"])
                    st.success("Charge supprimee")


def render_reports():
    render_page_title("Rapports", "Synthese des ventes et marges")

    start_date, end_date = st.date_input(
        "Periode", value=(date.today().replace(day=1), date.today())
    )

    totals = get_sales_totals(start_date, end_date)
    total_ventes = totals["total_ventes"] if totals else 0
    marge = totals["marge"] if totals else 0
    total_charges = get_charge_total(start_date, end_date)
    net = Decimal(str(marge)) - Decimal(str(total_charges))

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total ventes", f"{total_ventes:,.2f}")
    col2.metric("Marge", f"{marge:,.2f}")
    col3.metric("Charges", f"{total_charges:,.2f}")
    col4.metric("Net", f"{net:,.2f}")

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


# --- Routage des pages (main) ---
PAGES = {
    "Tableau de bord": render_dashboard,
    "Produits": render_products,
    "Entrees": render_entries,
    "Ventes": render_sales,
    "Charges": render_charges,
    "Rapports": render_reports,
}

apply_theme()

# --- Sidebar (navigation) ---
with st.sidebar:
    st.markdown("<div class='sidebar-brand'>BarStock</div>", unsafe_allow_html=True)
    st.markdown("<div class='sidebar-sub'>Gestion de stock</div>", unsafe_allow_html=True)
    st.text_input("Search", placeholder="Rechercher", label_visibility="collapsed")
    st.markdown("<div class='sidebar-section'>Menu</div>", unsafe_allow_html=True)
    choice = st.radio("Navigation", list(PAGES.keys()), label_visibility="collapsed")
    st.markdown("<div class='sidebar-section'>Support</div>", unsafe_allow_html=True)
    st.caption("Aide et assistance")

# --- Main (affichage des pages) ---
PAGES[choice]()

# --- Footer (non utilise pour le moment) ---
