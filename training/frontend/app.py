import streamlit as st
import requests

# Configure the page
st.set_page_config(
    page_title="BSK Training Optimization",
    page_icon="🎓",
    layout="wide"
)

st.title("BSK Training Optimization System")
st.markdown("""
Welcome to the BSK Training Optimization System!\
Use the sidebar to navigate to different data views and analytics.\
Each section provides interactive tables and visualizations for your data.\
""") 

# Fetch data for overview
API_BASE_URL = "http://localhost:54300"

def fetch_all_data(endpoint):
    try:
        response = requests.get(f"{API_BASE_URL}/{endpoint}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching {endpoint}: {e}")
        return []

bsk_centers = fetch_all_data("bsk/")
deos = fetch_all_data("deo/")
services = fetch_all_data("services/")

num_bsks = len(bsk_centers) if bsk_centers else 0
num_deos = len(deos) if deos else 0
num_services = len(services) if services else 0

# Display summary info at the top
st.markdown("### System Overview")
col_a, col_b, col_c = st.columns(3)
col_a.metric("Total BSKs", num_bsks)
col_b.metric("Total DEOs", num_deos)
col_c.metric("Total Services", num_services) 