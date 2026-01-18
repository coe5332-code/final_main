import streamlit as st
import requests

API_BASE_URL = "http://localhost:54300"


def fetch_data_with_controls(endpoint):
    """
    Fetch data from API with limit and skip controls
    Returns: (data, limit, skip)
    """
    st.sidebar.markdown(f"### ⚙️ Data Controls")

    limit = st.sidebar.number_input(
        "Limit",
        min_value=10,
        max_value=1000,
        value=100,
        step=10,
        help="Number of records to fetch",
    )

    skip = st.sidebar.number_input(
        "Skip",
        min_value=0,
        max_value=10000,
        value=0,
        step=10,
        help="Number of records to skip",
    )

    if st.sidebar.button("🔄 Refresh Data"):
        st.cache_data.clear()

    data = fetch_data(endpoint, limit=limit, skip=skip)
    return data, limit, skip


@st.cache_data(ttl=300)
def fetch_data(endpoint, limit=100, skip=0):
    """Fetch data from API with caching"""
    try:
        params = {"limit": limit, "skip": skip}
        response = requests.get(f"{API_BASE_URL}/{endpoint}", params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error(f"🔌 Cannot connect to backend service at {API_BASE_URL}")
        return []
    except requests.exceptions.Timeout:
        st.error(f"⏱️ Request timeout for {endpoint}")
        return []
    except Exception as e:
        st.error(f"Error fetching {endpoint}: {e}")
        return []


def apply_common_styling():
    """Apply common CSS styling across pages"""
    st.markdown(
        """
    <style>
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
        
        .data-card {
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            padding: 1.5rem;
            margin: 1rem 0;
            background: white;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        }
        
        .page-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 10px;
            color: white;
            text-align: center;
            margin-bottom: 2rem;
        }
    </style>
    """,
        unsafe_allow_html=True,
    )


def create_metric_card(value, label):
    """Create a styled metric card"""
    return f"""
    <div class="metric-card">
        <p class="metric-value">{value}</p>
        <p class="metric-label">{label}</p>
    </div>
    """
