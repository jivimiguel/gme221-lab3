# GmE 221 - Laboratory Exercise 3: 3D Computational Modeling: DEM-Vector Integration and GeoJson Service Delivery
## Overview

---

## Environment Setup
- Python 3.14
- `PostgreSQL` with `PostGIS`
- `GeoPandas`, `SQLAlchemy`, `psycopg2`, `Rasterio`. `numPy`, `PyProj`, `Shapely`, `Flask`, `Flask-CORS`

---

## How to Run
1. Activate the virtual environment

---

## Reflection
### Hybrid IO Milestone
As I worked through this part of the lab, I started to see why the workflow deliberately separates the sources of the vector and raster data. Pulling the roads from PostGIS made sense because the database already maintains the geometry, CRS, and structure in a controlled environment. It felt more reliable than loading a standalone shapefile, especially since PostGIS is designed for managing vector datasets and enforcing data integrity. The DEM, on the other hand, stayed as a GeoTIFF because rasters are naturally file‑based and are more efficiently accessed directly through raster libraries. Keeping it as a file rather than importing it into PostGIS kept the workflow simpler and closer to how raster processing usually works.

This split between database‑stored vectors and file‑stored rasters reflects real GIS architecture, where different data types live in the storage model best suited for them. Python then becomes the layer where everything comes together vector features from PostGIS and pixel values from the DEM, ready for the actual analysis in the next stage. At this point, though, nothing analytical is happening yet. Part C is entirely about preparing inputs: loading, checking CRS, and making sure both datasets are ready for the 3D modeling steps that follow.