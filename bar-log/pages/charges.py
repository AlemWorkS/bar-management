"""
Page "Charges": CRUD des depenses (loyer, factures, etc.).

Interaction:
- streamlit_app.py route ici via le menu.
- data_access.py gere les operations SQL (list/add/update/delete).
- ui.py fournit le titre standard et l'affichage de tableau.
"""

from datetime import date

import streamlit as st

from data_access import add_charge, delete_charge, list_charges, update_charge
from ui import render_page_title, show_dataframe


def render_charges():
    """Rend les onglets Liste/Ajouter/Modifier/Supprimer des charges."""
    render_page_title("Charges", "Loyer, factures, charges fixes")

    tab_list, tab_add, tab_edit, tab_delete = st.tabs(
        ["Liste", "Ajouter", "Modifier", "Supprimer"]
    )

    with tab_list:
        # Filtre temporel simple pour consulter les depenses.
        col1, col2 = st.columns(2)
        start_date = col1.date_input(
            "Debut", value=date.today().replace(day=1), key="charge_start"
        )
        end_date = col2.date_input("Fin", value=date.today(), key="charge_end")
        charges_df = list_charges(start_date, end_date)
        show_dataframe(charges_df, "Aucune charge sur la periode")

    with tab_add:
        # Feedback utilisateur apres insertion.
        if st.session_state.get("charge_added"):
            st.success("Charge ajoutee")
            st.session_state["charge_added"] = False

        # Reset des champs si une insertion vient d'etre faite.
        if st.session_state.get("charge_reset"):
            st.session_state["charge_type"] = ""
            st.session_state["charge_montant"] = 0.0
            st.session_state["charge_date"] = date.today()
            st.session_state["charge_reset"] = False

        with st.form("add_charge", clear_on_submit=True):
            type_charge = st.text_input("Type charge", key="charge_type")
            montant = st.number_input(
                "Montant", min_value=0.0, step=0.01, key="charge_montant"
            )
            date_charge = st.date_input(
                "Date charge", value=date.today(), key="charge_date"
            )
            submitted = st.form_submit_button("Ajouter")
        if submitted:
            if not type_charge:
                st.error("Type charge requis")
            else:
                add_charge(type_charge, montant, date_charge)
                st.session_state["charge_added"] = True
                st.session_state["charge_reset"] = True
                st.rerun()

    with tab_edit:
        # Edition en 2 etapes:
        # 1) choisir une ligne dans le tableau,
        # 2) charger ses valeurs dans un formulaire.
        charges_df = list_charges()
        if charges_df.empty:
            st.info("Aucune charge a modifier")
        else:
            event = st.dataframe(
                charges_df,
                use_container_width=True,
                hide_index=True,
                on_select="rerun",
                selection_mode="single-row",
                key="edit_charge_table",
            )
            selected_charge = None
            if event.selection.rows:
                selected_charge = charges_df.iloc[event.selection.rows[0]].to_dict()

            if selected_charge is None:
                st.info("Selectionnez une ligne du tableau")
            else:
                if st.button("Charger pour modifier", key="load_charge_edit"):
                    st.session_state["edit_charge_id"] = selected_charge["id_charge"]
                    st.session_state["edit_charge_type"] = selected_charge["type_charge"]
                    st.session_state["edit_charge_montant"] = float(
                        selected_charge["montant"]
                    )
                    st.session_state["edit_charge_date"] = selected_charge[
                        "date_charge"
                    ]
                    st.rerun()

            if st.session_state.get("edit_charge_id"):
                with st.form("edit_charge"):
                    type_charge = st.text_input("Type charge", key="edit_charge_type")
                    montant = st.number_input(
                        "Montant",
                        min_value=0.0,
                        step=0.01,
                        key="edit_charge_montant",
                    )
                    date_charge = st.date_input("Date charge", key="edit_charge_date")
                    submitted = st.form_submit_button("Mettre a jour")
                if submitted:
                    if not type_charge:
                        st.error("Type charge requis")
                    else:
                        update_charge(
                            st.session_state["edit_charge_id"],
                            type_charge,
                            montant,
                            date_charge,
                        )
                        st.success("Charge modifiee")
                        st.session_state.pop("edit_charge_id", None)
                        st.rerun()

    with tab_delete:
        charges_df = list_charges()
        if charges_df.empty:
            st.info("Aucune charge a supprimer")
        else:
            # Mapping label -> row pour recuperer facilement l'id cible.
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

