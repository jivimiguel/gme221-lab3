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

### 3D Geometry Construction Milestone
As I started converting the roads into 3D geometries, it became clear why densification is a necessary step rather than an optional refinement. Many of the original road lines only contain a few vertices, which means that if I sampled elevation only at those points, the resulting 3D line would ignore almost all terrain variation. By inserting additional points at a fixed interval, I’m effectively giving the DEM more opportunities to describe how the elevation actually changes along each road. Without densification, the 3D output would be coarse and misleading, especially in areas with subtle slopes or abrupt elevation shifts.

Before sampling any elevation values, I also needed to ensure that the roads and the DEM shared the same CRS. Even a small mismatch would mean sampling the wrong pixel locations, or worse, retrieving nodata everywhere because the coordinate spaces do not overlap. Aligning the CRS puts both datasets into the same spatial frame, so that each interpolated road point corresponds to the correct DEM cell. This alignment step is foundational, if it’s wrong, everything that follows becomes unreliable.

Once Z values are finally added, the geometry becomes something fundamentally different from a simple extrusion. The coordinate tuples themselves now carry elevation information, which means the 3D shape is driven by actual terrain data rather than a symbolic vertical offset. This produces a true LINESTRINGZ, where the geometry encodes the physical relationship between the road and the landscape. The result is no longer a visualization trick, it is a dataset with analytical meaning that can support 3D modeling, profiling, or further terrain‑aware computations.