import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from collections import Counter
from typing import Dict, List
import json


def training_recommendation(
    bsks_df: pd.DataFrame,
    provisions_df: pd.DataFrame,
    deos_df: pd.DataFrame,
    services_df: pd.DataFrame,
    top_n_services: int = 10,
    min_provision_threshold: int = 5,
    n_clusters: int = None
) -> List[Dict]:
    """
    Generate training recommendations for BSKs/DEOs based on cluster analysis.
    OPTIMIZED for large provision datasets (1.66M+ records).
    
    This function:
    1. Pre-aggregates provision data (efficient on large datasets)
    2. Clusters BSKs using K-means on geographic coordinates
    3. Identifies top services in each cluster
    4. Finds BSKs with low provision counts for those top services
    5. Recommends training on those services
    
    Args:
        bsks_df: DataFrame of BSK centers
        provisions_df: DataFrame of service provisions
        deos_df: DataFrame of DEOs
        services_df: DataFrame of services
        top_n_services: Number of top services to consider per cluster (default: 10)
        min_provision_threshold: Minimum provisions to not need training (default: 5)
        n_clusters: Number of clusters (default: sqrt of total BSKs)
        
    Returns:
        List of dictionaries with training recommendations in JSON-compatible format
    """
    
    print("🔄 Starting training recommendation analysis...")
    
    # ----------------------------
    # 1. PREPARE BSK DATA
    # ----------------------------
    print("[1/6] Preparing BSK data...")
    bsks = bsks_df.copy()
    bsks['bsk_id'] = pd.to_numeric(bsks['bsk_id'], errors='coerce')
    bsks['bsk_lat'] = pd.to_numeric(bsks['bsk_lat'], errors='coerce')
    bsks['bsk_long'] = pd.to_numeric(bsks['bsk_long'], errors='coerce')
    
    # Remove BSKs without valid coordinates
    bsks = bsks.dropna(subset=['bsk_lat', 'bsk_long', 'bsk_id'])
    
    if len(bsks) == 0:
        print("❌ No valid BSKs with coordinates found")
        return []
    
    print(f"   ✓ {len(bsks)} valid BSKs loaded")
    
    # ----------------------------
    # 2. K-MEANS CLUSTERING (Fast - only on BSK coordinates)
    # ----------------------------
    print("[2/6] Clustering BSKs...")
    if n_clusters is None:
        n_clusters = max(int(np.sqrt(len(bsks))), 1)
    
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    bsks['cluster_id'] = kmeans.fit_predict(bsks[['bsk_lat', 'bsk_long']])
    print(f"   ✓ Created {n_clusters} clusters")
    
    # ----------------------------
    # 3. PRE-AGGREGATE PROVISIONS (KEY OPTIMIZATION!)
    # This runs ONCE on the full dataset instead of repeatedly
    # ----------------------------
    print("[3/6] Pre-aggregating provision data (this is the heavy lifting)...")
    
    prov = provisions_df.copy()
    prov['bsk_id'] = pd.to_numeric(prov['bsk_id'], errors='coerce')
    prov['service_id'] = pd.to_numeric(prov['service_id'], errors='coerce')
    
    # Drop invalid records early
    prov = prov.dropna(subset=['bsk_id', 'service_id'])
    print(f"   ✓ Processing {len(prov)} provision records...")
    
    # CRITICAL OPTIMIZATION: Aggregate to BSK-Service level ONCE
    # This reduces 1.66M rows to ~few thousand rows
    bsk_service_counts = prov.groupby(['bsk_id', 'service_id']).size().reset_index(name='provision_count')
    print(f"   ✓ Aggregated to {len(bsk_service_counts)} BSK-Service combinations")
    
    # Add cluster info to aggregated data
    bsk_service_counts = bsk_service_counts.merge(
        bsks[['bsk_id', 'cluster_id']],
        on='bsk_id',
        how='left'
    )
    
    # ----------------------------
    # 4. IDENTIFY TOP SERVICES PER CLUSTER (Fast - works on aggregated data)
    # ----------------------------
    print("[4/6] Identifying top services per cluster...")
    
    # Group by cluster and service, sum provisions
    cluster_service_totals = bsk_service_counts.groupby(
        ['cluster_id', 'service_id']
    )['provision_count'].sum().reset_index()
    
    # Get top N services per cluster
    cluster_top_services = {}
    for cluster_id in range(n_clusters):
        cluster_data = cluster_service_totals[cluster_service_totals['cluster_id'] == cluster_id]
        
        if len(cluster_data) == 0:
            cluster_top_services[cluster_id] = []
            continue
        
        # Sort by provision count and get top N
        top_services = cluster_data.nlargest(top_n_services, 'provision_count')['service_id'].tolist()
        cluster_top_services[cluster_id] = top_services
        
    print(f"   ✓ Identified top services for {len(cluster_top_services)} clusters")
    
    # ----------------------------
    # 5. CALCULATE CLUSTER AVERAGES (Fast - works on aggregated data)
    # ----------------------------
    print("[5/6] Calculating cluster benchmarks...")
    
    # For each cluster-service combination, calculate average provisions per BSK
    cluster_service_avg = cluster_service_totals.copy()
    
    # Count BSKs per cluster
    bsks_per_cluster = bsks.groupby('cluster_id').size().reset_index(name='bsk_count')
    
    cluster_service_avg = cluster_service_avg.merge(
        bsks_per_cluster,
        on='cluster_id',
        how='left'
    )
    
    cluster_service_avg['avg_provisions'] = (
        cluster_service_avg['provision_count'] / cluster_service_avg['bsk_count']
    )
    
    # Create lookup dictionary for fast access
    cluster_service_avg_dict = {}
    for _, row in cluster_service_avg.iterrows():
        key = (int(row['cluster_id']), int(row['service_id']))
        cluster_service_avg_dict[key] = row['avg_provisions']
    
    print(f"   ✓ Calculated benchmarks for {len(cluster_service_avg_dict)} cluster-service pairs")
    
    # ----------------------------
    # 6. GENERATE RECOMMENDATIONS (Fast - iterates only over BSKs, not provisions)
    # ----------------------------
    print("[6/6] Generating recommendations...")
    
    # Convert bsk_service_counts to dict for fast lookup
    bsk_service_dict = {}
    for _, row in bsk_service_counts.iterrows():
        key = (int(row['bsk_id']), int(row['service_id']))
        bsk_service_dict[key] = row['provision_count']
    
    # Prepare services lookup for details
    services_lookup = services_df.set_index('service_id').to_dict('index')
    
    # Prepare DEOs lookup
    deos_by_bsk = deos_df.groupby('bsk_id').apply(
        lambda x: x.to_dict('records')
    ).to_dict()
    
    training_recommendations = []
    
    # Iterate through BSKs (small number - fast)
    for _, bsk_row in bsks.iterrows():
        bsk_id = int(bsk_row['bsk_id'])
        cluster_id = int(bsk_row['cluster_id'])
        
        # Get top services for this BSK's cluster
        cluster_services = cluster_top_services.get(cluster_id, [])
        
        if not cluster_services:
            continue
        
        recommended_services = []
        
        # Check each top service (small number - fast)
        for service_id in cluster_services:
            service_id = int(service_id)
            
            # Get this BSK's provision count for this service
            provision_count = bsk_service_dict.get((bsk_id, service_id), 0)
            
            # Get cluster average
            cluster_avg = cluster_service_avg_dict.get((cluster_id, service_id), 0)
            
            # If provisions are below threshold, recommend training
            if provision_count < min_provision_threshold:
                gap = cluster_avg - provision_count
                
                # Get service details
                if service_id in services_lookup:
                    service_info = services_lookup[service_id]
                    
                    recommended_services.append({
                        'service_id': int(service_id),
                        'service_name': str(service_info.get('service_name', 'Unknown')),
                        'service_type': str(service_info.get('service_type', 'N/A')),
                        'service_desc': str(service_info.get('service_desc', ''))[:200],
                        'current_provisions': int(provision_count),
                        'cluster_avg_provisions': round(float(cluster_avg), 2),
                        'gap': round(float(gap), 2)
                    })
        
        # Only add recommendation if there are services to train on
        if recommended_services:
            # Get DEO information for this BSK
            bsk_deos = deos_by_bsk.get(bsk_id, [])
            
            deo_details = []
            for deo_row in bsk_deos:
                deo_details.append({
                    'agent_id': str(deo_row.get('agent_id', '')),
                    'user_name': str(deo_row.get('user_name', '')),
                    'agent_code': str(deo_row.get('agent_code', '')),
                    'agent_email': str(deo_row.get('agent_email', '')),
                    'agent_phone': str(deo_row.get('agent_phone', '')),
                    'bsk_post': str(deo_row.get('bsk_post', '')),
                    'is_active': bool(deo_row.get('is_active', False))
                })
            
            # Create recommendation record
            recommendation = {
                'bsk_id': int(bsk_id),
                'bsk_name': str(bsk_row.get('bsk_name', '')),
                'bsk_code': str(bsk_row.get('bsk_code', '')),
                'district_name': str(bsk_row.get('district_name', '')),
                'block_municipalty_name': str(bsk_row.get('block_municipalty_name', '')),
                'bsk_type': str(bsk_row.get('bsk_type', '')),
                'cluster_id': int(cluster_id),
                'bsk_lat': float(bsk_row['bsk_lat']) if pd.notna(bsk_row['bsk_lat']) else None,
                'bsk_long': float(bsk_row['bsk_long']) if pd.notna(bsk_row['bsk_long']) else None,
                'total_training_services': len(recommended_services),
                'recommended_services': sorted(
                    recommended_services, 
                    key=lambda x: x['gap'], 
                    reverse=True
                ),
                'deos': deo_details,
                'priority_score': sum(s['gap'] for s in recommended_services)
            }
            
            training_recommendations.append(recommendation)
    
    # Sort by priority
    training_recommendations = sorted(
        training_recommendations,
        key=lambda x: x['priority_score'],
        reverse=True
    )
    
    print(f"✅ Generated {len(training_recommendations)} training recommendations")
    
    return training_recommendations


def export_training_recommendations_json(
    recommendations: List[Dict],
    filepath: str = 'training_recommendations.json'
):
    """
    Export training recommendations to JSON file.
    
    Args:
        recommendations: List of recommendation dictionaries
        filepath: Output file path
    """
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(recommendations, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Training recommendations exported to {filepath}")


# Example usage:
if __name__ == "__main__":
    """
    Test the training recommendation function locally using database connection.
    Make sure to have your backend database configured properly.
    """
    import sys
    import os
    
    # Add backend to path for imports
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))
    
    try:
        from app.models.database import SessionLocal
        from app.models import models
        
        print("=" * 80)
        print("TRAINING RECOMMENDATION SYSTEM - LOCAL TEST")
        print("=" * 80)
        
        # Create database session
        db = SessionLocal()
        
        try:
            # Fetch data from database
            print("\n[1/4] Fetching BSK data from database...")
            bsks = db.query(models.BSKMaster).all()
            bsks_df = pd.DataFrame([b.__dict__ for b in bsks])
            if "_sa_instance_state" in bsks_df.columns:
                bsks_df.drop("_sa_instance_state", axis=1, inplace=True)
            print(f"      ✓ Loaded {len(bsks_df)} BSK records")
            
            print("\n[2/4] Fetching Provisions data from database...")
            provisions = db.query(models.Provision).all()
            provisions_df = pd.DataFrame([p.__dict__ for p in provisions])
            if "_sa_instance_state" in provisions_df.columns:
                provisions_df.drop("_sa_instance_state", axis=1, inplace=True)
            print(f"      ✓ Loaded {len(provisions_df)} provision records")
            
            print("\n[3/4] Fetching DEO data from database...")
            deos = db.query(models.DEOMaster).all()
            deos_df = pd.DataFrame([d.__dict__ for d in deos])
            if "_sa_instance_state" in deos_df.columns:
                deos_df.drop("_sa_instance_state", axis=1, inplace=True)
            print(f"      ✓ Loaded {len(deos_df)} DEO records")
            
            print("\n[4/4] Fetching Services data from database...")
            services = db.query(models.ServiceMaster).all()
            services_df = pd.DataFrame([s.__dict__ for s in services])
            if "_sa_instance_state" in services_df.columns:
                services_df.drop("_sa_instance_state", axis=1, inplace=True)
            print(f"      ✓ Loaded {len(services_df)} service records")
            
            print("\n" + "=" * 80)
            print("DATA LOADED SUCCESSFULLY")
            print("=" * 80)
            
            # Run training recommendation
            print("\n🔄 Generating training recommendations...")
            recommendations = training_recommendation(
                bsks_df=bsks_df,
                provisions_df=provisions_df,
                deos_df=deos_df,
                services_df=services_df,
                top_n_services=10,
                min_provision_threshold=5
            )
            
            print("\n" + "=" * 80)
            print("TRAINING RECOMMENDATIONS GENERATED")
            print("=" * 80)
            
            # Export to JSON
            output_file = 'training_recommendations.json'
            export_training_recommendations_json(recommendations, output_file)
            
            # Print detailed summary
            print(f"\n📊 SUMMARY:")
            print(f"   Total BSKs analyzed: {len(bsks_df)}")
            print(f"   BSKs needing training: {len(recommendations)}")
            print(f"   Total training gaps identified: {sum(r['total_training_services'] for r in recommendations)}")
            
            if recommendations:
                print(f"\n🏆 TOP 10 BSKs NEEDING TRAINING (by priority):")
                print("-" * 80)
                
                for i, rec in enumerate(recommendations[:10], 1):
                    print(f"\n{i}. {rec['bsk_name']} (ID: {rec['bsk_id']})")
                    print(f"   📍 Location: {rec['district_name']} - {rec['block_municipalty_name']}")
                    print(f"   🎯 Cluster: {rec['cluster_id']} | BSK Type: {rec['bsk_type']}")
                    print(f"   📚 Services needing training: {rec['total_training_services']}")
                    print(f"   ⚠️  Priority Score: {rec['priority_score']:.2f}")
                    
                    # Show DEOs
                    if rec['deos']:
                        print(f"   👥 DEOs ({len(rec['deos'])}):")
                        for deo in rec['deos'][:3]:  # Show max 3 DEOs
                            status = "✓ Active" if deo['is_active'] else "✗ Inactive"
                            print(f"      - {deo['user_name']} ({deo['bsk_post']}) - {status}")
                    else:
                        print(f"   👥 DEOs: No DEOs assigned")
                    
                    # Show top 3 service gaps
                    print(f"   📋 Top Service Gaps:")
                    for j, svc in enumerate(rec['recommended_services'][:3], 1):
                        print(f"      {j}. {svc['service_name']}")
                        print(f"         Current: {svc['current_provisions']} | "
                              f"Cluster Avg: {svc['cluster_avg_provisions']:.1f} | "
                              f"Gap: {svc['gap']:.1f}")
                
                # Statistics by district
                print("\n\n📈 TRAINING NEEDS BY DISTRICT:")
                print("-" * 80)
                district_stats = {}
                for rec in recommendations:
                    district = rec['district_name']
                    if district not in district_stats:
                        district_stats[district] = {
                            'bsks': 0,
                            'total_services': 0,
                            'total_priority': 0
                        }
                    district_stats[district]['bsks'] += 1
                    district_stats[district]['total_services'] += rec['total_training_services']
                    district_stats[district]['total_priority'] += rec['priority_score']
                
                # Sort by priority
                sorted_districts = sorted(
                    district_stats.items(),
                    key=lambda x: x[1]['total_priority'],
                    reverse=True
                )
                
                for district, stats in sorted_districts[:10]:
                    print(f"   {district}:")
                    print(f"      BSKs needing training: {stats['bsks']}")
                    print(f"      Total service gaps: {stats['total_services']}")
                    print(f"      Total priority: {stats['total_priority']:.2f}")
                
                # Most recommended services
                print("\n\n🎓 MOST NEEDED TRAINING SERVICES:")
                print("-" * 80)
                service_needs = {}
                for rec in recommendations:
                    for svc in rec['recommended_services']:
                        svc_name = svc['service_name']
                        if svc_name not in service_needs:
                            service_needs[svc_name] = {
                                'count': 0,
                                'total_gap': 0,
                                'service_type': svc['service_type']
                            }
                        service_needs[svc_name]['count'] += 1
                        service_needs[svc_name]['total_gap'] += svc['gap']
                
                sorted_services = sorted(
                    service_needs.items(),
                    key=lambda x: x[1]['count'],
                    reverse=True
                )
                
                for i, (service, stats) in enumerate(sorted_services[:15], 1):
                    print(f"   {i}. {service}")
                    print(f"      Needed at {stats['count']} BSKs | "
                          f"Total gap: {stats['total_gap']:.1f} | "
                          f"Type: {stats['service_type']}")
                
            else:
                print("\n✅ No training recommendations needed - all BSKs are performing well!")
            
            print("\n" + "=" * 80)
            print(f"✅ Results saved to: {output_file}")
            print("=" * 80)
            
        finally:
            db.close()
            print("\n✓ Database connection closed")
            
    except ImportError as e:
        print(f"\n❌ ERROR: Could not import database modules")
        print(f"   {str(e)}")
        print("\n   Make sure you're running this from the project root and")
        print("   the backend database is properly configured.")
        print("\n   Try: python -m ai_service.training_recommendation")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()