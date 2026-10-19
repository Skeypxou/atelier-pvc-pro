import streamlit as st
from atelier_pvc.store import load_db, initialize_db

st.set_page_config(page_title="Atelier PVC Pro", page_icon="🏭", layout="wide")
initialize_db()
st.title("🏭 Atelier PVC Pro")
st.caption("Gestion d'atelier de menuiserie PVC")

try:
    db = load_db()
except Exception as exc:
    st.error(str(exc))
    st.stop()

st.subheader("Tableau de bord")
cols = st.columns(4)
cols[0].metric("Clients", len(db["clients"]))
cols[1].metric("Produits", len(db["products"]))
cols[2].metric("Devis", len(db["quotes"]))
cols[3].metric("Fabrications", len(db["jobs"]))

paid = sum(float(i.get("paid", 0)) for i in db["invoices"])
outstanding = sum(max(0.0, float(i.get("total", 0)) - float(i.get("paid", 0))) for i in db["invoices"])
col_a, col_b = st.columns(2)
col_a.metric("Montant encaissé", f"{paid:,.2f} DA")
col_b.metric("Reste à encaisser", f"{outstanding:,.2f} DA")

st.divider()
st.markdown("### Démarrage rapide")
st.write("Utilise le menu à gauche pour gérer les clients, le catalogue, les devis, la fabrication et les factures.")
st.info("Important : sur Streamlit Community Cloud, les fichiers JSON locaux ne constituent pas un stockage permanent garanti. Télécharge régulièrement une sauvegarde depuis la page Sauvegarde.")
