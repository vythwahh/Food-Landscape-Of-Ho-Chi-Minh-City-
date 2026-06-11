import pandas as pd
import numpy as np
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataQualityGuard:
    def __init__(self, filepath):
        self.filepath = filepath
        self.df = pd.read_csv(filepath)
        self.report = {}

    def run_comprehensive_audit(self):
        """Executes systematic data health assessment checks."""
        logger.info(f"Running data validation suite on {self.filepath}...")
        total_rows = len(self.df)
        
        # 1. Missing values evaluation rates
        missing_summary = self.df.isna().sum()
        missing_percentages = (missing_summary / total_rows * 100).to_dict()
        
        # 2. Duplicate rows audit
        duplicate_count = int(self.df.duplicated().sum())

        # 3. Geo-fencing checks - Detecting out-of-bounds anomaly points (e.g. coordinates in the ocean)
        # Saigon geographic limits bounding box coordinates boundaries approximation
        lat_min, lat_max = 10.3, 11.2
        lon_min, lon_max = 106.3, 107.2
        
        out_of_bounds_mask = (
            (self.df['latitude'] < lat_min) | (self.df['latitude'] > lat_max) |
            (self.df['longitude'] < lon_min) | (self.df['longitude'] > lon_max)
        )
        out_of_bounds_count = int(out_of_bounds_mask.sum())

        # Build final report schema JSON structure
        self.report = {
            "total_records_analyzed": total_rows,
            "missing_values_percentage_by_column": missing_percentages,
            "duplicate_records_detected": duplicate_count,
            "geospatial_out_of_bounds_anomalies": out_of_bounds_count,
            "data_health_status": "PENDING_VERIFICATION"
        }
        return self