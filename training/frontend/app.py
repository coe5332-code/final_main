# import streamlit as st
# import requests

# # Configure the page
# st.set_page_config(
#     page_title="BSK Training Optimization",
#     page_icon="🎓",
#     layout="wide"
# )

# st.title("BSK Training Optimization System")
# st.markdown("""
# Welcome to the BSK Training Optimization System!\
# Use the sidebar to navigate to different data views and analytics.\
# Each section provides interactive tables and visualizations for your data.\
# """) 

# # Fetch data for overview
# API_BASE_URL = "http://localhost:54300"

# def fetch_all_data(endpoint):
#     try:
#         response = requests.get(f"{API_BASE_URL}/{endpoint}")
#         response.raise_for_status()
#         return response.json()
#     except Exception as e:
#         st.error(f"Error fetching {endpoint}: {e}")
#         return []

# bsk_centers = fetch_all_data("bsk/")
# deos = fetch_all_data("deo/")
# services = fetch_all_data("services/")

# num_bsks = len(bsk_centers) if bsk_centers else 0
# num_deos = len(deos) if deos else 0
# num_services = len(services) if services else 0

# # Display summary info at the top
# st.markdown("### System Overview")
# col_a, col_b, col_c = st.columns(3)
# col_a.metric("Total BSKs", num_bsks)
# col_b.metric("Total DEOs", num_deos)
# col_c.metric("Total Services", num_services) 







import streamlit as st
import requests

# Configure the page
st.set_page_config(
    page_title="BSK Training Optimization System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
css = """
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        margin: 0;
    }
    
    .metric-label {
        font-size: 1rem;
        opacity: 0.9;
        margin: 0.5rem 0 0 0;
    }
    
    .feature-card {
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        background: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    
    .sidebar-nav {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# API Configuration
API_BASE_URL = "http://localhost:54300"

# Fetch data for overview
def fetch_all_data(endpoint):
    try:
        response = requests.get(f"{API_BASE_URL}/{endpoint}", timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.warning(f"Could not fetch {endpoint}: {e}")
        return []

# Sidebar Navigation
with st.sidebar:
    st.markdown("""
    <div class="sidebar-nav">
        <h2 style="color: #667eea; margin: 0;">🎓 BSK Training Hub</h2>
        <p style="margin: 0.5rem 0; color: #666;">Bangla Sahayta Kendra</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 📋 Navigation Guide")
    st.markdown("""
    **Data Management:**
    - BSK Centers
    - Services
    - DEOs
    - Provisions
    
    **Training Analytics:**
    - Service Recommendations
    - Underperforming BSKs
    - Training Recommendations
    
    **Video Generation:**
    - Create Training Videos
    - Manage Video Library
    """)
    
    st.markdown("---")
    st.markdown("### ℹ️ System Info")
    st.caption("Version 1.0")
    st.caption("© 2024 BSK Training System")

# Main Header
st.markdown("""
<div class="main-header">
    <h1 style="margin: 0;">🎓 BSK Training Optimization System</h1>
    <p style="margin: 0.5rem 0 0 0; font-size: 1.1rem;">
        Comprehensive Training Management & Analytics Platform
    </p>
</div>
""", unsafe_allow_html=True)

# Fetch overview data
with st.spinner("Loading system overview..."):
    bsk_centers = fetch_all_data("bsk/")
    deos = fetch_all_data("deo/")
    services = fetch_all_data("services/")
    
    num_bsks = len(bsk_centers) if bsk_centers else 0
    num_deos = len(deos) if deos else 0
    num_services = len(services) if services else 0

# System Overview Metrics
st.markdown("## 📊 System Overview")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <p class="metric-value">{num_bsks}</p>
        <p class="metric-label">Total BSK Centers</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <p class="metric-value">{num_deos}</p>
        <p class="metric-label">Data Entry Operators</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <p class="metric-value">{num_services}</p>
        <p class="metric-label">Available Services</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Feature Highlights
st.markdown("## 🎯 Platform Features")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="feature-card">
        <h3>📊 Data Management</h3>
        <p>Access and visualize BSK centers, services, DEOs, and provision data with interactive charts and filters.</p>
        <ul>
            <li>Real-time data synchronization</li>
            <li>Advanced filtering and search</li>
            <li>Geographic distribution maps</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="feature-card">
        <h3>🎥 Training Video Generation</h3>
        <p>Create professional training videos for BSK operators with AI-powered content generation.</p>
        <ul>
            <li>PDF to video conversion</li>
            <li>Form-based content creation</li>
            <li>Version management system</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <h3>🤖 AI-Powered Recommendations</h3>
        <p>Intelligent service recommendations and BSK performance analysis using machine learning.</p>
        <ul>
            <li>Service-BSK matching</li>
            <li>Performance scoring</li>
            <li>Geographic clustering</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="feature-card">
        <h3>📈 Training Analytics</h3>
        <p>Identify training needs and track performance metrics across all BSK centers.</p>
        <ul>
            <li>Underperforming BSK detection</li>
            <li>Training priority scoring</li>
            <li>District-wise benchmarking</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Quick Stats
if bsk_centers and isinstance(bsk_centers, list) and len(bsk_centers) > 0:
    st.markdown("## 📍 Quick Statistics")
    
    import pandas as pd
    bsk_df = pd.DataFrame(bsk_centers)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if 'district_name' in bsk_df.columns:
            unique_districts = bsk_df['district_name'].nunique()
            st.metric("Districts Covered", unique_districts)
    
    with col2:
        if 'bsk_type' in bsk_df.columns:
            unique_types = bsk_df['bsk_type'].nunique()
            st.metric("BSK Types", unique_types)
    
    with col3:
        if 'is_active' in bsk_df.columns:
            active_bsks = bsk_df[bsk_df['is_active'] == True].shape[0]
            st.metric("Active BSKs", active_bsks)

# Getting Started Guide
st.markdown("---")
st.markdown("## 🚀 Getting Started")

with st.expander("📖 How to Use This Platform", expanded=False):
    st.markdown("""
    ### Navigation
    Use the sidebar to navigate between different sections:
    
    **1. Data Views (Pages 01-04)**
    - View and analyze BSK centers, services, DEOs, and provisions
    - Interactive charts and filtering options
    - Export data for external analysis
    
    **2. Analytics & Recommendations (Pages 05-07)**
    - **Service Recommendations**: Find optimal BSKs for new services
    - **Underperforming BSKs**: Identify centers needing support
    - **Training Recommendations**: Prioritized training needs
    
    **3. Video Management (Page 08)**
    - Create training videos from PDF or forms
    - Upload existing videos
    - Manage video library with versioning
    
    ### Tips
    - 💡 Use filters to narrow down data views
    - 📊 Hover over charts for detailed information
    - 💾 Export results as CSV for reporting
    - 🔄 Refresh data using the controls in each page
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>BSK Training Optimization System | Powered by AI & Analytics</p>
    <p style="font-size: 0.8rem;">For support, contact your system administrator</p>
</div>
""", unsafe_allow_html=True)