"""
Couche de connexion MySQL centralisee.

Interaction avec les autres modules:
- data_access.py ne parle jamais directement a mysql.connector.
- data_access.py passe uniquement par db_cursor() pour chaque requete.
- en cas d'erreur de configuration DB, st.stop() arrete proprement l'app.
"""

from contextlib import contextmanager
import os

import mysql.connector
import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError

# Clés minimales obligatoires pour etablir une connexion.
REQUIRED_KEYS = ("host", "user", "password", "database")


def _has_keys(cfg, keys):
    """Verifie qu'une config contient toutes les cles attendues."""
    return cfg is not None and all(key in cfg for key in keys)


def _from_secrets():
    """
    Lit la config DB depuis .streamlit/secrets.toml.

    Prioritaire en execution Streamlit (pratique pour dev local + cloud).
    """
    try:
        secrets = st.secrets
    except StreamlitSecretNotFoundError:
        return None
    if "mysql" not in secrets:
        return None

    cfg = secrets["mysql"]
    if not _has_keys(cfg, REQUIRED_KEYS):
        return None

    return {
        "host": cfg.get("host"),
        "port": int(cfg.get("port", 3306)),
        "user": cfg.get("user"),
        "password": cfg.get("password"),
        "database": cfg.get("database"),
    }


def _from_env():
    """
    Lit la config DB depuis des variables d'environnement.

    Utilise comme fallback si st.secrets est absent/incomplet.
    """
    host = os.getenv("DB_HOST")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    database = os.getenv("DB_NAME")
    if host is None or user is None or password is None or database is None:
        return None

    port = int(os.getenv("DB_PORT", "3306"))
    return {
        "host": host,
        "port": port,
        "user": user,
        "password": password,
        "database": database,
    }


def get_db_config():
    """
    Retourne la config DB finale.

    Priorite de resolution:
    1) st.secrets["mysql"]
    2) variables d'environnement DB_*
    """
    cfg = _from_secrets() or _from_env()
    if cfg is None:
        st.error(
            "Database config not found. Use Streamlit secrets or env vars: "
            "DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME."
        )
        # stop() coupe l'execution de la page en cours (signal utilisateur propre).
        st.stop()
    return cfg


@contextmanager
def db_cursor():
    """
    Context manager transactionnel pour toutes les operations SQL.

    Contrat:
    - ouvre une connexion + un cursor en dictionnaire (rows type dict),
    - yield (conn, cursor) au code appelant (dans data_access.py),
    - commit si tout se passe bien,
    - rollback si exception,
    - fermeture systematique cursor + connexion.
    """
    cfg = get_db_config()
    conn = mysql.connector.connect(
        host=cfg["host"],
        port=cfg["port"],
        user=cfg["user"],
        password=cfg["password"],
        database=cfg["database"],
    )
    try:
        cursor = conn.cursor(dictionary=True)
        yield conn, cursor
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()
