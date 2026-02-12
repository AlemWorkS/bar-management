"""
Couche d'acces aux donnees (DAO/repository) de l'application BarStock.

Ce module encapsule toute la logique SQL et expose des fonctions Python
simples pour les pages Streamlit.

Architecture d'interaction:
- pages/*.py appellent ces fonctions pour lire/ecrire des donnees.
- ce module utilise db.db_cursor() pour gerer connexions + transactions.
- ui.py ne fait pas d'acces SQL: il consomme seulement les DataFrame/valeurs
  que ce module retourne.
"""

from datetime import datetime
from decimal import Decimal

import pandas as pd

from db import db_cursor


def fetch_df(query, params=None):
    """
    Execute une requete SQL et retourne un DataFrame pandas.

    Utilise par la plupart des fonctions list_* et par pages/reports.py
    pour des aggregations SQL ad-hoc.
    """
    with db_cursor() as (_, cur):
        cur.execute(query, params or ())
        rows = cur.fetchall()
    return pd.DataFrame(rows)


def fetch_one(query, params=None):
    """
    Execute une requete SQL et retourne une seule ligne (dict) ou None.

    Utilise pour les KPI (totaux) et les lectures ponctuelles.
    """
    with db_cursor() as (_, cur):
        cur.execute(query, params or ())
        return cur.fetchone()


def exec_query(query, params=None):
    """
    Execute une requete SQL sans retour (INSERT/UPDATE/DELETE simple).

    Le commit/rollback est gere automatiquement par db_cursor().
    """
    with db_cursor() as (_, cur):
        cur.execute(query, params or ())


def list_categories(stockable=None):
    """
    Retourne les categories.

    - stockable=None: toutes les categories,
    - stockable=True/False: filtre sur le flag stockable.

    Appelee notamment par pages/products.py et pages/sales.py.
    """
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
    """
    Retourne les derniers recus.

    Potentiellement utile pour des pages de suivi caisse/historique.
    """
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
    """
    Cree un recu et retourne son id.

    Appelee dans pages/sales.py avant d'inserer les lignes de vente.
    """
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
    """
    Retourne le catalogue produit avec categorie jointe.

    Source principale des ecrans:
    - pages/products.py
    - pages/entries.py
    - pages/sales.py
    - pages/dashboard.py (stock faible via autre fonction)
    """
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
               p.id_categorie
        FROM produit p
        JOIN categorie c ON p.id_categorie = c.id_categorie
        ORDER BY p.nom_produit
        """
    )


def create_product(
    nom,
    id_categorie,
    prix_achat=0,
    prix_vente_bouteille=0,
    prix_vente_verre=0,
    stock_actuel=0,
    unite_vente="bouteille",
):
    """
    Cree un nouveau produit.

    Les parametres optionnels permettent de pre-remplir prix/stock
    depuis l'UI (page produits, onglet Ajouter).
    """
    exec_query(
        """
        INSERT INTO produit (
            nom_produit,
            id_categorie,
            prix_achat,
            prix_vente_bouteille,
            prix_vente_verre,
            stock_actuel,
            unite_vente
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (
            nom,
            id_categorie,
            prix_achat,
            prix_vente_bouteille,
            prix_vente_verre,
            stock_actuel,
            unite_vente,
        ),
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
):
    """
    Met a jour un produit.

    Utilise par l'onglet "Modifier" de pages/products.py.
    """
    exec_query(
        """
        UPDATE produit
        SET nom_produit = %s,
            id_categorie = %s,
            prix_achat = %s,
            prix_vente_bouteille = %s,
            prix_vente_verre = %s,
            stock_actuel = %s,
            unite_vente = %s
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
            product_id,
        ),
    )


def delete_product(product_id):
    """
    Supprime un produit par id.

    Appelee depuis pages/products.py (onglet suppression).
    """
    exec_query("DELETE FROM produit WHERE id_produit = %s", (product_id,))


def add_stock_entry(
    product_id, quantite, date_entree, prix_achat, prix_vente, unite_vente
):
    """
    Enregistre une entree de stock et met a jour le produit associe.

    Flux metier:
    1) insertion dans entree_stock (historique),
    2) incrementation stock_actuel dans produit,
    3) mise a jour prix_achat + prix de vente selon l'unite cible.

    Appelee uniquement depuis pages/entries.py.
    """
    with db_cursor() as (_, cur):
        # Historisation de l'entree brute.
        cur.execute(
            """
            INSERT INTO entree_stock (date_entree, quantite, id_produit)
            VALUES (%s, %s, %s)
            """,
            (date_entree, quantite, product_id),
        )

        # Le prix de vente stocke depend de l'unite de vente choisie.
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
    """
    Enregistre une vente de produit stockable et decremente le stock.

    Flux transactionnel (dans le meme db_cursor):
    1) lock ligne produit (FOR UPDATE),
    2) validations (produit existe, stock suffisant, prix defini),
    3) insertion dans vente,
    4) decrementation de stock.

    Appelee depuis pages/sales.py.
    """
    with db_cursor() as (_, cur):
        # Lock pessimiste pour eviter les ventes concurrentes incoherentes.
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

        # Le prix utilise depend de l'unite vendue (bouteille/verre).
        if type_vente == "verre":
            prix_vente = row["prix_vente_verre"]
        else:
            prix_vente = row["prix_vente_bouteille"]
        if prix_vente <= 0:
            raise ValueError("Prix de vente non defini pour cette unite")

        montant = (prix_vente * Decimal(quantite)).quantize(Decimal("0.01"))

        # Ecriture de la ligne de vente.
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

        # Mise a jour stock apres la vente.
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
    """
    Enregistre une vente non stockable.

    Actuellement non utilisee dans l'UI principale, mais utile pour
    categories/preparations sans gestion de stock.
    """
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
    """
    Cree une charge.

    Utilisee dans pages/charges.py (onglet Ajouter).
    """
    exec_query(
        """
        INSERT INTO charge (type_charge, montant, date_charge)
        VALUES (%s, %s, %s)
        """,
        (type_charge, montant, date_charge),
    )


def update_charge(charge_id, type_charge, montant, date_charge):
    """
    Met a jour une charge existante.

    Utilisee dans pages/charges.py (onglet Modifier).
    """
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
    """
    Supprime une charge.

    Utilisee dans pages/charges.py (onglet Supprimer).
    """
    exec_query("DELETE FROM charge WHERE id_charge = %s", (charge_id,))


def list_entries(start_date=None, end_date=None, product_id=None):
    """
    Retourne l'historique des entrees de stock avec filtres optionnels.

    Utilisee par pages/entries.py (bloc Historique).
    """
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
    """
    Retourne l'historique des ventes avec filtres optionnels.

    Utilisee par pages/sales.py (bloc Historique).
    """
    query = (
        """
        SELECT v.id_vente,
               v.date_vente,
               v.quantite,
               v.montant,
               v.type_vente,
               v.id_recu,
               v.id_produit,
               c.libelle AS categorie,
               CASE
                   WHEN v.id_produit IS NOT NULL THEN p.nom_produit
                   ELSE v.nom_preparation
               END AS article,
               (v.montant - COALESCE(p.prix_achat, 0) * v.quantite) AS marge
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
    """
    Retourne les charges avec filtres de periode optionnels.

    Utilisee dans pages/charges.py (liste + edition + suppression)
    et indirectement par pages/dashboard.py / pages/reports.py via totaux.
    """
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
    """
    Retourne les totaux de ventes et marge sur une periode.

    Utilisee par pages/dashboard.py et pages/reports.py.
    """
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
    """
    Retourne la somme des charges sur une periode.

    Utilisee par pages/dashboard.py et pages/reports.py pour calculer le net.
    """
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
    """
    Retourne les produits dont le stock est inferieur/egal au seuil.

    Utilisee par pages/dashboard.py.
    """
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
