import streamlit as st
from modules import inputs, dashboard, trends, investments

st.set_page_config(page_title="Finanzplaner Smart+", page_icon="💰", layout="wide")

# load CSS
try:
    with open("assets/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except Exception:
    pass

tab = st.sidebar.radio("Navigation", ["📥 Eingaben", "📊 Dashboard", "📉 Trends", "💰 Investments"])

if tab == "📥 Eingaben":
    inputs.render()
elif tab == "📊 Dashboard":
    dashboard.render()
elif tab == "📉 Trends":
    trends.render()
elif tab == "💰 Investments":
    investments.render()
