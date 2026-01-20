CARLA'S PINEAPPLES - TOPOGRAPHIC DATA PACKAGE
=============================================

Site Location: 8.927°N, 79.900°W (Panama Canal corridor)
Data Source: SRTM 1 Arc-Second (~30m resolution)
Coverage: 3km x 3km (108 x 108 pixels)

ELEVATION SUMMARY
-----------------
Range: 96m - 199m
Mean:  149m
Relief: 103m across 3km area

SLOPE ANALYSIS
--------------
Range: 0° - 21.4°
Mean:  5.1°

Zone A (0-5°):   59.5% - ideal for swales, annual crops
Zone B (5-15°):  39.1% - perennials, food forest
Zone C (15-25°):  1.4% - erosion control needed


FILES INCLUDED
--------------

GeoTIFF Rasters (108x108 pixels, WGS84):
  carlas_dem_large.tif         - Elevation in meters
  carlas_slope_large.tif       - Slope in degrees
  carlas_aspect_large.tif      - Aspect (slope direction)
  carlas_hillshade_large.tif   - Shaded relief for visualization
  carlas_slope_zones_large.tif - Permaculture zone classification (1-4)

Vector Contours:
  carlas_contours_2m_large.geojson  - 2m interval contours
  carlas_contours_5m_large.geojson  - 5m interval contours
  carlas_contours_2m_large.kml      - For Google Earth

Visualizations:
  carlas_topographic_analysis.png   - 4-panel analysis overview
  carlas_elevation_contours.png     - Detailed contour map

Code:
  generate_topographic_data.py      - Python script to regenerate images


REGENERATING IMAGES
-------------------

Requirements:
    pip install rasterio numpy matplotlib

Run:
    python generate_topographic_data.py


USING THE DATA
--------------

Google Earth:
  - Open carlas_contours_2m_large.kml

QGIS:
  - Add the .tif files as raster layers
  - Add .geojson files as vector layers
  - Style slope_zones with categorical colors

Web Maps:
  - Use GeoJSON files with Leaflet/Mapbox


SITE BOUNDARY (WGS84)
---------------------
Northwest: -79.89987304898075, 8.927740689895115
Northeast: -79.90054120047037, 8.927140839240714
Southeast: -79.90036168654315, 8.926865210184468
Southwest: -79.89968317055779, 8.92750064638159


COORDINATE REFERENCE SYSTEM
---------------------------
All data is in WGS84 (EPSG:4326)
For metric calculations, reproject to UTM Zone 17N (EPSG:32617)


Generated: 2026-01-20
