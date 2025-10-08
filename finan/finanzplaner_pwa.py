import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd
import math
import plotly.express as px

# === App Setup ===
st.set_page_config(page_title="Finanzplaner Smart+ Ultra", page_icon="💰", layout="wide")

# === Custom CSS ===
st.markdown("""
    <style>
        :root {
            --primary: #00C896;
            --bg-dark: #1E1E1E;
            --text-light: #EAEAEA;
            --card-bg: #2B2B2B;
        }
        body {
            color: var(--text-light);
            background-color: var(--bg-dark);
        }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        h1, h2, h3, h4 {
            color: var(--primary);
        }
        div[data-testid="stMetricValue"] {
            color: var(--primary);
        }
        .stButton>button {
            background-color: var(--primary);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.6rem 1.2rem;
        }
        .stButton>button:hover {
            background-color: #00b387;
        }
        .stDataFrame {
            background-color: var(--card-bg);
        }
        .stAlert {
            border-radius: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# === Files & Parameters ===
DATA_FILE = "finanzdaten.json"
HISTORY_FILE = "finanzverlauf.json"
REMINDER_DAYS = 30

# === Utility Functions ===
def load_json(path, default):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return default

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def days_since_last_month(history):
    if not history:
        return None
    last = max(h["datum"] for h in history)
    last_date = datetime.strptime(last + "-01", "%Y-%m-%d")
    return (datetime.now() - last_date).days

def calculate_ampel_score(sparquote, fixquote, investquote):
    score = 0
    score += min(max(sparquote / 0.2, 0), 1) * 40
    score += min(max((0.7 - fixquote) / 0.7, 0), 1) * 30
    score += min(max(investquote / 0.1, 0), 1) * 30
    return round(score)

def ampel_color(score):
    if score >= 80:
        return "🟢 Sehr gut"
    elif score >= 50:
        return "🟡 Mittel"
    else:
        return "🔴 Kritisch"

# === Daten laden ===
data = load_json(DATA_FILE, {"netto": 0, "kosten": []})
history = load_json(HISTORY_FILE, [])

# === Erinnerung ===
days_last = days_since_last_month(history)
if days_last and days_last > REMINDER_DAYS:
    st.warning(f"🔔 {days_last} Tage seit letztem Monatsabschluss – Zeit für ein Update!")

# === Titel ===
st.markdown("<h1>💰 Finanzplaner Smart+ Ultra</h1>", unsafe_allow_html=True)
st.caption("Darkmode | Finanzanalyse | Investment-Simulation | Dashboard")

# === Eingaben ===
st.markdown("## 📥 Eingaben")
data["netto"] = st.number_input("Nettoeinkommen (€)", min_value=0.0, value=float(data.get("netto", 0)), step=100.0)

st.markdown("#### Fixkosten")
kosten_table = st.data_editor(
    pd.DataFrame(data["kosten"] or [{"Kategorie": "", "Betrag": 0.0}]),
    num_rows="dynamic",
    key="kosten_table"
)
data["kosten"] = [
    {"Kategorie": row["Kategorie"], "Betrag": float(row["Betrag"])}
    for _, row in kosten_table.iterrows() if row["Kategorie"] and row["Betrag"] > 0
]
save_json(DATA_FILE, data)

# === Berechnungen ===
gesamt_kosten = sum(k["Betrag"] for k in data["kosten"])
uebrig = data["netto"] - gesamt_kosten
sparquote = uebrig / data["netto"] if data["netto"] else 0
fixquote = gesamt_kosten / data["netto"] if data["netto"] else 0
investquote = min(sparquote, 0.3)

# === Übersicht ===
st.markdown("## 📊 Übersicht")
col1, col2, col3 = st.columns(3)
col1.metric("Fixkosten", f"{gesamt_kosten:,.2f} €")
col2.metric("Verfügbar", f"{uebrig:,.2f} €")
col3.metric("Sparquote", f"{sparquote*100:.1f} %")

# === Finanz-Ampel ===
st.markdown("## 🧭 Finanz-Ampel")
score = calculate_ampel_score(sparquote, fixquote, investquote)
st.metric("Finanz-Score", f"{score}/100", ampel_color(score))

# === Diagramm: Kostenaufteilung ===
if data["kosten"]:
    st.markdown("### 🥧 Kostenaufteilung")
    df_kosten = pd.DataFrame(data["kosten"])
    fig_pie = px.pie(df_kosten, names="Kategorie", values="Betrag", title="Fixkosten-Verteilung", color_discrete_sequence=px.colors.sequential.Teal)
    st.plotly_chart(fig_pie, use_container_width=True)

# === Monatsabschluss ===
if st.button("📅 Monatsabschluss speichern"):
    month = datetime.now().strftime("%Y-%m")
    entry = {
        "datum": month,
        "einkommen": data["netto"],
        "kosten": gesamt_kosten,
        "uebrig": uebrig,
        "sparquote": sparquote,
    }
    history = [h for h in history if h["datum"] != month] + [entry]
    save_json(HISTORY_FILE, history)
    st.success(f"Monat {month} gespeichert.")

# === Trendanalyse ===
st.markdown("## 📉 Trendanalyse")
if len(history) >= 3:
    df = pd.DataFrame(history).sort_values("datum")
    df["diff"] = df["uebrig"].diff()
    last_diff = df["diff"].iloc[-1]
    trend = "steigend" if last_diff > 0 else "sinkend"

    st.write(f"Trend: **{trend}** ({last_diff:+.2f} € Veränderung).")

    avg_savings = df["sparquote"].tail(3).mean() * 100
    if avg_savings < 10:
        st.warning(f"⚠️ Durchschnittliche Sparquote {avg_savings:.1f}% → Ziel ≥ 20%.")
    elif avg_savings < 20:
        st.info(f"ℹ️ Sparquote {avg_savings:.1f}% – verbesserbar.")
    else:
        st.success(f"✅ Starke Sparquote {avg_savings:.1f}%.")

    fig_line = px.line(df, x="datum", y=["uebrig", "kosten"], title="Monatsüberschuss & Kostenverlauf", color_discrete_sequence=["#00C896", "#FF6666"])
    st.plotly_chart(fig_line, use_container_width=True)
else:
    st.info("Mindestens 3 Monate speichern, um Trends zu erkennen.")

# === Investment-Simulation ===
st.markdown("## 💰 Investment-Simulation")
col1, col2, col3 = st.columns(3)
monat_invest = col1.number_input("Monatliche Investition (€)", min_value=0.0, step=50.0, value=max(0.0, uebrig*0.3))
jahres_rendite = col2.number_input("Erwartete Rendite (% p.a.)", min_value=0.0, max_value=20.0, value=5.0)
jahre = col3.number_input("Anlagedauer (Jahre)", min_value=1, max_value=50, value=10)

r = jahres_rendite / 100 / 12
n = jahre * 12
endwert = monat_invest * (((1 + r) ** n - 1) / r) if r > 0 else monat_invest * n
gesamt_investiert = monat_invest * n
gewinn = endwert - gesamt_investiert

st.markdown("### 📈 Ergebnis")
c1, c2, c3 = st.columns(3)
c1.metric("Endvermögen", f"{endwert:,.2f} €")
c2.metric("Gesamt investiert", f"{gesamt_investiert:,.2f} €")
c3.metric("Zins-Gewinn", f"{gewinn:,.2f} €")

timeline = [monat_invest * (((1 + r) ** i - 1) / r) for i in range(1, int(n)+1)]
growth_df = pd.DataFrame({"Monat": range(1, int(n)+1), "Vermögen": timeline})
fig_growth = px.line(growth_df, x="Monat", y="Vermögen", title="Investment-Wachstum", color_discrete_sequence=["#00C896"])
st.plotly_chart(fig_growth, use_container_width=True)

# === Sparziel-Rechner ===
st.markdown("### 🎯 Sparziel-Rechner")
ziel = st.number_input("Zielbetrag (€)", min_value=0.0, step=1000.0, value=100000.0)
if monat_invest > 0 and r > 0:
    needed_months = math.log(1 + ziel * r / monat_invest) / math.log(1 + r)
    years = needed_months / 12
    st.write(f"Du erreichst dein Ziel in **{years:.1f} Jahren**.")
else:
    st.info("Bitte gültige Rendite und Investition angeben.")
