import streamlit as st
import pandas as pd
import plotly.express as px
import math
from modules import storage

def render():
    st.header("💰 Investment-Simulation")
    data = storage.load_json(storage.DATA_FILE, {"netto": 0, "kosten": []})
    netto = data.get("netto",0)
    kosten = sum(k.get("Betrag",0) for k in data.get("kosten", []))
    uebrig = netto - kosten

    col1, col2, col3 = st.columns(3)
    monat = col1.number_input("Monatliche Investition (€)", min_value=0.0, step=10.0, value=max(0.0, uebrig*0.3))
    rendite = col2.number_input("Erwartete Rendite (% p.a.)", min_value=0.0, max_value=20.0, value=5.0)
    jahre = col3.number_input("Dauer (Jahre)", min_value=1, max_value=50, value=10)

    r = rendite / 100 / 12
    n = jahre * 12
    endwert = monat * (((1 + r)**n - 1) / r) if r > 0 else monat * n
    gesamt = monat * n
    gewinn = endwert - gesamt

    st.metric("Endvermögen", f"{endwert:,.2f} €")
    st.metric("Gesamt investiert", f"{gesamt:,.2f} €")
    st.metric("Gewinn", f"{gewinn:,.2f} €")

    df = pd.DataFrame({"Monat": range(1, int(n)+1), "Vermögen": [monat * (((1+r)**i - 1)/r) for i in range(1, int(n)+1)]})
    fig = px.line(df, x="Monat", y="Vermögen", title="Wachstum", color_discrete_sequence=["#00C896"])
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("🎯 Sparziel")
    ziel = st.number_input("Zielbetrag (€)", min_value=0.0, step=1000.0, value=100000.0)
    if monat > 0 and r > 0:
        monate_bis_ziel = math.log(1 + ziel * r / monat) / math.log(1 + r)
        st.write(f"Ziel erreicht in **{monate_bis_ziel/12:.1f} Jahren**.")
    else:
        st.info("Bitte Rendite und Investition angeben.")
