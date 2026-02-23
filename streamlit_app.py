import streamlit as st

# Configuration de la page
st.set_page_config(page_title="ERP SASU", layout="centered")

# Titre principal
st.title("📊 Mon ERP SASU Mobile")

# Menu sur le côté
menu = st.sidebar.selectbox("Menu", ["Stock", "Ventes", "Paramètres"])

if menu == "Stock":
    st.subheader("📦 Gestion du Stock")
    with st.form("ajout_produit"):
        nom = st.text_input("Nom du produit")
        qte = st.number_input("Quantité", min_value=0, step=1)
        prix = st.number_input("Prix d'achat unitaire (€)", min_value=0.0, step=0.01)
        
        btn = st.form_submit_button("Enregistrer le produit")
        
        if btn:
            if nom:
                st.success(f"✅ {nom} ajouté (Quantité: {qte})")
            else:
                st.error("⚠️ Donne un nom au produit")

elif menu == "Ventes":
    st.subheader("💰 Enregistrer une Vente")
    st.write("Interface de vente à venir...")

elif menu == "Paramètres":
    st.subheader("⚙️ Configuration")
    st.write("Ici on branchera ton Google Sheets prochainement.")

st.divider()
st.caption("Président : SASU (Unremunerated)")
