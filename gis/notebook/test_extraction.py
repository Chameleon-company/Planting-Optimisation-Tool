#!/usr/bin/env python3
"""
Test extraction functions with real farm coordinates from CSV
Uses REAL Google Earth Engine to extract data for first 10 farms
"""

import pandas as pd
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path to import gis modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.gee_client import init_gee
from core.extract_data import (
    get_rainfall,
    get_temperature,
    get_elevation,
    get_ph,
    get_area_ha,
)

print("="*80)
print("EXTRACTION TEST WITH REAL EARTH ENGINE")
print("="*80)
print(f"Started at: {datetime.now()}\n")

# ============================================================================
# INITIALIZE EARTH ENGINE
# ============================================================================

print("Initializing Google Earth Engine...")
try:
    init_gee()
    print("✓ Earth Engine initialized successfully\n")
except Exception as e:
    print(f"✗ Failed to initialize Earth Engine: {e}")
    print("Please check your .env file has GEE_SERVICE_ACCOUNT and GEE_KEY_PATH")
    sys.exit(1)

# ============================================================================
# LOAD CSV AND EXTRACT DATA
# ============================================================================

# Find CSV file
csv_path = Path(__file__).parent / "all_farm_environmental_factors.csv"
if not csv_path.exists():
    # Try parent directory
    csv_path = Path(__file__).parent.parent / "all_farm_environmental_factors.csv"
if not csv_path.exists():
    # Try docs directory
    csv_path = Path(__file__).parent.parent / "docs" / "all_farm_environmental_factors.csv"

if not csv_path.exists():
    print("✗ Could not find all_farm_environmental_factors.csv")
    print("Please place the CSV in the same directory as this script")
    sys.exit(1)

print(f"📂 Loading CSV: {csv_path}\n")

df = pd.read_csv(csv_path)
print(f"✓ Loaded {len(df)} farms total")
print(f"✓ Columns: {list(df.columns)}\n")

# Get first 10 farms
first_10 = df.head(10)

print("="*80)
print("EXTRACTING DATA FOR FIRST 10 FARMS (Using Real Earth Engine)")
print("="*80 + "\n")

print("NOTE: Extracting for year 2024 (your CSV has 2020-2024 average)")
print("Expect some differences due to different time periods\n")

# Extract data for each farm
results = []

for idx, row in first_10.iterrows():
    farm_id = row['farm_id']
    lat = row['lat']
    lon = row['lon']
    geometry = (lat, lon)
    
    print(f"Farm {farm_id}:")
    print(f"  Location: ({lat:.4f}, {lon:.4f})")
    
    # Extract environmental data from Earth Engine
    try:
        print(f"  Extracting from Earth Engine...", end=" ", flush=True)
        
        rainfall = get_rainfall(geometry, year=2024)
        temperature = get_temperature(geometry, year=2024)
        elevation = get_elevation(geometry)
        ph = get_ph(geometry)
        # Note: area_ha requires polygon, not just point
        # Using CSV value for now
        area_ha = row['area_ha']
        
        print("Done!")
        print(f"  Rainfall: {rainfall} mm (CSV: {row['rainfall_mm']} mm)")
        print(f"  Temperature: {temperature}°C (CSV: {row['temperature_celsius']}°C)")
        print(f"  Elevation: {elevation} m (CSV: {row['elevation_m']} m)")
        print(f"  pH: {ph} (CSV: {row['ph']})")
        print(f"  Area: {area_ha} ha (from CSV)")
        print(f"  Status: ✓ Success\n")
        
        results.append({
            "farm_id": farm_id,
            "lat": lat,
            "lon": lon,
            "rainfall_mm_extracted": rainfall,
            "temperature_celsius_extracted": temperature,
            "elevation_m_extracted": elevation,
            "ph_extracted": ph,
            "area_ha": area_ha,
            "status": "success"
        })
        
    except Exception as e:
        print(f"Failed!")
        print(f"  Status: ✗ Error - {e}\n")
        results.append({
            "farm_id": farm_id,
            "lat": lat,
            "lon": lon,
            "status": "failed",
            "error": str(e)
        })

# ============================================================================
# CREATE RESULTS DATAFRAME
# ============================================================================

print("="*80)
print("RESULTS SUMMARY")
print("="*80 + "\n")

results_df = pd.DataFrame(results)
success_count = len(results_df[results_df['status'] == 'success'])

print(f"Total farms processed: {len(results_df)}")
print(f"Success: {success_count}/{len(results_df)}")

if success_count > 0:
    successful = results_df[results_df['status'] == 'success']
    print(f"\nExtracted Data Summary (2024):")
    print(f"  Average Rainfall: {successful['rainfall_mm_extracted'].mean():.1f} mm")
    print(f"  Average Temperature: {successful['temperature_celsius_extracted'].mean():.1f}°C")
    print(f"  Average Elevation: {successful['elevation_m_extracted'].mean():.1f} m")
    if successful['ph_extracted'].notna().any():
        print(f"  Average pH: {successful['ph_extracted'].mean():.1f}")

# ============================================================================
# COMPARISON WITH CSV DATA
# ============================================================================

print("\n" + "="*80)
print("COMPARISON: CSV DATA (2020-2024 avg) vs EXTRACTED (2024)")
print("="*80 + "\n")

# Merge with original data
comparison = first_10[['farm_id', 'lat', 'lon', 'rainfall_mm', 'temperature_celsius', 
                       'elevation_m', 'ph', 'area_ha']].copy()
comparison = comparison.merge(results_df, on=['farm_id', 'lat', 'lon'], how='left')

# Calculate differences
comparison['rainfall_diff'] = comparison['rainfall_mm_extracted'] - comparison['rainfall_mm']
comparison['temp_diff'] = comparison['temperature_celsius_extracted'] - comparison['temperature_celsius']
comparison['elevation_diff'] = comparison['elevation_m_extracted'] - comparison['elevation_m']
comparison['ph_diff'] = comparison['ph_extracted'] - comparison['ph']

print("Farm-by-Farm Comparison (all 10):")
print("-" * 80)

for idx, row in comparison.iterrows():
    print(f"\nFarm {row['farm_id']}:")
    print(f"  Rainfall:    CSV={row['rainfall_mm']:.0f}mm, GEE={row['rainfall_mm_extracted']:.0f}mm, Diff={row['rainfall_diff']:.0f}mm")
    print(f"  Temperature: CSV={row['temperature_celsius']:.1f}°C, GEE={row['temperature_celsius_extracted']:.1f}°C, Diff={row['temp_diff']:.1f}°C")
    print(f"  Elevation:   CSV={row['elevation_m']:.0f}m, GEE={row['elevation_m_extracted']:.0f}m, Diff={row['elevation_diff']:.0f}m")
    if pd.notna(row['ph_extracted']):
        print(f"  pH:          CSV={row['ph']:.1f}, GEE={row['ph_extracted']:.1f}, Diff={row['ph_diff']:.1f}")

# Calculate correlation statistics
if success_count > 0:
    successful_comp = comparison[comparison['status'] == 'success']
    
    print("\n" + "="*80)
    print("VALIDATION STATISTICS")
    print("="*80 + "\n")
    
    from scipy.stats import pearsonr
    import numpy as np
    
    # Rainfall correlation
    if len(successful_comp) > 2:
        r_rainfall, _ = pearsonr(successful_comp['rainfall_mm'], 
                                 successful_comp['rainfall_mm_extracted'])
        mae_rainfall = np.abs(successful_comp['rainfall_diff']).mean()
        
        r_temp, _ = pearsonr(successful_comp['temperature_celsius'], 
                            successful_comp['temperature_celsius_extracted'])
        mae_temp = np.abs(successful_comp['temp_diff']).mean()
        
        r_elev, _ = pearsonr(successful_comp['elevation_m'], 
                            successful_comp['elevation_m_extracted'])
        mae_elev = np.abs(successful_comp['elevation_diff']).mean()
        
        print(f"Rainfall:    r={r_rainfall:.3f}, MAE={mae_rainfall:.1f}mm")
        print(f"Temperature: r={r_temp:.3f}, MAE={mae_temp:.1f}°C")
        print(f"Elevation:   r={r_elev:.3f}, MAE={mae_elev:.1f}m")
        
        # pH if available
        valid_ph = successful_comp.dropna(subset=['ph_extracted'])
        if len(valid_ph) > 2:
            r_ph, _ = pearsonr(valid_ph['ph'], valid_ph['ph_extracted'])
            mae_ph = np.abs(valid_ph['ph_diff']).mean()
            print(f"pH:          r={r_ph:.3f}, MAE={mae_ph:.2f}")

# ============================================================================
# SAVE RESULTS
# ============================================================================

print("\n" + "="*80)
print("SAVING RESULTS")
print("="*80 + "\n")

output_dir = Path(__file__).parent / "extraction_results"
output_dir.mkdir(exist_ok=True)

# Save extracted data
output_file1 = output_dir / "extracted_data_first_10_REAL.csv"
results_df.to_csv(output_file1, index=False)
print(f"✓ Extracted data saved: {output_file1}")

# Save comparison
output_file2 = output_dir / "comparison_csv_vs_gee_REAL.csv"
comparison.to_csv(output_file2, index=False)
print(f"✓ Comparison saved: {output_file2}")

# Save detailed results
output_file3 = output_dir / "extraction_results_REAL_detailed.txt"
with open(output_file3, 'w') as f:
    f.write("="*80 + "\n")
    f.write("EXTRACTION TEST RESULTS - REAL EARTH ENGINE\n")
    f.write("="*80 + "\n\n")
    f.write(f"Test Date: {datetime.now()}\n")
    f.write(f"Total Farms: {len(results_df)}\n")
    f.write(f"Success: {success_count}/{len(results_df)}\n\n")
    f.write("Data Sources:\n")
    f.write("  CSV: 2020-2024 average (5 years)\n")
    f.write("  GEE: 2024 single year\n\n")
    f.write("="*80 + "\n")
    f.write("EXTRACTED DATA\n")
    f.write("="*80 + "\n\n")
    f.write(results_df.to_string())
    f.write("\n\n")
    f.write("="*80 + "\n")
    f.write("COMPARISON\n")
    f.write("="*80 + "\n\n")
    f.write(comparison.to_string())

print(f"✓ Detailed results saved: {output_file3}")

print("\n" + "="*80)
print("✅ EXTRACTION TEST COMPLETE")
print("="*80)
print(f"\nResults saved to: {output_dir.absolute()}\n")