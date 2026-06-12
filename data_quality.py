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
    def enforce_strict_assertions(self):
        """Validates critical business logic structural rules via hard assertions."""
        try:
            # Rule 1: No missing spatial coordinate cells allowed
            assert self.df['latitude'].isna().sum() == 0, "Data Quality Defect: Missing latitude entries found!"
            assert self.df['longitude'].isna().sum() == 0, "Data Quality Defect: Missing longitude entries found!"
            
            # Rule 2: Geospatial anomaly failure block threshold (Max 1% anomaly rows tolerated)
            anomaly_rate = self.report["geospatial_out_of_bounds_anomalies"] / self.report["total_records_analyzed"]
            assert anomaly_rate <= 0.01, f"Data Quality Defect: High geographic error rate found: {anomaly_rate:.2%}"
            
            # Rule 3: Critical context columns missing data cell rates boundary constraints
            assert self.report["missing_values_percentage_by_column"].get("district", 100) < 5.0, "Critical Defect: Too many unassigned districts!"

            self.report["data_health_status"] = "PASSED_VERIFICATION"
            logger.info("🎉 DATA QUALITY ASSERTIONS PASSED! Dataset cleared for Deep Learning execution.")
            
        except AssertionError as error:
            self.report["data_health_status"] = "FAILED_VERIFICATION"
            logger.error(f"❌ DATA VALIDATION FAILURE CRITICAL DETECTED: {str(error)}")
            # Raise exception to intentionally block down-stream PyTorch network execution workflows
            raise error
            
        return self

    def export_quality_report(self, report_output_json):
        """Saves generated validation audit profile metadata into local JSON format."""
        with open(report_output_json, 'w', encoding='utf-8') as f:
            json.dump(self.report, f, indent=4, ensure_ascii=False)
        logger.info(f"Data quality report diagnostic log saved to {report_output_json}")


if __name__ == "__main__":
    # Test execution context simulation manually
    try:
        guard = DataQualityGuard('foodscape_data.csv')
        guard.run_comprehensive_audit().enforce_strict_assertions().export_quality_report('data_quality_report.json')
    except Exception as e:
        print(f"Process terminated by gatekeeper: {e}")