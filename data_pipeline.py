import pandas as pd
import numpy as np
from sklearn.neighbors import BallTree
from shapely.geometry import Point, Polygon, MultiPolygon
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FoodscapeDataPipeline:
    def __init__(self, filepath, geojson_path=None):
        self.filepath = filepath
        self.geojson_path = geojson_path
        self.df = None
        self.districts_boundary = {}

        if geojson_path:
            self._load_geojson_boundaries()

    def _load_geojson_boundaries(self):
        """Loads district boundaries from a GeoJSON file using Shapely structures."""
        try:
            with open(self.geojson_path, 'r', encoding='utf-8') as f:
                geojson_data = json.load(f)
            
            for feature in geojson_data['features']:
                # Adjust key names depending on your specific GeoJSON structure (e.g., 'name', 'Ten_Quan')
                district_name = feature['properties'].get('name') or feature['properties'].get('Ten_Quan')
                geometry = feature['geometry']
                
                if geometry['type'] == 'Polygon':
                    poly = Polygon(geometry['coordinates'][0])
                elif geometry['type'] == 'MultiPolygon':
                    polys = [Polygon(coords[0]) for coords in geometry['coordinates']]
                    poly = MultiPolygon(polys)
                else:
                    continue
                
                if district_name:
                    self.districts_boundary[district_name] = poly
            logger.info(f"Loaded {len(self.districts_boundary)} district boundaries from GeoJSON.")
        except Exception as e:
            logger.error(f"Failed to parse GeoJSON boundaries: {str(e)}")

    def load_data(self):
        """Loads the raw dataset and standardizes basic coordinate names."""
        logger.info(f"Loading raw spatial dataset from {self.filepath}")
        self.df = pd.read_csv(self.filepath)
        self.df = self.df.rename(columns={
            'Latitude': 'latitude', 'Longitude': 'longitude', 
            'lat': 'latitude', 'lon': 'longitude'
        })
        return self
    # 1 . ADVANCED DATA IMPUTATION
    def impute_missing_districts(self):
        """Predicts missing districts based on coordinates falling inside GeoJSON Polygons."""
        if not self.districts_boundary:
            logger.warning("Skipping district imputation: No GeoJSON boundaries loaded.")
            return self

        missing_mask = self.df['district'].isna() | (self.df['district'] == 'unknown')
        impute_count = 0

        for idx, row in self.df[missing_mask].iterrows():
            if pd.notna(row['latitude']) and pd.notna(row['longitude']):
                point = Point(row['longitude'], row['latitude']) # Shapely uses (X, Y) layout -> (lon, lat)
                for district_name, polygon in self.districts_boundary.items():
                    if polygon.contains(point):
                        self.df.at[idx, 'district'] = district_name
                        impute_count += 1
                        break
        
        logger.info(f"Spatial District Imputation complete. Resolved {impute_count} missing rows.")
        return self
