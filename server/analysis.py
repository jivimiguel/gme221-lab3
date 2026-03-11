import geopandas as gpd
import rasterio
import numpy as np
import os
from sqlalchemy import create_engine
from shapely.geometry import LineString, MultiLineString

# Database connection parameters
host = "localhost"
port = "5432"
dbname = "gme221_ex3"
user = "jpucio_gme"
password = "Jivimigols_8118"

conn_str =  f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}"
engine = create_engine(conn_str) 

# Minimal SQL query (no spatial processing) 
sql_roads = "SELECT gid, geom FROM public.roads"
 
roads = gpd.read_postgis(sql_roads, engine, geom_col="geom") 
# IMPORTANT: attach CRS (GeoPandas often reads PostGIS geometry without CRS) 
# Replace 3123 with the SRID from: SELECT ST_SRID(geom) FROM public.roads LIMIT 
1; 

roads = roads.set_crs(epsg=3123, allow_override=True) 
# print(roads.head()) 
# print(roads.crs) 
# print(roads.geometry.type.unique()) 

dem = rasterio.open("data/dem.tif") 
# print("DEM CRS:", dem.crs) 
# print("DEM Resolution:", dem.res) 
# print("DEM Bounds:", dem.bounds) 

SAMPLE_STEP = 10

def densify_line(line: LineString, step: float): 
    """Return points sampled along a line at fixed distance spacing.""" 
    if line.length == 0: 
        return [] 
    distances = list(range(0, int(line.length), int(step))) 
    pts = [line.interpolate(d) for d in distances] 
    pts.append(line.interpolate(line.length))  # ensure endpoint included 
    return pts

def explode_to_lines(geom):
    if geom is None:
        return []
    if geom.geom_type == "LineString":
        return [geom]
    if geom.geom_type == "MultiLineString":
        return list(geom.geoms)
    return []

# test_geom = roads.geometry.iloc[0]
# lines = explode_to_lines(test_geom)
# pts = densify_line(lines[0], SAMPLE_STEP)

# print("Sample points:", len(pts), "Line length:", lines[0].length)

all_sample_points = []

for geom in roads.geometry:
    parts = explode_to_lines(geom)
    for line in parts:
        pts = densify_line(line, SAMPLE_STEP)
        for pt in pts:
            all_sample_points.append(pt)

gdf_samples = gpd.GeoDataFrame(geometry=all_sample_points, crs=roads.crs)
gdf_samples.to_file("output/road_sample_points.shp")

# print("Densified sample points exported.")

band1 = dem.read(1)
nodata = dem.nodata

def sample_dem_z(x, y):
    row, col = dem.index(x, y)
    z = band1[row, col]
    if nodata is not None and z == nodata:
        return None
    if np.isnan(z):
        return None
    return float(z)

roads_3d = []

for geom in roads.geometry:
    parts = explode_to_lines(geom)
    if not parts:
        roads_3d.append(None)
        continue

    line = parts[0]
    pts = densify_line(line, SAMPLE_STEP)

    coords_3d = []
    for pt in pts:
        z = sample_dem_z(pt.x, pt.y)
        if z is None:
            continue
        coords_3d.append((pt.x, pt.y, z))

    roads_3d.append(LineString(coords_3d) if len(coords_3d) >= 2 else None)

roads["geom_3d"] = roads_3d

print("3D lines created:", roads["geom_3d"].notna().sum(), "/", len(roads))

## Temporary checks
# valid_3d = roads["geom_3d"].dropna()
# print("3D geometries created:", len(valid_3d), "/", len(roads))

# first = valid_3d.iloc[0]
# print("First 3D coord sample:", list(first.coords)[0])

os.makedirs("output", exist_ok=True)

roads_3d_gdf = roads.dropna(subset=["geom_3d"]).copy()
roads_3d_gdf = roads_3d_gdf.drop(columns=["geom"], errors="ignore")
roads_3d_gdf = roads_3d_gdf.set_geometry("geom_3d")

roads_3d_gdf.to_file("output/roads_3d.geojson", driver="GeoJSON")
print("Saved: output/roads_3d.geojson")