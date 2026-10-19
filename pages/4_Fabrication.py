import pandas as pd
import streamlit as st
from atelier_pvc.store import load_db, create_record, update_record

st.set_page_config(page_title="Fabrication | Atelier PVC Pro", page_icon="⚙️", layout="wide")
st.title("⚙️ Fabrication et commandes")
db = load_db()

with st.expander("➕ Enregistrer un travail", expanded=not db["jobs"]):
    if not db["clients"]:
        st.warning("Crée d'abord un client dans la page Clients.")
    else:
        options = {f"{c['name']} — {c['id'][:8]}": c for c in db["clients"]}
        with st.form("create_job"):
            client_label = st.selectbox("Client", list(options))
            description = st.text_input("Description (ex. fenêtre 2 vantaux) *")
            width = st.number_input("Largeur (mm)", min_value=1, value=1200, step=10)
            height = st.number_input("Hauteur (mm)", min_value=1, value=1000, step=10)
            qty = st.number_input("Quantité", min_value=1, value=1, step=1)
            color = st.text_input("Couleur / finition", "Blanc")
            glass = st.text_input("Type de vitrage")
            notes = st.text_area("Instructions de fabrication")
            submitted = st.form_submit_button("Enregistrer le travail", use_container_width=True)
        if submitted:
            if not description.strip():
                st.error("La description est obligatoire.")
            else:
                number = f"FAB-{len(db['jobs']) + 1:04d}"
                create_record("jobs", {"number": number, "client_id": options[client_label]["id"], "client_name": options[client_label]["name"], "description": description.strip(), "width_mm": int(width), "height_mm": int(height), "quantity": int(qty), "color": color.strip(), "glass": glass.strip(), "notes": notes.strip(), "status": "À préparer"})
                st.success("Travail de fabrication enregistré.")
                st.rerun()

db = load_db()
st.subheader("Suivi de fabrication")
if db["jobs"]:
    rows = [{"Numéro": j.get("number"), "Client": j.get("client_name"), "Description": j.get("description"), "Dimensions": f"{j.get('width_mm')} × {j.get('height_mm')} mm", "Qté": j.get("quantity"), "Finition": j.get("color"), "Statut": j.get("status"), "ID": j.get("id", "")} for j in reversed(db["jobs"])]
    st.dataframe(pd.DataFrame(rows).drop(columns=["ID"]), use_container_width=True, hide_index=True)
    jobs = {f"{j['number']} — {j.get('client_name')} — {j.get('description')}": j for j in db["jobs"]}
    choice = st.selectbox("Mettre à jour un travail", list(jobs))
    job = jobs[choice]
    statuses = ["À préparer", "En fabrication", "Prêt", "Livré", "Annulé"]
    current = job.get("status", statuses[0])
    with st.form("update_job"):
        status = st.selectbox("Nouveau statut", statuses, index=statuses.index(current) if current in statuses else 0)
        submitted = st.form_submit_button("Mettre à jour")
    if submitted:
        update_record("jobs", job["id"], {"status": status})
        st.success("Statut de fabrication mis à jour.")
        st.rerun()
    csv_rows = [{"Numero": j.get("number"), "Client": j.get("client_name"), "Description": j.get("description"), "Largeur_mm": j.get("width_mm"), "Hauteur_mm": j.get("height_mm"), "Quantite": j.get("quantity"), "Couleur": j.get("color"), "Vitrage": j.get("glass"), "Notes": j.get("notes"), "Statut": j.get("status")} for j in db["jobs"]]
    st.download_button("📥 Exporter la liste de fabrication CSV", pd.DataFrame(csv_rows).to_csv(index=False).encode("utf-8-sig"), "fabrications.csv", "text/csv")
    st.caption("Les dimensions sont enregistrées telles que saisies. Les coupes exactes dépendent du système de profilés et des règles du fabricant ; elles ne sont pas déduites automatiquement ici.")
else:
    st.info("Aucun travail enregistré.")
