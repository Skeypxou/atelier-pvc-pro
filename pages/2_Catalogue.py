import pandas as pd
import streamlit as st
from atelier_pvc.store import load_db, create_record, update_record

st.set_page_config(page_title="Catalogue | Atelier PVC Pro", page_icon="🪟", layout="wide")
st.title("🪟 Catalogue PVC, vitrages et accessoires")
db = load_db()

with st.expander("➕ Ajouter un produit", expanded=not db["products"]):
    with st.form("add_product", clear_on_submit=True):
        name = st.text_input("Désignation *")
        category = st.selectbox("Catégorie", ["Profil PVC", "Vitrage", "Accessoire", "Quincaillerie", "Autre"])
        reference = st.text_input("Référence")
        unit = st.selectbox("Unité", ["pièce", "mètre", "m²", "lot"])
        price = st.number_input("Prix unitaire (DA)", min_value=0.0, value=0.0, step=100.0)
        stock = st.number_input("Stock", min_value=0, value=0, step=1)
        description = st.text_area("Description / dimensions")
        submitted = st.form_submit_button("Enregistrer le produit", use_container_width=True)
    if submitted:
        if not name.strip():
            st.error("La désignation est obligatoire.")
        elif reference.strip() and any(p.get("reference", "").casefold() == reference.strip().casefold() for p in db["products"]):
            st.error("Cette référence existe déjà.")
        else:
            create_record("products", {"name": name.strip(), "category": category, "reference": reference.strip(), "unit": unit, "price": round(price, 2), "stock": int(stock), "description": description.strip()})
            st.success("Produit enregistré.")
            st.rerun()

db = load_db()
filter_cat = st.selectbox("Filtrer par catégorie", ["Toutes"] + sorted({p.get("category", "Autre") for p in db["products"]}))
products = db["products"] if filter_cat == "Toutes" else [p for p in db["products"] if p.get("category") == filter_cat]
rows = [{"Désignation": p.get("name", ""), "Catégorie": p.get("category", ""), "Référence": p.get("reference", ""), "Unité": p.get("unit", "pièce"), "Prix (DA)": p.get("price", 0), "Stock": p.get("stock", 0), "ID": p.get("id", "")[:8]} for p in products]
if rows:
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    st.download_button("📥 Exporter le catalogue CSV", pd.DataFrame(rows).drop(columns=["ID"]).to_csv(index=False).encode("utf-8-sig"), "catalogue_pvc.csv", "text/csv")
else:
    st.info("Aucun produit dans cette catégorie.")

if db["products"]:
    st.subheader("Modifier le prix ou le stock")
    choices = {f"{p['name']} — {p.get('reference') or p['id'][:8]}": p for p in db["products"]}
    selected = st.selectbox("Produit à modifier", list(choices))
    product = choices[selected]
    with st.form("edit_product"):
        price = st.number_input("Prix (DA)", min_value=0.0, value=float(product.get("price", 0)), step=100.0)
        stock = st.number_input("Stock", min_value=0, value=int(product.get("stock", 0)), step=1)
        submitted = st.form_submit_button("Mettre à jour")
    if submitted:
        update_record("products", product["id"], {"price": round(price, 2), "stock": int(stock)})
        st.success("Produit mis à jour.")
        st.rerun()
