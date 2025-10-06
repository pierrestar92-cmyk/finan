# Datei: finanzplaner_pwa.py
import streamlit as st
import pandas as pd
import math
import altair as alt

st.set_page_config(page_title="Finanzplaner", page_icon="💰", layout="centered")

# --- CSS für mobiles Layout ---
st.markdown("""
    <style>
    body { font-family: 'Inter', sans-serif; }
    .block-container { padding-top: 1rem; padding-bottom: 1rem; }
    </style>
""", unsafe_allow_html=True)

# --- Kopfbereich ---
st.title("💰 Finanzplaner & Investitionsrechner")
st.caption("Berechne dein verfügbares Budget und simuliere mögliche Investments.")

# --- Eingaben ---
st.header("1️⃣ Monatliche Finanzen")

netto = st.number_input("Monatliches Netto-Einkommen (€)", min_value=0.0, step=100.0)

anzahl_kosten = st.number_input("Anzahl Fixkosten", min_value=0, max_value=20, step=1)
kosten_namen, kosten_betraege = [], []

for i in range(int(anzahl_kosten)):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input(f"Kosten #{i+1} – Name", key=f"name_{i}")
    with col2:
        betrag = st.number_input(f"Kosten #{i+1} – Betrag (€)", min_value=0.0, step=10.0, key=f"betrag_{i}")
    if name:
        kosten_namen.append(name)
        kosten_betraege.append(betrag)

gesamt_kosten = sum(kosten_betraege)
verbleibend = netto - gesamt_kosten

st.subheader("💡 Ergebnis")
st.write(f"**Gesamte Fixkosten:** {gesamt_kosten:,.2f} €")
st.write(f"**Verfügbar zum Investieren:** {verbleibend:,.2f} €")

if verbleibend > 0:
    st.success("Du hast Geld übrig zum Investieren 💪")
elif verbleibend == 0:
    st.info("Du liegst bei ±0 – kein Puffer.")
else:
    st.error("Du gibst mehr aus, als du einnimmst ❌")

# --- Diagramme ---
if kosten_namen:
    df = pd.DataFrame({"Kostenpunkt": kosten_namen, "Betrag (€)": kosten_betraege})
    st.subheader("📊 Kostenverteilung")
    chart = alt.Chart(df).mark_arc().encode(
        theta="Betrag (€)",
        color="Kostenpunkt",
        tooltip=["Kostenpunkt", "Betrag (€)"]
    )
    st.altair_chart(chart, use_container_width=True)

    df_bar = pd.DataFrame({
        "Kategorie": ["Einkommen", "Fixkosten", "Verfügbar"],
        "Betrag (€)": [netto, gesamt_kosten, verbleibend]
    })
    st.subheader("📈 Budgetübersicht")
    bar = alt.Chart(df_bar).mark_bar().encode(
        x="Kategorie",
        y="Betrag (€)",
        color="Kategorie",
        tooltip=["Kategorie", "Betrag (€)"]
    )
    st.altair_chart(bar, use_container_width=True)

# --- Investitionssimulation ---
st.header("2️⃣ Investitionssimulation")

monatl_invest = st.number_input("Monatlicher Investitionsbetrag (€)", min_value=0.0, value=max(0.0, verbleibend))
jahre = st.slider("Anlagezeitraum (Jahre)", 1, 40, 10)
rendite = st.slider("Durchschnittliche Jahresrendite (%)", 0.0, 15.0, 5.0, step=0.1)

def endwert(monatlich, jahre, zinssatz):
    r = zinssatz / 100 / 12
    n = jahre * 12
    if r == 0:
        return monatlich * n
    return monatlich * ((math.pow(1 + r, n) - 1) / r)

endbetrag = endwert(monatl_invest, jahre, rendite)
eingezahlt = monatl_invest * jahre * 12
gewinn = endbetrag - eingezahlt

st.write(f"📦 Nach **{jahre} Jahren** hättest du etwa **{endbetrag:,.2f} €**, davon sind **{gewinn:,.2f} €** Gewinn.")

if monatl_invest > 0:
    st.subheader("💹 Entwicklung über Zeit")
    data = pd.DataFrame({
        "Jahr": list(range(1, jahre + 1)),
        "Wert": [endwert(monatl_invest, j, rendite) for j in range(1, jahre + 1)]
    })
    chart2 = alt.Chart(data).mark_line(point=True).encode(x="Jahr", y="Wert", tooltip=["Jahr", "Wert"])
    st.altair_chart(chart2, use_container_width=True)

# --- PWA Manifest ---
st.markdown(
    """
    <link rel="manifest" href="manifest.json">
    <script>
      if ('serviceWorker' in navigator) {
          navigator.serviceWorker.register('service-worker.js');
      }
    </script>
    """,
    unsafe_allow_html=True
)
