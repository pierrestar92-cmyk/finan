import streamlit as st
import pandas as pd
import plotly.express as px
from modules import storage

def render():
    st.header("📊 Dashboard")
    data = storage.load_json(storage.DATA_FILE, {"netto": 0, "kosten": []})

    netto = data.get("netto", 0)
    kosten = sum(k.get("Betrag",0) for k in data.get("kosten", []))
    uebrig = netto - kosten
    sparquote = (uebrig / netto) if netto else 0
    fixquote = (kosten / netto) if netto else 0
    investquote = min(sparquote, 0.3)

    def score(s, f, i):
        return round(min(max(s/0.2,0),1)*40 + min(max((0.7-f)/0.7,0),1)*30 + min(max(i/0.1,0),1)*30)
    def ampel_text(val):
        return "🟢 Sehr gut" if val>=80 else "🟡 Mittel" if val>=50 else "🔴 Kritisch"

    st.metric("Finanz-Score", f"{score(sparquote, fixquote, investquote)}/100", ampel_text(score(sparquote, fixquote, investquote)))
    st.metric("Sparquote", f"{sparquote*100:.1f} %")
    st.metric("Verfügbar", f"{uebrig:,.2f} €")

    if data.get("kosten"):
        df = pd.DataFrame(data["kosten"])
        fig = px.pie(df, names="Kategorie", values="Betrag", title="Kostenverteilung", color_discrete_sequence=px.colors.sequential.Teal)
        st.plotly_chart(fig, use_container_width=True)
