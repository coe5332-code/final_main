import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
import os
from pathlib import Path

# Configuration
st.set_page_config(
    page_title="Training Video MIS Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown(
    """
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
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
    
    .alert-card {
        border-left: 4px solid #ff4757;
        background: #fff5f5;
        padding: 1rem;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
    
    .success-card {
        border-left: 4px solid #2ed573;
        background: #f0fff4;
        padding: 1rem;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
    
    .warning-card {
        border-left: 4px solid #ffa502;
        background: #fffbeb;
        padding: 1rem;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
    
    .status-new {
        background: #2ed573;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    
    .status-old {
        background: #a4b0be;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    
    .source-pdf {
        background: #e74c3c;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 10px;
        font-size: 0.75rem;
    }
    
    .source-form {
        background: #3498db;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 10px;
        font-size: 0.75rem;
    }
    
    .source-upload {
        background: #9b59b6;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 10px;
        font-size: 0.75rem;
    }
    
    .data-table {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        overflow: hidden;
    }
</style>
""",
    unsafe_allow_html=True,
)

# API Configuration
API_BASE_URL = "http://localhost:54300"
VIDEOS_BASE_DIR = "videos"


# Data Fetching Functions
@st.cache_data(ttl=60)
def fetch_all_services():
    """Fetch all services from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/services/", timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching services: {e}")
        return []


@st.cache_data(ttl=60)
def fetch_service_videos():
    """Fetch all service video records from database"""
    try:
        # This would need a new API endpoint to get all service videos
        # For now, we'll construct from file system
        videos = []
        if os.path.exists(VIDEOS_BASE_DIR):
            for service_dir in os.listdir(VIDEOS_BASE_DIR):
                service_path = os.path.join(VIDEOS_BASE_DIR, service_dir)
                if os.path.isdir(service_path):
                    service_id = int(service_dir)
                    for video_file in os.listdir(service_path):
                        if video_file.endswith(".mp4"):
                            video_path = os.path.join(service_path, video_file)
                            try:
                                version = int(
                                    video_file.split("_v")[-1].replace(".mp4", "")
                                )
                                created = datetime.fromtimestamp(
                                    os.path.getctime(video_path)
                                )
                                size_mb = os.path.getsize(video_path) / (1024 * 1024)

                                # Determine source type from filename or metadata
                                if "pdf" in video_file.lower():
                                    source = "pdf"
                                elif "form" in video_file.lower():
                                    source = "form"
                                else:
                                    source = "uploaded"

                                videos.append(
                                    {
                                        "service_id": service_id,
                                        "version": version,
                                        "filename": video_file,
                                        "size_mb": size_mb,
                                        "created_at": created,
                                        "source_type": source,
                                        "is_new": (datetime.now() - created).days < 7,
                                        "path": video_path,
                                    }
                                )
                            except (ValueError, IndexError):
                                continue
        return videos
    except Exception as e:
        st.error(f"Error scanning videos: {e}")
        return []


@st.cache_data(ttl=300)
def fetch_training_recommendations():
    """Fetch training recommendations"""
    try:
        # Use summary_only=True for faster loading on dashboard
        response = requests.get(
            f"{API_BASE_URL}/service_training_recomendation/",  # Match API spelling
            params={"limit": 100, "summary_only": True},  # Summary mode for dashboard
            timeout=120,  # 2 minutes timeout for large datasets
        )
        response.raise_for_status()
        data = response.json()

        # If summary_only returns dict with 'top_10_bsks', extract that
        if isinstance(data, dict) and "top_10_bsks" in data:
            return data["top_10_bsks"]
        return data
    except requests.exceptions.Timeout:
        st.warning("⚠️ Recommendation API timed out. Using cached data or skipping...")
        return []
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 422:
            st.info("ℹ️ Using reduced dataset for recommendations")
        else:
            st.warning(f"⚠️ Could not fetch recommendations: {e}")
        return []
    except Exception as e:
        st.warning(f"⚠️ Recommendations temporarily unavailable: {e}")
        return []


def calculate_coverage_metrics(services, videos_df):
    """Calculate video coverage metrics"""
    total_services = len(services)
    services_with_videos = (
        videos_df["service_id"].nunique() if not videos_df.empty else 0
    )
    coverage_pct = (
        (services_with_videos / total_services * 100) if total_services > 0 else 0
    )

    return {
        "total_services": total_services,
        "services_with_videos": services_with_videos,
        "services_without_videos": total_services - services_with_videos,
        "coverage_percentage": coverage_pct,
    }


# Main Dashboard Header
st.markdown(
    """
<div class="main-header">
    <h1 style="margin: 0;">📊 Training Video MIS Dashboard</h1>
    <p style="margin: 0.5rem 0 0 0;">Complete Lifecycle Management & Analytics</p>
</div>
""",
    unsafe_allow_html=True,
)

# Sidebar Filters & Controls
with st.sidebar:
    st.markdown("### 🎛️ Dashboard Controls")

    date_range = st.date_input(
        "Date Range",
        value=(datetime.now() - timedelta(days=30), datetime.now()),
        key="date_range",
    )

    st.markdown("---")

    view_mode = st.radio(
        "View Mode",
        [
            "📈 Executive Summary",
            "🎬 Video Lifecycle",
            "📊 Analytics",
            "⚠️ Alerts & Actions",
        ],
        label_visibility="collapsed",
    )

    st.markdown("---")

    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.markdown("---")
    st.markdown("### 📅 Last Updated")
    st.caption(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

# Load Data
with st.spinner("Loading dashboard data..."):
    services = fetch_all_services()
    video_records = fetch_service_videos()
    recommendations = fetch_training_recommendations()

    videos_df = pd.DataFrame(video_records) if video_records else pd.DataFrame()
    services_df = pd.DataFrame(services) if services else pd.DataFrame()
    recommendations_df = (
        pd.DataFrame(recommendations) if recommendations else pd.DataFrame()
    )

# Calculate Metrics
coverage_metrics = calculate_coverage_metrics(services, videos_df)

# ============================================================
# EXECUTIVE SUMMARY VIEW
# ============================================================
if view_mode == "📈 Executive Summary":
    st.markdown("## 📈 Executive Summary")

    # Key Metrics Row
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            f"""
        <div class="metric-card">
            <p class="metric-value">{coverage_metrics['total_services']}</p>
            <p class="metric-label">Total Services</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
        <div class="metric-card">
            <p class="metric-value">{coverage_metrics['services_with_videos']}</p>
            <p class="metric-label">Videos Created</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
        <div class="metric-card">
            <p class="metric-value">{coverage_metrics['coverage_percentage']:.1f}%</p>
            <p class="metric-label">Coverage</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col4:
        total_versions = len(videos_df) if not videos_df.empty else 0
        st.markdown(
            f"""
        <div class="metric-card">
            <p class="metric-value">{total_versions}</p>
            <p class="metric-label">Total Versions</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # Charts Row
    col1, col2 = st.columns(2)

    with col1:
        # Coverage Pie Chart
        coverage_data = pd.DataFrame(
            {
                "Status": ["With Videos", "Without Videos"],
                "Count": [
                    coverage_metrics["services_with_videos"],
                    coverage_metrics["services_without_videos"],
                ],
            }
        )

        fig_coverage = px.pie(
            coverage_data,
            values="Count",
            names="Status",
            title="Video Coverage Distribution",
            color_discrete_sequence=["#2ed573", "#ff4757"],
        )
        st.plotly_chart(fig_coverage, width="stretch")

    with col2:
        # Source Type Distribution
        if not videos_df.empty:
            source_counts = videos_df["source_type"].value_counts()
            fig_source = px.bar(
                x=source_counts.index,
                y=source_counts.values,
                title="Videos by Source Type",
                labels={"x": "Source Type", "y": "Count"},
                color=source_counts.values,
                color_continuous_scale="Viridis",
            )
            st.plotly_chart(fig_source, width="stretch")

    # Recent Activity
    st.markdown("### 📅 Recent Video Activity")

    if not videos_df.empty:
        recent_videos = videos_df.nlargest(10, "created_at")

        for _, video in recent_videos.iterrows():
            service_info = (
                services_df[services_df["service_id"] == video["service_id"]].iloc[0]
                if not services_df.empty
                else {}
            )
            service_name = service_info.get(
                "service_name", f"Service {video['service_id']}"
            )

            status_badge = (
                f'<span class="status-new">NEW</span>'
                if video["is_new"]
                else f'<span class="status-old">OLD</span>'
            )
            source_badge = f'<span class="source-{video["source_type"]}">{video["source_type"].upper()}</span>'

            st.markdown(
                f"""
            <div class="success-card">
                <strong>{service_name}</strong> {status_badge} {source_badge}<br>
                <small>Version {video['version']} • {video['size_mb']:.2f} MB • {video['created_at'].strftime('%Y-%m-%d %H:%M')}</small>
            </div>
            """,
                unsafe_allow_html=True,
            )

# ============================================================
# VIDEO LIFECYCLE VIEW
# ============================================================
elif view_mode == "🎬 Video Lifecycle":
    st.markdown("## 🎬 Video Lifecycle Management")

    # Lifecycle Stages
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        pending_count = coverage_metrics["services_without_videos"]
        st.metric("⏳ Pending Creation", pending_count)

    with col2:
        new_count = (
            len(videos_df[videos_df["is_new"] == True]) if not videos_df.empty else 0
        )
        st.metric("🆕 Newly Created", new_count)

    with col3:
        active_count = coverage_metrics["services_with_videos"]
        st.metric("✅ Active Videos", active_count)

    with col4:
        update_needed = len(recommendations_df) if not recommendations_df.empty else 0
        st.metric("🔄 Update Needed", update_needed)

    st.markdown("---")

    # Lifecycle Timeline
    st.markdown("### 📊 Video Creation Timeline")

    if not videos_df.empty:
        videos_df["created_date"] = pd.to_datetime(videos_df["created_at"]).dt.date
        timeline_data = (
            videos_df.groupby("created_date").size().reset_index(name="count")
        )

        fig_timeline = px.line(
            timeline_data,
            x="created_date",
            y="count",
            title="Videos Created Over Time",
            markers=True,
        )
        fig_timeline.update_layout(
            xaxis_title="Date", yaxis_title="Number of Videos", hovermode="x unified"
        )
        st.plotly_chart(fig_timeline, width="stretch")

    # Services Requiring Videos
    st.markdown("### 🎯 Services Requiring Video Creation")

    if not services_df.empty and not videos_df.empty:
        services_with_videos = set(videos_df["service_id"].unique())
        services_without_videos = services_df[
            ~services_df["service_id"].isin(services_with_videos)
        ]

        if not services_without_videos.empty:
            st.dataframe(
                services_without_videos[
                    ["service_id", "service_name", "service_type", "department_name"]
                ],
                width="stretch",
                hide_index=True,
            )

            csv = services_without_videos.to_csv(index=False)
            st.download_button(
                "📥 Download Missing Videos List",
                csv,
                "services_without_videos.csv",
                "text/csv",
                width="stretch",
            )
        else:
            st.success("🎉 All services have training videos!")

    # Version Management
    st.markdown("### 📚 Version Management")

    if not videos_df.empty:
        # Services with multiple versions
        version_counts = (
            videos_df.groupby("service_id").size().reset_index(name="version_count")
        )
        multi_version = version_counts[version_counts["version_count"] > 1]

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Services with Multiple Versions", len(multi_version))

        with col2:
            avg_versions = version_counts["version_count"].mean()
            st.metric("Average Versions per Service", f"{avg_versions:.1f}")

        # Show services with most versions
        if not multi_version.empty:
            multi_version_merged = multi_version.merge(
                services_df[["service_id", "service_name"]], on="service_id", how="left"
            )
            multi_version_merged = multi_version_merged.sort_values(
                "version_count", ascending=False
            )

            st.dataframe(
                multi_version_merged[["service_name", "version_count"]].head(10),
                width="stretch",
                hide_index=True,
            )

# ============================================================
# ANALYTICS VIEW
# ============================================================
elif view_mode == "📊 Analytics":
    st.markdown("## 📊 Detailed Analytics")

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "📈 Production Metrics",
            "🎬 Content Analysis",
            "👥 BSK Coverage",
            "📊 Recommendations",
        ]
    )

    with tab1:
        st.markdown("### 📈 Video Production Metrics")

        if not videos_df.empty:
            # Production by source type
            col1, col2 = st.columns(2)

            with col1:
                source_stats = videos_df["source_type"].value_counts()
                fig = px.bar(
                    x=source_stats.index,
                    y=source_stats.values,
                    title="Production by Source Type",
                    labels={"x": "Source", "y": "Videos"},
                )
                st.plotly_chart(fig, width="stretch")

            with col2:
                # Storage usage
                total_storage = videos_df["size_mb"].sum()
                avg_size = videos_df["size_mb"].mean()

                st.metric("Total Storage (MB)", f"{total_storage:.2f}")
                st.metric("Average Video Size (MB)", f"{avg_size:.2f}")

                # Size distribution
                fig = px.histogram(
                    videos_df, x="size_mb", title="Video Size Distribution", nbins=20
                )
                st.plotly_chart(fig, width="stretch")

            # Monthly production trend
            videos_df["month"] = pd.to_datetime(videos_df["created_at"]).dt.to_period(
                "M"
            )
            monthly = videos_df.groupby("month").size().reset_index(name="count")
            monthly["month"] = monthly["month"].astype(str)

            fig = px.line(
                monthly,
                x="month",
                y="count",
                title="Monthly Video Production",
                markers=True,
            )
            st.plotly_chart(fig, width="stretch")

    with tab2:
        st.markdown("### 🎬 Content Analysis")

        if not services_df.empty:
            # Department-wise coverage
            if "department_name" in services_df.columns:
                dept_coverage = (
                    services_df.groupby("department_name")
                    .agg({"service_id": "count"})
                    .reset_index()
                )
                dept_coverage.columns = ["Department", "Services"]

                # Initialize Videos column with 0
                dept_coverage["Videos"] = 0

                if not videos_df.empty:
                    videos_by_dept = videos_df.merge(
                        services_df[["service_id", "department_name"]],
                        on="service_id",
                        how="left",
                    )
                    dept_videos = (
                        videos_by_dept.groupby("department_name")
                        .size()
                        .reset_index(name="Videos")
                    )
                    # Update the Videos column where we have data
                    dept_coverage = dept_coverage.merge(
                        dept_videos,
                        left_on="Department",
                        right_on="department_name",
                        how="left",
                        suffixes=("", "_new"),
                    )
                    # Use new values where available, otherwise keep 0
                    dept_coverage["Videos"] = (
                        dept_coverage["Videos_new"].fillna(0).astype(int)
                    )
                    # Drop extra columns
                    dept_coverage = dept_coverage[["Department", "Services", "Videos"]]

                dept_coverage["Coverage %"] = (
                    dept_coverage["Videos"] / dept_coverage["Services"] * 100
                ).round(1)

                st.dataframe(dept_coverage, width="stretch", hide_index=True)

                # Only create chart if we have the required columns
                if all(
                    col in dept_coverage.columns
                    for col in ["Department", "Services", "Videos"]
                ):
                    # Melt the dataframe for grouped bars
                    dept_melted = dept_coverage[
                        ["Department", "Services", "Videos"]
                    ].melt(
                        id_vars=["Department"],
                        value_vars=["Services", "Videos"],
                        var_name="Metric",
                        value_name="Count",
                    )

                    fig = px.bar(
                        dept_melted,
                        x="Department",
                        y="Count",
                        color="Metric",
                        title="Department-wise Video Coverage",
                        barmode="group",
                    )
                    st.plotly_chart(fig, width="stretch")
                else:
                    st.info("Insufficient data for department coverage chart")

    with tab3:
        st.markdown("### 👥 BSK Training Coverage")

        if not recommendations_df.empty:
            # Training recommendations analysis
            total_bsks = len(recommendations_df)
            avg_services_needed = recommendations_df["total_training_services"].mean()

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("BSKs Needing Training", total_bsks)

            with col2:
                st.metric("Avg Services/BSK", f"{avg_services_needed:.1f}")

            with col3:
                total_training_needed = recommendations_df[
                    "total_training_services"
                ].sum()
                st.metric("Total Training Gaps", int(total_training_needed))

            # District-wise analysis
            if "district_name" in recommendations_df.columns:
                district_stats = (
                    recommendations_df.groupby("district_name")
                    .agg(
                        {
                            "bsk_id": "count",
                            "total_training_services": "sum",
                            "priority_score": "mean",
                        }
                    )
                    .reset_index()
                )
                district_stats.columns = [
                    "District",
                    "BSKs",
                    "Training Gaps",
                    "Avg Priority",
                ]
                district_stats = district_stats.sort_values(
                    "Training Gaps", ascending=False
                )

                st.dataframe(district_stats, width="stretch", hide_index=True)

    with tab4:
        st.markdown("### 📊 Service Recommendations")

        if not recommendations_df.empty:
            # Extract service recommendations
            all_services = []
            for _, row in recommendations_df.iterrows():
                for svc in row.get("recommended_services", []):
                    all_services.append(
                        {
                            "service_name": svc.get("service_name"),
                            "gap": svc.get("gap", 0),
                        }
                    )

            if all_services:
                services_rec_df = pd.DataFrame(all_services)
                top_services = (
                    services_rec_df.groupby("service_name")["gap"].sum().nlargest(20)
                )

                fig = px.bar(
                    x=top_services.values,
                    y=top_services.index,
                    orientation="h",
                    title="Top 20 Services with Highest Training Demand",
                    labels={"x": "Total Gap", "y": "Service"},
                )
                st.plotly_chart(fig, width="stretch")

# ============================================================
# ALERTS & ACTIONS VIEW
# ============================================================
else:  # Alerts & Actions
    st.markdown("## ⚠️ Alerts & Action Items")

    # Critical Alerts
    st.markdown("### 🚨 Critical Alerts")

    alerts = []

    # Check for services without videos
    if coverage_metrics["services_without_videos"] > 0:
        alerts.append(
            {
                "severity": "high",
                "message": f"{coverage_metrics['services_without_videos']} services have no training videos",
                "action": "Create videos for these services",
            }
        )

    # Check for old videos (>90 days)
    if not videos_df.empty:
        old_videos = videos_df[
            (datetime.now() - pd.to_datetime(videos_df["created_at"])).dt.days > 90
        ]
        if not old_videos.empty:
            alerts.append(
                {
                    "severity": "medium",
                    "message": f"{len(old_videos)} videos are older than 90 days",
                    "action": "Review and update outdated content",
                }
            )

    # Check for high training demand
    if not recommendations_df.empty:
        high_priority = recommendations_df[recommendations_df["priority_score"] > 70]
        if not high_priority.empty:
            alerts.append(
                {
                    "severity": "high",
                    "message": f"{len(high_priority)} BSKs have high-priority training needs",
                    "action": "Prioritize training for these BSKs",
                }
            )

    # Display alerts
    if alerts:
        for alert in alerts:
            if alert["severity"] == "high":
                st.markdown(
                    f"""
                <div class="alert-card">
                    <strong>🚨 HIGH PRIORITY</strong><br>
                    {alert['message']}<br>
                    <small>Action: {alert['action']}</small>
                </div>
                """,
                    unsafe_allow_html=True,
                )
            elif alert["severity"] == "medium":
                st.markdown(
                    f"""
                <div class="warning-card">
                    <strong>⚠️ MEDIUM PRIORITY</strong><br>
                    {alert['message']}<br>
                    <small>Action: {alert['action']}</small>
                </div>
                """,
                    unsafe_allow_html=True,
                )
    else:
        st.markdown(
            """
        <div class="success-card">
            <strong>✅ All Systems Normal</strong><br>
            No critical alerts at this time
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # Action Items
    st.markdown("### 📋 Recommended Actions")

    action_items = []

    # Generate action items based on data
    if coverage_metrics["coverage_percentage"] < 80:
        action_items.append(
            {
                "priority": "High",
                "task": "Improve video coverage",
                "details": f"Current coverage is {coverage_metrics['coverage_percentage']:.1f}%. Target: 80%+",
                "deadline": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
            }
        )

    if not videos_df.empty:
        # Check for version inconsistencies
        version_counts = videos_df.groupby("service_id").size()
        if (version_counts == 1).sum() > 0:
            action_items.append(
                {
                    "priority": "Medium",
                    "task": "Review single-version services",
                    "details": f"{(version_counts == 1).sum()} services have only one version",
                    "deadline": (datetime.now() + timedelta(days=60)).strftime(
                        "%Y-%m-%d"
                    ),
                }
            )

    if not recommendations_df.empty:
        action_items.append(
            {
                "priority": "High",
                "task": "Address training gaps",
                "details": f"{len(recommendations_df)} BSKs need additional training",
                "deadline": (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d"),
            }
        )

    # Display action items
    if action_items:
        action_df = pd.DataFrame(action_items)
        st.dataframe(action_df, width="stretch", hide_index=True)

        # Download action items
        csv = action_df.to_csv(index=False)
        st.download_button(
            "📥 Download Action Items",
            csv,
            "action_items.csv",
            "text/csv",
            width="stretch",
        )

    st.markdown("---")

    # Quick Actions
    st.markdown("### ⚡ Quick Actions")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🎬 Create Bulk Videos", width="stretch"):
            st.info(
                "Navigate to Video Generator to create videos for multiple services"
            )

    with col2:
        if st.button("📊 Export Full Report", width="stretch"):
            # Generate comprehensive report
            report_data = {
                "Coverage Metrics": [coverage_metrics],
                "Alerts": alerts,
                "Action Items": action_items,
            }
            st.success("Report generation functionality ready for implementation")

    with col3:
        if st.button("📧 Send Alert Notifications", width="stretch"):
            st.info("Email notification system ready for integration")

# Footer
st.markdown("---")
st.markdown(
    """
<div style="text-align: center; color: #666; padding: 1rem;">
    <p><strong>BSK Training Video MIS Dashboard</strong></p>
    <p style="font-size: 0.9rem;">Real-time monitoring and management of training video lifecycle</p>
</div>
""",
    unsafe_allow_html=True,
)
