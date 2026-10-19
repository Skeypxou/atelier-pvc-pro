from datetime import date, timedelta
import pandas as pd
import streamlit as st
from atelier_pvc.store import load_db, create_record, update_record
from atelier_pvc.pdf import document_pdf

st.set_page_config(page_title="Devis | Atelier PVC Pro", page_icon="📄", layout="wide")
st.title("📄 Devis")
db = load_db()
clients_by_id = {c["id"]: c for c in db["clients"]}

with st.expander("➕ Créer un devis", expanded=not db["quotes"]):
    if not db["clients"]:
        st.warning("Crée d'abord un client dans la page Clients.")
    else:
        client_options = {f"{c['name']} — {c['id'][:8]}": c for c in db["clients"]}
        with st.form("create_quote"):
            selected_client = st.selectbox("Client", list(client_options))
            st.caption("Ajoute les lignes du devis dans le tableau. Les lignes vides sont ignorées.")
            starter = pd.DataFrame([
                {"Désignation": "Fenêtre PVC", "Quantité": 1, "Prix unitaire (DA)": 0.0},
                {"Désignation": "", "Quantité": 1, "Prix unitaire (DA)": 0.0},
                {"Désignation": "", "Quantité": 1, "Prix unitaire (DA)": 0.0},
            ])
            edited = st.data_editor(starter, num_rows="dynamic", use_container_width=True, key="quote_lines_editor", column_config={"Désignation": st.column_config.TextColumn(required=False), "Quantité": st.column_config.NumberColumn(min_value=1, step=1, required=True), "Prix unitaire (DA)": st.column_config.NumberColumn(min_value=0, step=100, format="%.2f DA")})
            tax_rate = st.number_input("TVA (%)", min_value=0.0, max_value=100.0, value=19.0, step=1.0)
            validity_days = st.number_input("Validité du devis (jours)", min_value=1, max_value=365, value=30, step=1)
            notes = st.text_area("Notes et conditions")
            submitted = st.form_submit_button("Enregistrer le devis", use_container_width=True)
        if submitted:
            lines = []
            try:
                for _, row in edited.iterrows():
                    description = str(row.get("Désignation", "")).strip()
                    if not description:
                        continue
                    qty = int(row.get("Quantité", 1))
                    price = float(row.get("Prix unitaire (DA)", 0))
                    if qty < 1 or price < 0:
                        raise ValueError("Les quantités doivent être positives et les prix non négatifs.")
                    lines.append({"description": description, "quantity": qty, "unit_price": round(price, 2), "line_total": round(qty * price, 2)})
                if not lines:
                    raise ValueError("Ajoute au moins une ligne avec une désignation.")
                subtotal = round(sum(x["line_total"] for x in lines), 2)
                tax = round(subtotal * tax_rate / 100, 2)
                total = round(subtotal + tax, 2)
                number = f"DEV-{date.today():%Y%m%d}-{len(db['quotes']) + 1:04d}"
                quote = create_record("quotes", {"number": number, "date": date.today().isoformat(), "valid_until": (date.today() + timedelta(days=int(validity_days))).isoformat(), "client_id": client_options[selected_client]["id"], "client_name": client_options[selected_client]["name"], "lines": lines, "subtotal": subtotal, "tax_rate": tax_rate, "tax": tax, "total": total, "notes": notes.strip(), "status": "En attente"})
                st.success(f"Devis {quote['number']} enregistré pour {total:,.2f} DA.")
                st.rerun()
            except (ValueError, TypeError) as exc:
                st.error(str(exc))

db = load_db()
st.subheader("Historique des devis")
if db["quotes"]:
    rows = [{"Numéro": q.get("number"), "Date": q.get("date"), "Client": q.get("client_name", clients_by_id.get(q.get("client_id"), {}).get("name", "Client")), "Total (DA)": q.get("total", 0), "Statut": q.get("status", "En attente"), "ID": q.get("id", "")} for q in reversed(db["quotes"])]
    st.dataframe(pd.DataFrame(rows).drop(columns=["ID"]), use_container_width=True, hide_index=True)
    selected_quote = st.selectbox("Afficher / exporter un devis", db["quotes"], format_func=lambda q: f"{q['number']} — {q.get('client_name', '')} — {q.get('total', 0):,.2f} DA")
    client = clients_by_id.get(selected_quote.get("client_id"), {"name": selected_quote.get("client_name", "")})
    pdf_bytes = document_pdf("DEVIS", selected_quote, client, "devis")
    st.download_button("📄 Télécharger le devis en PDF", pdf_bytes, f"{selected_quote['number']}.pdf", "application/pdf")
    col1, col2 = st.columns(2)
    with col1:
        new_status = st.selectbox("Statut du devis", ["En attente", "Accepté", "Refusé", "Expiré"], index=["En attente", "Accepté", "Refusé", "Expiré"].index(selected_quote.get("status", "En attente")) if selected_quote.get("status", "En attente") in ["En attente", "Accepté", "Refusé", "Expiré"] else 0)
    with col2:
        if st.button("Mettre à jour le statut"):
            update_record("quotes", selected_quote["id"], {"status": new_status})
            st.success("Statut mis à jour.")
            st.rerun()
else:
    st.info("Aucun devis pour le moment.")
