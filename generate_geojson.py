import json
import math

# Get the exact list of district coordinates and radii from the collect_data.py file
DISTRICTS = [
    ("Quan 1", 10.7769, 106.7009, 2500),
    ("Quan 2", 10.7873, 106.7519, 4000),
    ("Quan 3", 10.7797, 106.6886, 2500),
    ("Quan 4", 10.7583, 106.7047, 2500),
    ("Quan 5", 10.7553, 106.6618, 2500),
    ("Quan 6", 10.7478, 106.6346, 3000),
    ("Quan 7", 10.7324, 106.7218, 3500),
    ("Quan 8", 10.7232, 106.6283, 3500),
    ("Quan 9", 10.8437, 106.8006, 4000),
    ("Quan 10", 10.7736, 106.6680, 2500),
    ("Quan 11", 10.7632, 106.6513, 2500),
    ("Quan 12", 10.8682, 106.6432, 4000),
    ("Binh Thanh", 10.8122, 106.7099, 3500),
    ("Binh Tan", 10.7456, 106.6018, 5000),
    ("Go Vap", 10.8380, 106.6652, 3500),
    ("Thu Duc", 10.8700, 106.8030, 4500),
    ("Tan Binh", 10.8015, 106.6524, 3500),
    ("Tan Phu", 10.7908, 106.6276, 4500),
    ("Phu Nhuan", 10.7993, 106.6840, 2500)
]

def create_circular_polygon(lat, lon, radius_meters, sides=32):
    """ Create a circular polygon around a point (lat, lon) with a given radius in meters. """
    coordinates = []
    # Transform radius from meters to degrees (approximation)
    lat_degree = radius_meters / 111320.0
    lon_degree = radius_meters / (111320.0 * math.cos(math.radians(lat)))
    
    for i in range(sides + 1):
        angle = float(i) * 2.0 * math.pi / float(sides)
        dx = lon_degree * math.cos(angle)
        dy = lat_degree * math.sin(angle)
        coordinates.append([lon + dx, lat + dy])
        
    return [coordinates]

geojson_data = {
    "type": "FeatureCollection",
    "features": []
}

for name, lat, lon, radius in DISTRICTS:
    poly_coords = create_circular_polygon(lat, lon, radius)
    feature = {
        "type": "Feature",
        "properties": { "name": name },
        "geometry": {
            "type": "Polygon",
            "coordinates": poly_coords
        }
    }
    geojson_data["features"].append(feature)

 
with open("hcmc_districts.geojson", "w", encoding="utf-8") as f:
    json.dump(geojson_data, f, ensure_ascii=False, indent=2)

print("Created file hcmc_districts.geojson with district boundaries for HCMC")