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

### 3D GeoJSON Export
When exporting the 3D roads to GeoJSON, the full coordinate structure is preserved, meaning every vertex keeps its complete (x, y, z) tuple. This allows the elevation information to remain embedded directly inside the geometry, even after leaving Python. What stood out to me, however, is that although the Z‑values are fully retained, GeoJSON does not formally acknowledge that the geometry is 3D. The standard has no `LineStringZ` type, so the file still labels the feature simply as `LineString`, leaving the third coordinate implicit rather than explicitly declared. In effect, nothing is lost in terms of actual elevation data, but the formal semantics of being a 3D geometry are not part of the GeoJSON specification. This reveals a clear separation between what the data contains, a true 3D line and what the standard can express, a 2D type with an optional third value.

This becomes more visible when bringing the exported layer into QGIS 3D View. QGIS reads the Z‑values directly from the coordinate tuples, so it can still display the roads with real elevation, but it treats them more as a 2.5D visualization rather than as objects with explicit 3D semantics. In other words, QGIS is reconstructing 3D from the data, not because GeoJSON declared it structurally. The 3D view looks correct, but it’s driven by interpretation rather than by a formal geometry type.

If I needed a format that preserves 3D semantics more explicitly, I would look at options designed for multi‑dimensional storage. Formats like GeoPackage and PostGIS can store true 3D geometries with well‑defined types, and pipelines like 3D Tiles or glTF carry 3D structure as part of the standard rather than as an implicit property of coordinates. Those formats make the 3D character of the data unambiguous, unlike GeoJSON, which quietly supports Z‑values without formally recognizing 3D geometry classes.