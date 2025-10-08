import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from modules import storage

def render():
    st.header("📉 Trends")
    data = storage.load_json(storage.DATA_FILE, {"netto": 0, "kosten": []})
    history = storage.load_json(storage.HISTORY_FILE, [])

    if st.button("📅 Monatsabschluss speichern"):
        month = datetime.now().strftime("%Y-%m")
        eintrag = {
            "datum": month,
            "einkommen": data.get("netto",0),
            "kosten": sum(k.get("Betrag",0) for k in data.get("kosten", [])),
            "uebrig": data.get("netto",0) - sum(k.get("Betrag",0) for k in data.get("kosten", []))
        }
        history = [h for h in history if h.get("datum") != month] + [eintrag]
        storage.save_json(storage.HISTORY_FILE, history)
        st.success(f"Monat {month} gespeichert.")

    if len(history) >= 1:
        df = pd.DataFrame(history).sort_values("datum")
        if len(df) >= 2:
            fig = px.line(df, x="datum", y=["uebrig", "kosten"], title="Monatsentwicklung", color_discrete_sequence=["#00C896", "#FF6666"])
            st.plotly_chart(fig, use_container_width=True)
            # Simple trend messages
            if len(df) >= 3:
                df['diff'] = df['uebrig'].diff()
                last_diff = df['diff'].iloc[-1]
                if last_diff < 0:
                    st.warning(f"Verfügbares Einkommen gesunken um {abs(last_diff):.2f} € seit letztem Monat.")
                else:
                    st.success(f"Verfügbares Einkommen gestiegen um {last_diff:.2f} € seit letztem Monat.")
        else:
            st.info("Mindestens 2 Monate nötig für Zeitreihe (aktuell 1 gespeichert).")
    else:
        st.info("Keine Historie vorhanden.")
