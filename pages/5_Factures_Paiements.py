from datetime import date, timedelta
import pandas as pd
import streamlit as st
from atelier_pvc.store import load_db, create_record, update_record
from atelier_pvc.pdf import document_pdf

st.set_page_config(page_title="Factures et paiements | Atelier PVC Pro", page_icon="💳", layout="wide")
st.title("💳 Factures et paiements")
db = load_db()

with st.expander("➕ Créer une facture depuis un devis accepté"):
    accepted = [q for q in db["quotes"] if q.get("status") == "Accepté"]
    invoice_quote_ids = {i.get("quote_id") for i in db["invoices"]}
    available = [q for q in accepted if q.get("id") not in invoice_quote_ids]
    if not available:
        st.info("Aucun devis accepté sans facture. Accepte d'abord un devis dans la page Devis.")
    else:
        choices = {f"{q['number']} — {q.get('client_name', '')} — {q['total']:,.2f} DA": q for q in available}
        selected_label = st.selectbox("Devis à facturer", list(choices))
        due_days = st.number_input("Délai de paiement (jours)", min_value=0, max_value=365, value=30, step=1)
        if st.button("Créer la facture", use_container_width=True):
            quote = choices[selected_label]
            number = f"FAC-{date.today():%Y%m%d}-{len(db['invoices']) + 1:04d}"
            create_record("invoices", {"number": number, "date": date.today().isoformat(), "due_date": (date.today() + timedelta(days=int(due_days))).isoformat(), "quote_id": quote["id"], "client_id": quote.get("client_id"), "client_name": quote.get("client_name", ""), "lines": quote.get("lines", []), "subtotal": quote.get("subtotal", quote["total"]), "tax": quote.get("tax", 0), "total": float(quote["total"]), "paid": 0.0, "status": "À payer", "notes": quote.get("notes", "")})
            st.success(f"Facture {number} créée.")
            st.rerun()

db = load_db()
st.subheader("État des factures")
if db["invoices"]:
    rows = [{"Facture": i["number"], "Date": i["date"], "Échéance": i.get("due_date", ""), "Client": i.get("client_name", ""), "Total (DA)": i["total"], "Payé (DA)": i.get("paid", 0), "Reste (DA)": round(float(i["total"]) - float(i.get("paid", 0)), 2), "Statut": i.get("status", "À payer")} for i in db["invoices"]]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    choices = {f"{i['number']} — {i.get('client_name')} — reste {float(i['total']) - float(i.get('paid', 0)):,.2f} DA": i for i in db["invoices"]}
    selected = st.selectbox("Facture à consulter", list(choices))
    invoice = choices[selected]
    clients = {c["id"]: c for c in db["clients"]}
    pdf_bytes = document_pdf("FACTURE", invoice, clients.get(invoice.get("client_id"), {"name": invoice.get("client_name", "")}), "facture")
    st.download_button("📄 Télécharger la facture en PDF", pdf_bytes, f"{invoice['number']}.pdf", "application/pdf")
    remaining = round(float(invoice["total"]) - float(invoice.get("paid", 0)), 2)
    if remaining > 0:
        with st.form("record_payment"):
            amount = st.number_input("Montant du paiement (DA)", min_value=0.01, max_value=float(remaining), value=min(float(remaining), 1000.0), step=100.0)
            method = st.selectbox("Mode de paiement", ["Espèces", "Virement", "Chèque", "Carte", "Autre"])
            note = st.text_input("Référence / note")
            submitted = st.form_submit_button("Enregistrer le paiement")
        if submitted:
            db = load_db()
            latest = next((i for i in db["invoices"] if i["id"] == invoice["id"]), None)
            if not latest:
                st.error("Facture introuvable.")
            elif amount > round(float(latest["total"]) - float(latest.get("paid", 0)), 2):
                st.error("Le montant dépasse le reste à payer.")
            else:
                create_record("payments", {"invoice_id": invoice["id"], "invoice_number": invoice["number"], "client_name": invoice.get("client_name", ""), "date": date.today().isoformat(), "amount": round(float(amount), 2), "method": method, "note": note.strip()})
                new_paid = round(float(latest.get("paid", 0)) + float(amount), 2)
                status = "Payée" if new_paid >= float(latest["total"]) else "Partiellement payée"
                update_record("invoices", invoice["id"], {"paid": new_paid, "status": status})
                st.success("Paiement enregistré.")
                st.rerun()
else:
    st.info("Aucune facture pour le moment.")

st.subheader("Historique des paiements")
db = load_db()
if db["payments"]:
    st.dataframe(pd.DataFrame([{ "Date": p.get("date"), "Facture": p.get("invoice_number"), "Client": p.get("client_name"), "Montant (DA)": p.get("amount"), "Mode": p.get("method"), "Note": p.get("note", "") } for p in reversed(db["payments"])]), use_container_width=True, hide_index=True)
else:
    st.info("Aucun paiement enregistré.")
