#!/usr/bin/env python3
"""
Carla's Pineapples - Topographic Data Generation Script
========================================================
Generates elevation analysis and visualizations for permaculture site planning.

Site: 8.927°N, 79.900°W (Panama Canal corridor)

Requirements:
    pip install rasterio numpy matplotlib

Usage:
    python generate_topographic_data.py

Outputs:
    - carlas_topographic_analysis.png (4-panel overview)
    - carlas_elevation_contours.png (detailed contour map)
"""

import rasterio
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from pathlib import Path

# Site boundary polygon (WGS84 coordinates from KML)
SITE_BOUNDARY = [
    (-79.89987304898075, 8.927740689895115),  # NW
    (-79.90054120047037, 8.927140839240714),  # NE
    (-79.90036168654315, 8.926865210184468),  # SE
    (-79.89968317055779, 8.92750064638159),   # SW
    (-79.89987304898075, 8.927740689895115),  # close polygon
]

def load_raster(filename):
    """Load a raster file and return data, extent, and nodata mask."""
    with rasterio.open(filename) as src:
        data = src.read(1).astype(float)
        if src.nodata is not None:
            data[data == src.nodata] = np.nan
        bounds = src.bounds
        extent = [bounds.left, bounds.right, bounds.bottom, bounds.top]
    return data, extent

def create_overview_figure(dem, hillshade, slope, zones, extent):
    """Create 4-panel topographic analysis figure."""

    site_lons = [p[0] for p in SITE_BOUNDARY]
    site_lats = [p[1] for p in SITE_BOUNDARY]

    fig, axes = plt.subplots(2, 2, figsize=(14, 14))
    fig.suptitle("Carla's Pineapples - Topographic Analysis\n8.927°N, 79.900°W (Panama)",
                 fontsize=14, fontweight='bold')

    # 1. Elevation with contours
    ax1 = axes[0, 0]
    im1 = ax1.imshow(dem, extent=extent, cmap='terrain', origin='upper')
    contours = ax1.contour(dem, levels=np.arange(100, 220, 5), extent=extent,
                           colors='black', linewidths=0.5, origin='upper')
    ax1.clabel(contours, inline=True, fontsize=7, fmt='%d m')
    ax1.plot(site_lons, site_lats, 'r-', linewidth=2, label='Site boundary')
    ax1.set_title('Elevation with 5m Contours')
    ax1.set_xlabel('Longitude')
    ax1.set_ylabel('Latitude')
    plt.colorbar(im1, ax=ax1, label='Elevation (m)', shrink=0.8)
    ax1.legend(loc='upper right')

    # 2. Hillshade
    ax2 = axes[0, 1]
    ax2.imshow(hillshade, extent=extent, cmap='gray', origin='upper')
    ax2.plot(site_lons, site_lats, 'r-', linewidth=2, label='Site boundary')
    ax2.set_title('Hillshade (illumination from NW)')
    ax2.set_xlabel('Longitude')
    ax2.set_ylabel('Latitude')
    ax2.legend(loc='upper right')

    # 3. Slope
    ax3 = axes[1, 0]
    im3 = ax3.imshow(slope, extent=extent, cmap='YlOrRd', origin='upper', vmin=0, vmax=25)
    ax3.plot(site_lons, site_lats, 'b-', linewidth=2, label='Site boundary')
    ax3.set_title('Slope (degrees)')
    ax3.set_xlabel('Longitude')
    ax3.set_ylabel('Latitude')
    plt.colorbar(im3, ax=ax3, label='Slope (°)', shrink=0.8)
    ax3.legend(loc='upper right')

    # 4. Permaculture Slope Zones
    ax4 = axes[1, 1]
    zone_cmap = mcolors.ListedColormap(['white', '#2ecc71', '#f39c12', '#e74c3c', '#8e44ad'])
    zone_bounds = [0, 0.5, 1.5, 2.5, 3.5, 4.5]
    zone_norm = mcolors.BoundaryNorm(zone_bounds, zone_cmap.N)
    im4 = ax4.imshow(zones, extent=extent, cmap=zone_cmap, norm=zone_norm, origin='upper')
    ax4.plot(site_lons, site_lats, 'k-', linewidth=2, label='Site boundary')
    ax4.set_title('Permaculture Slope Zones')
    ax4.set_xlabel('Longitude')
    ax4.set_ylabel('Latitude')
    cbar4 = plt.colorbar(im4, ax=ax4, ticks=[1, 2, 3, 4], shrink=0.8)
    cbar4.ax.set_yticklabels([
        'A: 0-5°\n(swales)',
        'B: 5-15°\n(food forest)',
        'C: 15-25°\n(erosion ctrl)',
        'D: >25°\n(natural)'
    ])
    ax4.legend(loc='upper right')

    plt.tight_layout()
    return fig

def create_contour_figure(dem, hillshade, extent):
    """Create detailed elevation and contour map."""

    site_lons = [p[0] for p in SITE_BOUNDARY]
    site_lats = [p[1] for p in SITE_BOUNDARY]

    fig, ax = plt.subplots(figsize=(10, 10))
    ax.imshow(hillshade, extent=extent, cmap='gray', origin='upper')
    im = ax.imshow(dem, extent=extent, cmap='terrain', alpha=0.5, origin='upper')
    contours = ax.contour(dem, levels=np.arange(100, 220, 2), extent=extent,
                          colors='black', linewidths=0.3, origin='upper')
    ax.plot(site_lons, site_lats, 'r-', linewidth=3, label='Site boundary')
    ax.set_title("Carla's Pineapples - Elevation & Contours (2m interval)", fontsize=12)
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    plt.colorbar(im, ax=ax, label='Elevation (m)', shrink=0.8)
    ax.legend(loc='upper right')

    return fig

def print_statistics(dem, slope, zones):
    """Print elevation and slope statistics."""

    dem_valid = dem[~np.isnan(dem)]
    slope_valid = slope[~np.isnan(slope)]

    print("=" * 55)
    print("CARLA'S PINEAPPLES - TOPOGRAPHIC SUMMARY")
    print("=" * 55)
    print(f"\nSite: 8.927°N, 79.900°W (Panama Canal corridor)")
    print(f"DEM Size: {dem.shape[0]} x {dem.shape[1]} pixels (~30m resolution)")
    print(f"\nElevation:")
    print(f"  Range: {dem_valid.min():.0f}m - {dem_valid.max():.0f}m")
    print(f"  Mean:  {dem_valid.mean():.1f}m")
    print(f"\nSlope:")
    print(f"  Range: {slope_valid.min():.1f}° - {slope_valid.max():.1f}°")
    print(f"  Mean:  {slope_valid.mean():.1f}°")
    print(f"\nPermaculture Slope Zones:")

    total_valid = (zones > 0).sum()
    zone_info = [
        (1, "Zone A (0-5°)", "annual crops, swales"),
        (2, "Zone B (5-15°)", "perennials, food forest"),
        (3, "Zone C (15-25°)", "erosion control"),
        (4, "Zone D (>25°)", "leave natural"),
    ]
    for zone_id, name, use in zone_info:
        count = (zones == zone_id).sum()
        pct = count / total_valid * 100 if total_valid > 0 else 0
        if pct > 0:
            print(f"  {name}: {pct:.1f}% - {use}")

    print("=" * 55)

def main():
    """Main function to generate all visualizations."""

    print("Loading raster data...")

    # Check for required files
    required_files = [
        'carlas_dem_large.tif',
        'carlas_hillshade_large.tif',
        'carlas_slope_large.tif',
        'carlas_slope_zones_large.tif'
    ]

    for f in required_files:
        if not Path(f).exists():
            print(f"ERROR: Required file '{f}' not found.")
            print("Make sure you have the GeoTIFF files in the current directory.")
            return

    # Load data
    dem, extent = load_raster('carlas_dem_large.tif')
    hillshade, _ = load_raster('carlas_hillshade_large.tif')
    slope, _ = load_raster('carlas_slope_large.tif')

    with rasterio.open('carlas_slope_zones_large.tif') as src:
        zones = src.read(1)

    # Print statistics
    print_statistics(dem, slope, zones)

    # Create visualizations
    print("\nGenerating visualizations...")

    fig1 = create_overview_figure(dem, hillshade, slope, zones, extent)
    fig1.savefig('carlas_topographic_analysis.png', dpi=150, bbox_inches='tight')
    print("  Saved: carlas_topographic_analysis.png")

    fig2 = create_contour_figure(dem, hillshade, extent)
    fig2.savefig('carlas_elevation_contours.png', dpi=200, bbox_inches='tight')
    print("  Saved: carlas_elevation_contours.png")

    plt.close('all')
    print("\nDone!")

if __name__ == '__main__':
    main()
