import streamlit as st
import pandas as pd
from modules import storage

def render():
    st.header("📥 Eingaben")
    data = storage.load_json(storage.DATA_FILE, {"netto": 0, "kosten": []})

    data["netto"] = st.number_input("Nettoeinkommen (€)", min_value=0.0, step=100.0, value=float(data.get("netto", 0)))
    st.markdown("#### Fixkosten (Kategorie, Betrag)")

    default_df = pd.DataFrame(data["kosten"]) if data.get("kosten") else pd.DataFrame([{"Kategorie": "", "Betrag": 0.0}])
    kosten_df = st.data_editor(default_df, num_rows="dynamic", key="kosten_editor")

    new_kosten = []
    for _, row in kosten_df.iterrows():
        k = row.get("Kategorie") if "Kategorie" in row else row.get("name")
        b = row.get("Betrag") if "Betrag" in row else row.get("betrag")
        if k and b and float(b) > 0:
            new_kosten.append({"Kategorie": k, "Betrag": float(b)})

    data["kosten"] = new_kosten
    storage.save_json(storage.DATA_FILE, data)
    st.success("Daten gespeichert ✅")
