# Gestion de stock pour bar (Streamlit + MySQL)

Application web locale pour gerer les stocks, ventes et charges d'un bar.
Acces via navigateur, mise a jour simple, deploiement possible sur Streamlit Cloud.

## Fonctionnalites
- Produits: ajout, modification, suppression, consultation, stock actuel
- Categories: table dediee, stockable ou non stockable
- Entrees de stock: enregistrement, historique, mise a jour du stock
- Ventes: enregistrement, calcul du montant, diminution du stock si stockable, choix unite (bouteille/verre), gestion des recus
- Charges fixes: ajout, modification, suppression, consultation par periode
- Rapports: ventes, marge, charges, net (jour et periode)

## Installation locale
1. Creer une base MySQL et un utilisateur.
2. Executer `schema.sql` dans la base.
3. Renseigner la configuration DB avec:
   - Streamlit secrets (recommande): `.streamlit/secrets.toml` (modele: `.streamlit/secrets.toml.example`)
   - ou variables d'environnement: `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`
4. Installer les dependances: `python -m pip install -r requirements.txt`
5. Lancer l'app: `streamlit run streamlit_app.py`

## Deploiement Streamlit Cloud
- Ajouter les secrets MySQL dans la section "Secrets" du projet Streamlit Cloud.
- La base MySQL doit etre accessible depuis le cloud (host public ou tunnel securise).

## Notes
- La marge est calculee avec les prix actuels des produits.
- L'ajustement du stock est disponible via la modification du produit.
- Les categories non stockables (Cocktail, Mocktail) demandent un nom de preparation et un prix saisi a la vente.
- En cas d'ancienne base, recreez ou migrez les tables avant d'executer le nouveau schema.
- L'unite de vente est choisie au moment de la vente (plus stockee sur le produit).
- Les ventes peuvent etre regroupees par recu pour identifier un meme client.



d:\bar-log\.venv\Scripts\python.exe -m streamlit run d:\bar-log\streamlit_app.py
