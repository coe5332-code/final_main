import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
import sys
import os

# Add project root
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)

from ai_service.database_service import fetch_bsks_from_db


def extract_kmeans_clusters_to_excel(
    bsks_df: pd.DataFrame,
    output_file: str = "bsk_kmeans_clusters.xlsx",
    n_clusters: int = None
):
    """
    Uses EXACT SAME KMeans logic as underperforming_bsks
    and exports cluster details to Excel.
    """

    df = bsks_df.copy()

    # Same preprocessing
    df['bsk_lat'] = pd.to_numeric(df['bsk_lat'], errors='coerce')
    df['bsk_long'] = pd.to_numeric(df['bsk_long'], errors='coerce')

    # Same cluster count logic
    if n_clusters is None:
        n_clusters = int(np.sqrt(len(df))) or 1

    coords = df[['bsk_lat', 'bsk_long']].astype(float)

    kmeans = KMeans(
        n_clusters=n_clusters,
        random_state=42,
        n_init=10
    )

    df['cluster_id'] = kmeans.fit_predict(coords)

    # =========================
    # Sheet 1: Cluster Summary
    # =========================
    cluster_summary = (
        df.groupby('cluster_id')
        .agg(
            num_bsks=('bsk_id', 'count'),
            avg_lat=('bsk_lat', 'mean'),
            avg_long=('bsk_long', 'mean')
        )
        .reset_index()
        .sort_values('cluster_id')
    )

    # =========================
    # Sheet 2: Cluster → BSKs
    # =========================
    cluster_bsks = (
        df[['cluster_id', 'bsk_id']]
        .sort_values(['cluster_id', 'bsk_id'])
        .reset_index(drop=True)
    )

    # =========================
    # Write to Excel
    # =========================
    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        cluster_summary.to_excel(writer, sheet_name="cluster_summary", index=False)
        cluster_bsks.to_excel(writer, sheet_name="cluster_bsks", index=False)

    print(f"✅ Excel file created: {output_file}")
    print(f"📄 Sheets: cluster_summary, cluster_bsks")


# =========================
# Run
# =========================
if __name__ == "__main__":
    bsks_df = fetch_bsks_from_db()
    extract_kmeans_clusters_to_excel(bsks_df)
