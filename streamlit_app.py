import streamlit as st
from datetime import datetime, timedelta
import pandas as pd

# App Design & Setup
st.set_page_config(page_title="Discounter Journal", page_icon="📈", layout="wide")
st.title("📈 Mein Privates Discounter-Premium-Journal")

# Datenbank im Browser-Arbeitsspeicher (Session State) initialisieren
if "trades_list" not in st.session_state:
    st.session_state.trades_list = []

# Trade-Historie als Tabelle aufbereiten
trade_history = pd.DataFrame(st.session_state.trades_list, columns=[
    "Aktie", "Kaufdatum", "Kaufpreis (€)", "Cap (€)", 
    "Verkaufsdatum", "Verkaufspreis (€)", "Haltedauer (Tage)", 
    "Gewinn (%)", "Gewinn (€)", "Rendite p.a. (%)"
])

# Layout aufteilen: Links Eingabe, Rechts Statistik & Grafik
col_eingabe, col_stats = st.columns()

with col_eingabe:
    st.header("📌 Neuen Trade eintragen")
    aktie = st.text_input("Name der Aktie / Basiswert", "Gold / Silber / Aktie X")
    
    k_dat = st.date_input("Kaufdatum", datetime.now() - timedelta(days=5))
    k_preis = st.number_input("Kaufpreis des Scheins (€)", min_value=0.01, value=10.00, step=0.10)
    
    cap_wert = st.number_input("Cap des Scheins (€)", min_value=0.01, value=12.50, step=0.10)
    v_dat = st.date_input("Verkaufsdatum", datetime.now())
    v_preis = st.number_input("Verkaufspreis des Scheins (€)", min_value=0.01, value=12.00, step=0.10)

    if st.button("🚀 Trade hinzufügen"):
        haltedauer = (v_dat - k_dat).days
        if haltedauer <= 0: haltedauer = 1
        
        gewinn_eur = v_preis - k_preis
        gewinn_proz = (gewinn_eur / k_preis) * 100
        
        # Rendite p.a. mit Zinseszins
        jahresrendite = ((v_preis / k_preis) ** (365 / haltedauer) - 1) * 100
        
        neuer_eintrag = {
            "Aktie": aktie,
            "Kaufdatum": k_dat,
            "Kaufpreis (€)": round(k_preis, 2),
            "Cap (€)": round(cap_wert, 2),
            "Verkaufsdatum": v_dat,
            "Verkaufspreis (€)": round(v_preis, 2),
            "Haltedauer (Tage)": haltedauer,
            "Gewinn (%)": round(gewinn_proz, 2),
            "Gewinn (€)": round(gewinn_eur, 2),
            "Rendite p.a. (%)": round(jahresrendite, 2)
        }
        
        st.session_state.trades_list.append(neuer_eintrag)
        st.success("Erfolgreich hinzugefügt!")
        st.rerun()

with col_stats:
    st.header("📊 Deine Auswertungen & Grafiken")
    
    if not trade_history.empty:
        # Kennzahlen berechnen
        gesamt_gewinn = trade_history["Gewinn (€)"].sum()
        avg_haltedauer = trade_history["Haltedauer (Tage)"].mean()
        avg_pa = trade_history["Rendite p.a. (%)"].mean()
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Gesamtgewinn", f"{gesamt_gewinn:.2f} €")
        c2.metric("Ø Haltedauer", f"{avg_haltedauer:.1f} Tage")
        c3.metric("Ø Jahresrendite (p.a.)", f"{avg_pa:,.1f} %")
        
        st.markdown("---")
        st.subheader("🖼️ Visuelle Performance")
        
        col_grafik1, col_grafik2 = st.columns(2)
        
        with col_grafik1:
            st.write("**Kapital-Wachstum (Gewinnverlauf addiert):**")
            trade_history["Kontoverlauf (€)"] = trade_history["Gewinn (€)"].cumsum()
            st.line_chart(trade_history, x="Verkaufsdatum", y="Kontoverlauf (€)", color="#2ea44f")
            
        with col_grafik2:
            st.write("**Effizienz: Gewinn (%) nach Haltedauer (Tage):**")
            st.bar_chart(trade_history, x="Haltedauer (Tage)", y="Gewinn (%)", color="#1f77b4")
            
        st.markdown("---")
        st.subheader("📋 Eingetragene Trades")
        st.dataframe(trade_history.drop(columns=["Kontoverlauf (€)"], errors="ignore"), use_container_width=True)
        
        if st.button("🗑️ Historie zurücksetzen"):
            st.session_state.trades_list = []
            st.rerun()
    else:
        st.info("Trage links deinen ersten Test-Trade ein, um die Live-Grafiken und Tabellen auf dem Bildschirm zu erzeugen!")
