import streamlit as st
import pandas as pd
import requests

# -----------------------------
# CONFIG
# -----------------------------
API_URL = "http://localhost:54300/service_training_recomendation/"
st.set_page_config(page_title="BSK Training Recommendation Dashboard", layout="wide")

# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data
def load_recommendations(limit=500):
    response = requests.get(API_URL, params={"limit": limit})
    response.raise_for_status()
    return response.json()

data = load_recommendations()

df = pd.json_normalize(data, sep="_")

# -----------------------------
# SIDEBAR FILTERS
# -----------------------------
st.sidebar.title("🔍 Filters")

districts = sorted(df["district_name"].dropna().unique())
selected_district = st.sidebar.selectbox("District", ["All"] + districts)

bsk_types = sorted(df["bsk_type"].dropna().unique())
selected_bsk_type = st.sidebar.selectbox("BSK Type", ["All"] + bsk_types)

min_priority = st.sidebar.slider(
    "Minimum Priority Score",
    min_value=0.0,
    max_value=float(df["priority_score"].max()),
    value=0.0,
)

top_n = st.sidebar.slider("Top N BSKs", 10, 200, 100)

# Apply filters
filtered_df = df.copy()
if selected_district != "All":
    filtered_df = filtered_df[filtered_df["district_name"] == selected_district]

if selected_bsk_type != "All":
    filtered_df = filtered_df[filtered_df["bsk_type"] == selected_bsk_type]

filtered_df = filtered_df[filtered_df["priority_score"] >= min_priority]
filtered_df = filtered_df.nlargest(top_n, "priority_score")

# -----------------------------
# HEADER
# -----------------------------
st.title("🎓 BSK & DEO Training Recommendation Dashboard")
st.markdown(
    f"""
**Total BSKs needing training:** `{len(filtered_df)}`  
**Total priority score:** `{filtered_df['priority_score'].sum():.2f}`
"""
)

# -----------------------------
# TABS
# -----------------------------
tab1, tab2, tab3, tab4 = st.tabs(
    ["🏢 BSK / DEO View", "📍 District-wise", "📊 Service-wise", "⬇️ Download"]
)

# ==========================================================
# TAB 1 – BSK / DEO VIEW
# ==========================================================
with tab1:
    bsk_options = (
        filtered_df[["bsk_id", "bsk_name"]]
        .drop_duplicates()
        .apply(lambda x: f"{x.bsk_name} (ID: {x.bsk_id})", axis=1)
        .tolist()
    )

    selected_bsk = st.selectbox("Select BSK", bsk_options)

    bsk_id = int(selected_bsk.split("ID:")[1].replace(")", "").strip())
    bsk_data = filtered_df[filtered_df["bsk_id"] == bsk_id].iloc[0]

    col1, col2, col3 = st.columns(3)

    col1.metric("District", bsk_data["district_name"])
    col2.metric("Block", bsk_data["block_municipalty_name"])
    col3.metric("Priority Score", round(bsk_data["priority_score"], 2))

    st.subheader("🏢 BSK Details")
    st.json(
        {
            "BSK Code": bsk_data["bsk_code"],
            "BSK Type": bsk_data["bsk_type"],
            "Cluster ID": int(bsk_data["cluster_id"]),
            "Latitude": bsk_data["bsk_lat"],
            "Longitude": bsk_data["bsk_long"],
        }
    )

    st.subheader("👥 DEOs Assigned")
    if bsk_data["deos"]:
        st.table(pd.DataFrame(bsk_data["deos"]))
    else:
        st.info("No DEOs assigned")

    st.subheader("📚 Services Needing Training")
    service_df = pd.DataFrame(bsk_data["recommended_services"])
    st.dataframe(
        service_df[
            [
                "service_name",
                "service_type",
                "current_provisions",
                "cluster_avg_provisions",
                "gap",
            ]
        ],
        use_container_width=True,
    )

# ==========================================================
# TAB 2 – DISTRICT-WISE SUMMARY
# ==========================================================
with tab2:
    district_summary = (
        filtered_df.groupby("district_name")
        .agg(
            bsks=("bsk_id", "nunique"),
            total_services=("total_training_services", "sum"),
            total_priority=("priority_score", "sum"),
        )
        .reset_index()
        .sort_values("total_priority", ascending=False)
    )

    st.subheader("📍 District-wise Training Need")
    st.dataframe(district_summary, use_container_width=True)

# ==========================================================
# TAB 3 – SERVICE-WISE SUMMARY
# ==========================================================
with tab3:
    service_rows = []
    for _, row in filtered_df.iterrows():
        for svc in row["recommended_services"]:
            service_rows.append(
                {
                    "service_name": svc["service_name"],
                    "service_type": svc["service_type"],
                    "gap": svc["gap"],
                }
            )

    service_df = pd.DataFrame(service_rows)

    service_summary = (
        service_df.groupby(["service_name", "service_type"])
        .agg(
            bsks=("gap", "count"),
            total_gap=("gap", "sum"),
        )
        .reset_index()
        .sort_values("bsks", ascending=False)
    )

    st.subheader("📊 Service-wise Training Demand")
    st.dataframe(service_summary, use_container_width=True)

# ==========================================================
# TAB 4 – DOWNLOAD
# ==========================================================
with tab4:
    csv = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download Training Recommendation (CSV)",
        csv,
        "training_recommendations.csv",
        "text/csv",
    )
