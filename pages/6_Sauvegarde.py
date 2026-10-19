import json
import streamlit as st
from atelier_pvc.store import load_db, save_db, restore_db

st.set_page_config(page_title="Sauvegarde | Atelier PVC Pro", page_icon="💾", layout="wide")
st.title("💾 Sauvegarde et restauration")
st.warning("Important : les fichiers locaux de Streamlit Community Cloud ne garantissent pas une conservation durable après redémarrage, redéploiement ou maintenance. Télécharge une sauvegarde régulièrement et conserve-la sur ton ordinateur.")

db = load_db()
backup = json.dumps(db, ensure_ascii=False, indent=2).encode("utf-8")
st.download_button("📥 Télécharger la sauvegarde complète JSON", backup, "atelier_pvc_sauvegarde.json", "application/json", use_container_width=True)
st.caption("La sauvegarde contient les clients, produits, devis, fabrications, factures et paiements.")

st.subheader("Restaurer une sauvegarde")
upload = st.file_uploader("Choisir un fichier atelier_pvc_sauvegarde.json", type=["json"])
confirm = st.checkbox("Je comprends que la restauration remplacera toutes les données actuelles.")
if st.button("Restaurer la sauvegarde", disabled=not (upload and confirm), type="primary"):
    try:
        content = json.loads(upload.getvalue().decode("utf-8"))
        restore_db(content)
        st.success("Sauvegarde restaurée.")
        st.rerun()
    except Exception as exc:
        st.error(f"Restauration impossible : {exc}")
