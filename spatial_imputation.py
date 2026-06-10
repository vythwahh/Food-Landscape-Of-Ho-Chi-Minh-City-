import pandas as pd
import json
from shapely.geometry import Point, Polygon

def load_geojson_boundaries(geojson_path):
    """
    Load HCMC district boundaries from a GeoJSON file.
    """
    try:
        with open(geojson_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data['features']
    except FileNotFoundError:
        print(f"Warning: Boundary file {geojson_path} not found.")
        return []

def find_district_from_coords(lat, lon, district_features):
    """
    Determine which district a coordinate belongs to using Point-in-Polygon.
    """
    if pd.isna(lat) or pd.isna(lon):
        return "Unknown"
        
    point = Point(lon, lat)  # Shapely uses (longitude, latitude) order
    
    for feature in district_features:
        district_name = feature['properties'].get('name', 'Unknown')
        geometry = feature['geometry']
        
        if geometry['type'] == 'Polygon':
            poly = Polygon(geometry['coordinates'][0])
            if poly.contains(point):
                return district_name
        elif geometry['type'] == 'MultiPolygon':
            for coords in geometry['coordinates']:
                poly = Polygon(coords[0])
                if poly.contains(point):
                    return district_name
                    
    return "Outside HCMC"

def run_spatial_imputation_pipeline():
    print("Starting Advanced Spatial Imputation Pipeline...")
    
    # Load original scraped dataset
    try:
        df = pd.read_csv("foodscape_data.csv")
    except FileNotFoundError:
        print("Error: foodscape_data.csv not found!")
        return
        
    # Load dynamically generated GeoJSON boundary features
    features = load_geojson_boundaries("hcmc_districts.geojson")
    
    if not features:
        print("Pipeline aborted due to missing boundary data.")
        return
        
    # Impute missing district names based on coordinates
    if 'district' in df.columns:
        missing_district_before = df['district'].isna().sum()
        print(f"Missing district values before imputation: {missing_district_before}")
        
        # Apply spatial imputation to rows with missing district data
        df['district'] = df.apply(
            lambda row: find_district_from_coords(row['latitude'], row['longitude'], features) 
            if pd.isna(row['district']) else row['district'], 
            axis=1
        )
        
        missing_district_after = df['district'].isna().sum()
        print(f"Missing district values after imputation: {missing_district_after}")
    
    # Export the robust dataset
    df.to_csv("spatial_imputed_food_data.csv", index=False)
    print("Successfully generated spatial_imputed_food_data.csv")

if __name__ == "__main__":
    run_spatial_imputation_pipeline()
