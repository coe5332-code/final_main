import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go

# Configuration
API_URL = "http://localhost:54300/service_training_recomendation/"

st.set_page_config(
    page_title="BSK Training Recommendations",
    page_icon="🎯",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    
    .priority-high {
        background-color: #ff4757;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 15px;
        font-weight: bold;
    }
    
    .priority-medium {
        background-color: #ffa502;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 15px;
        font-weight: bold;
    }
    
    .priority-low {
        background-color: #2ed573;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 15px;
        font-weight: bold;
    }
    
    .bsk-detail-card {
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        background: white;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data(ttl=300)
def load_recommendations(limit=500):
    try:
        response = requests.get(API_URL, params={"limit": limit})
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching recommendations: {e}")
        return []

# Header
st.title("🎯 BSK & DEO Training Recommendations")
st.markdown("**Prioritized training needs based on service gap analysis**")
st.markdown("---")

# Sidebar filters
with st.sidebar:
    st.markdown("### 🔍 Filters")
    
    data_limit = st.slider("Number of BSKs to load", 100, 1000, 500, 50)
    data = load_recommendations(limit=data_limit)
    
    if not data:
        st.error("No data available")
        st.stop()
    
    df = pd.json_normalize(data, sep="_")
    
    # District filter
    districts = sorted(df["district_name"].dropna().unique())
    selected_district = st.selectbox("District", ["All"] + districts)
    
    # BSK Type filter
    bsk_types = sorted(df["bsk_type"].dropna().unique())
    selected_bsk_type = st.selectbox("BSK Type", ["All"] + bsk_types)
    
    # Priority score filter
    min_priority = st.slider(
        "Minimum Priority Score",
        min_value=0.0,
        max_value=float(df["priority_score"].max()),
        value=0.0,
        step=0.1
    )
    
    # Top N filter
    top_n = st.slider("Top N BSKs", 10, 200, 100, 10)
    
    st.markdown("---")
    st.markdown("### 📊 View Options")
    show_map = st.checkbox("Show Geographic Map", value=True)
    show_deo_details = st.checkbox("Show DEO Details", value=True)

# Apply filters
filtered_df = df.copy()

if selected_district != "All":
    filtered_df = filtered_df[filtered_df["district_name"] == selected_district]

if selected_bsk_type != "All":
    filtered_df = filtered_df[filtered_df["bsk_type"] == selected_bsk_type]

filtered_df = filtered_df[filtered_df["priority_score"] >= min_priority]
filtered_df = filtered_df.nlargest(top_n, "priority_score")

# Summary metrics
st.markdown("## 📊 Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <h2 style="margin: 0;">{len(filtered_df)}</h2>
        <p style="margin: 0.5rem 0 0 0;">BSKs Needing Training</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    total_priority = filtered_df['priority_score'].sum()
    st.markdown(f"""
    <div class="metric-card">
        <h2 style="margin: 0;">{total_priority:.1f}</h2>
        <p style="margin: 0.5rem 0 0 0;">Total Priority Score</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    total_services = filtered_df['total_training_services'].sum()
    st.markdown(f"""
    <div class="metric-card">
        <h2 style="margin: 0;">{int(total_services)}</h2>
        <p style="margin: 0.5rem 0 0 0;">Total Service Gaps</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    avg_priority = filtered_df['priority_score'].mean()
    st.markdown(f"""
    <div class="metric-card">
        <h2 style="margin: 0;">{avg_priority:.2f}</h2>
        <p style="margin: 0.5rem 0 0 0;">Avg Priority Score</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Tabs for different views
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏢 BSK Details", 
    "📍 District Analysis", 
    "📊 Service Analysis",
    "🗺️ Geographic View",
    "⬇️ Export Data"
])

# TAB 1: BSK Details
with tab1:
    st.markdown("## 🏢 BSK & DEO Training Details")
    
    # BSK selector
    bsk_options = (
        filtered_df[["bsk_id", "bsk_name", "priority_score"]]
        .drop_duplicates()
        .sort_values("priority_score", ascending=False)
        .apply(lambda x: f"{x.bsk_name} (ID: {x.bsk_id}, Priority: {x.priority_score:.1f})", axis=1)
        .tolist()
    )
    
    selected_bsk = st.selectbox("Select BSK to view details", bsk_options)
    
    if selected_bsk:
        bsk_id = int(selected_bsk.split("ID:")[1].split(",")[0].strip())
        bsk_data = filtered_df[filtered_df["bsk_id"] == bsk_id].iloc[0]
        
        # BSK Information Card
        st.markdown('<div class="bsk-detail-card">', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("District", bsk_data["district_name"])
        with col2:
            st.metric("Block/Municipality", bsk_data["block_municipalty_name"])
        with col3:
            priority = bsk_data["priority_score"]
            priority_class = "priority-high" if priority > 70 else "priority-medium" if priority > 40 else "priority-low"
            st.markdown(f'<div class="{priority_class}">Priority: {priority:.1f}</div>', unsafe_allow_html=True)
        with col4:
            st.metric("Training Services Needed", int(bsk_data["total_training_services"]))
        
        st.markdown("---")
        
        # BSK Details
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🏢 BSK Information")
            st.json({
                "BSK Code": bsk_data["bsk_code"],
                "BSK Type": bsk_data["bsk_type"],
                "Cluster ID": int(bsk_data["cluster_id"]),
                "Latitude": bsk_data.get("bsk_lat", "N/A"),
                "Longitude": bsk_data.get("bsk_long", "N/A"),
            })
        
        with col2:
            st.markdown("### 📊 Performance Metrics")
            st.write(f"**Priority Score:** {bsk_data['priority_score']:.2f}")
            st.write(f"**Services Needing Training:** {int(bsk_data['total_training_services'])}")
            
            if 'avg_gap' in bsk_data:
                st.write(f"**Average Service Gap:** {bsk_data['avg_gap']:.2f}")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # DEO Information
        if show_deo_details and bsk_data["deos"]:
            st.markdown("### 👥 Data Entry Operators (DEOs)")
            deo_df = pd.DataFrame(bsk_data["deos"])
            
            st.dataframe(
                deo_df,
                use_container_width=True,
                hide_index=True
            )
        elif not bsk_data["deos"]:
            st.info("ℹ️ No DEOs currently assigned to this BSK")
        
        # Services needing training
        st.markdown("### 📚 Services Requiring Training")
        
        if bsk_data["recommended_services"]:
            service_df = pd.DataFrame(bsk_data["recommended_services"])
            
            # Add priority indicators
            service_df['Priority'] = service_df['gap'].apply(
                lambda x: '🔴 High' if x > 10 else '🟡 Medium' if x > 5 else '🟢 Low'
            )
            
            # Reorder columns
            display_cols = [
                "service_name",
                "service_type",
                "current_provisions",
                "cluster_avg_provisions",
                "gap",
                "Priority"
            ]
            
            st.dataframe(
                service_df[display_cols],
                use_container_width=True,
                hide_index=True
            )
            
            # Service gap visualization
            fig = px.bar(
                service_df.sort_values('gap', ascending=False).head(10),
                x='service_name',
                y='gap',
                title='Top 10 Service Gaps',
                color='gap',
                color_continuous_scale='Reds'
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("ℹ️ No specific service gaps identified")

# TAB 2: District Analysis
with tab2:
    st.markdown("## 📍 District-wise Training Needs")
    
    district_summary = (
        filtered_df.groupby("district_name")
        .agg(
            bsk_count=("bsk_id", "nunique"),
            total_services=("total_training_services", "sum"),
            total_priority=("priority_score", "sum"),
            avg_priority=("priority_score", "mean")
        )
        .reset_index()
        .sort_values("total_priority", ascending=False)
    )
    
    # District metrics
    col1, col2 = st.columns(2)
    
    with col1:
        # Bar chart: BSKs by district
        fig1 = px.bar(
            district_summary,
            x='district_name',
            y='bsk_count',
            title='BSKs Needing Training by District',
            color='total_priority',
            color_continuous_scale='RdYlGn_r'
        )
        fig1.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # Pie chart: Priority distribution
        fig2 = px.pie(
            district_summary,
            values='total_priority',
            names='district_name',
            title='Priority Distribution by District'
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    # Detailed table
    st.markdown("### 📊 Detailed District Summary")
    st.dataframe(
        district_summary.style.background_gradient(subset=['total_priority'], cmap='RdYlGn_r'),
        use_container_width=True,
        hide_index=True
    )

# TAB 3: Service Analysis
with tab3:
    st.markdown("## 📊 Service-wise Training Demand")
    
    # Extract all services from recommendations
    service_rows = []
    for _, row in filtered_df.iterrows():
        for svc in row["recommended_services"]:
            service_rows.append({
                "bsk_name": row["bsk_name"],
                "district_name": row["district_name"],
                "service_name": svc["service_name"],
                "service_type": svc["service_type"],
                "gap": svc["gap"],
                "current_provisions": svc["current_provisions"],
                "cluster_avg": svc["cluster_avg_provisions"]
            })
    
    if service_rows:
        service_df = pd.DataFrame(service_rows)
        
        service_summary = (
            service_df.groupby(["service_name", "service_type"])
            .agg(
                bsk_count=("gap", "count"),
                total_gap=("gap", "sum"),
                avg_gap=("gap", "mean"),
                avg_current=("current_provisions", "mean"),
                avg_cluster=("cluster_avg", "mean")
            )
            .reset_index()
            .sort_values("bsk_count", ascending=False)
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Top services by demand
            fig1 = px.bar(
                service_summary.head(15),
                x='service_name',
                y='bsk_count',
                title='Top 15 Services by Training Demand',
                color='total_gap',
                color_continuous_scale='Reds'
            )
            fig1.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # Service type distribution
            type_summary = service_summary.groupby('service_type')['bsk_count'].sum().reset_index()
            fig2 = px.pie(
                type_summary,
                values='bsk_count',
                names='service_type',
                title='Training Demand by Service Type'
            )
            st.plotly_chart(fig2, use_container_width=True)
        
        # Detailed service table
        st.markdown("### 📋 Complete Service Analysis")
        st.dataframe(
            service_summary.style.background_gradient(subset=['bsk_count', 'total_gap'], cmap='YlOrRd'),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No service data available")

# TAB 4: Geographic View
with tab4:
    st.markdown("## 🗺️ Geographic Distribution of Training Needs")
    
    if show_map and 'bsk_lat' in filtered_df.columns and 'bsk_long' in filtered_df.columns:
        map_df = filtered_df[['bsk_name', 'district_name', 'bsk_lat', 'bsk_long', 'priority_score']].copy()
        map_df = map_df.dropna(subset=['bsk_lat', 'bsk_long'])
        
        if not map_df.empty:
            fig = px.scatter_mapbox(
                map_df,
                lat='bsk_lat',
                lon='bsk_long',
                color='priority_score',
                size='priority_score',
                hover_name='bsk_name',
                hover_data={'district_name': True, 'priority_score': ':.2f'},
                color_continuous_scale='RdYlGn_r',
                zoom=6,
                height=600,
                title='BSK Training Priority Map'
            )
            fig.update_layout(mapbox_style="carto-darkmatter")
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("""
            **Map Legend:**
            - 🔴 Red: High priority (urgent training needed)
            - 🟡 Yellow: Medium priority
            - 🟢 Green: Lower priority
            - Larger dots indicate higher priority scores
            """)
        else:
            st.warning("No valid coordinates available for mapping")
    else:
        st.info("Geographic visualization disabled or coordinates not available")

# TAB 5: Export
with tab5:
    st.markdown("## ⬇️ Export Training Recommendations")
    
    st.markdown("""
    Export the current filtered results for further analysis or reporting.
    The exported data includes all BSK details, DEO information, and service recommendations.
    """)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Full export
        csv_full = filtered_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "📥 Download Full Dataset (CSV)",
            csv_full,
            "training_recommendations_full.csv",
            "text/csv",
            use_container_width=True
        )
    
    with col2:
        # Summary export
        summary_df = filtered_df[['bsk_name', 'district_name', 'block_municipalty_name', 
                                   'priority_score', 'total_training_services']].copy()
        csv_summary = summary_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "📥 Download Summary (CSV)",
            csv_summary,
            "training_recommendations_summary.csv",
            "text/csv",
            use_container_width=True
        )
    
    with col3:
        # District summary
        csv_district = district_summary.to_csv(index=False).encode("utf-8") if 'district_summary' in locals() else b""
        st.download_button(
            "📥 Download District Summary (CSV)",
            csv_district,
            "district_summary.csv",
            "text/csv",
            use_container_width=True,
            disabled=not csv_district
        )
    
    # Preview of export data
    with st.expander("📋 Preview Export Data", expanded=False):
        st.dataframe(filtered_df.head(20), use_container_width=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>Training recommendations are automatically calculated based on service provision gaps and cluster benchmarks.</p>
    <p style="font-size: 0.9rem;">Use these insights to prioritize and schedule training sessions effectively.</p>
</div>
""", unsafe_allow_html=True)