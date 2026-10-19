import pandas as pd
import streamlit as st
from atelier_pvc.store import load_db, create_record, update_record

st.set_page_config(page_title="Clients | Atelier PVC Pro", page_icon="👥", layout="wide")
st.title("👥 Clients")
db = load_db()

with st.expander("➕ Ajouter un client", expanded=not db["clients"]):
    with st.form("add_client", clear_on_submit=True):
        name = st.text_input("Nom / raison sociale *")
        phone = st.text_input("Téléphone")
        email = st.text_input("E-mail")
        address = st.text_area("Adresse")
        notes = st.text_area("Notes")
        submitted = st.form_submit_button("Enregistrer le client", use_container_width=True)
    if submitted:
        if not name.strip():
            st.error("Le nom du client est obligatoire.")
        else:
            create_record("clients", {"name": name.strip(), "phone": phone.strip(), "email": email.strip(), "address": address.strip(), "notes": notes.strip()})
            st.success("Client enregistré.")
            st.rerun()

db = load_db()
st.subheader("Répertoire clients")
search = st.text_input("Rechercher par nom, téléphone ou e-mail")
term = search.strip().casefold()
clients = [c for c in db["clients"] if term in " ".join([c.get("name", ""), c.get("phone", ""), c.get("email", "")]).casefold()]
rows = [{"Nom": c.get("name", ""), "Téléphone": c.get("phone", ""), "E-mail": c.get("email", ""), "Adresse": c.get("address", ""), "ID": c.get("id", "")[:8]} for c in clients]
if rows:
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    st.download_button("📥 Exporter les clients CSV", pd.DataFrame(rows).drop(columns=["ID"]).to_csv(index=False).encode("utf-8-sig"), "clients.csv", "text/csv")
else:
    st.info("Aucun client à afficher.")

if db["clients"]:
    st.subheader("Modifier un client")
    options = {f"{c['name']} — {c['id'][:8]}": c for c in db["clients"]}
    selected = st.selectbox("Client", list(options))
    client = options[selected]
    with st.form("edit_client"):
        name = st.text_input("Nom / raison sociale *", client.get("name", ""))
        phone = st.text_input("Téléphone", client.get("phone", ""))
        email = st.text_input("E-mail", client.get("email", ""))
        address = st.text_area("Adresse", client.get("address", ""))
        notes = st.text_area("Notes", client.get("notes", ""))
        submitted = st.form_submit_button("Enregistrer les modifications")
    if submitted:
        if not name.strip():
            st.error("Le nom est obligatoire.")
        else:
            update_record("clients", client["id"], {"name": name.strip(), "phone": phone.strip(), "email": email.strip(), "address": address.strip(), "notes": notes.strip()})
            st.success("Client modifié.")
            st.rerun()
