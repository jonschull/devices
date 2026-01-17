# ERA - Ecosystem Restoration Atlas

An interactive world map showcasing successful ecosystem restoration projects that affect weather, climate, and precipitation. Features 500 stories from Mongabay and other conservation sources.

**Live site:** [https://jonschull.github.io/devices/](https://jonschull.github.io/devices/)

## Features

- **Dual View Modes:**
  - 2D Map (Leaflet.js with ESRI satellite imagery)
  - 3D Globe (Cesium.js with satellite imagery)
- **500 curated restoration stories** across 4 ecosystem types:
  - Forest
  - Wetland
  - Grassland
  - Marine/Coastal
- **Climate impact filtering** by:
  - Precipitation/Rainfall
  - Water Cycle/Retention
  - Flood Control
  - Drought/Desertification
  - Carbon/Climate
  - Storm/Coastal Protection
- **Marker clustering** to handle dense story regions without cluttering the UI
- **Global coverage** including 100+ indigenous-led restoration projects

## Architecture & Data Flow

```
┌─────────────────────────────────┐
│  restoration_climate_stories.csv │  ← 500 stories with lat/lng
└─────────────┬───────────────────┘
              │ fetch() on page load
              ▼
┌─────────────────────────────────┐
│  parseCSV()                      │  ← Converts to JS objects
└─────────────┬───────────────────┘
              │
              ▼
┌─────────────────────────────────┐
│  allStories[]                    │  ← In-memory array
└─────────────┬───────────────────┘
              │
      ┌───────┴───────┐
      ▼               ▼
┌───────────┐   ┌───────────┐
│  Map View │   │Globe View │
│  Leaflet  │   │  Cesium   │
│  +Cluster │   │           │
└───────────┘   └───────────┘
```

### Key Components

1. **Data Source** (`restoration_climate_stories.csv`)
   - CSV format with columns: id, title, description, location, lat, lng, category, climate_impact, date, source, url
   - Loaded via fetch() on page initialization

2. **Map View** (Leaflet.js)
   - Uses MarkerClusterGroup to group nearby markers
   - ESRI World Imagery satellite tiles
   - Popups show story details on click

3. **Globe View** (Cesium.js)
   - 3D Earth with ESRI satellite imagery
   - Point entities for each story
   - Info panel shows story details on click

4. **Filtering**
   - Dropdown filters for ecosystem type and climate impact
   - Re-renders markers on both views when filters change

## Usage

### View the Map

Open `index.html` in any modern web browser, or visit the GitHub Pages site.

### Host on GitHub Pages

1. Push this repository to GitHub
2. Go to Settings > Pages
3. Select "Deploy from a branch" and choose your branch
4. Your map will be available at `https://[username].github.io/[repo-name]/`

## Adding Stories

Edit `restoration_climate_stories.csv` to add new stories. Each row requires:

```csv
id,title,description,location,lat,lng,category,climate_impact,date,source,url
501,"Story Title","Description of the project",Location Name,12.345,-67.890,forest,water_retention,2024-01-15,Mongabay,https://...
```

**Categories:** forest, wetland, grassland, marine

**Climate impacts:** precipitation, water_retention, flood_control, drought_reversal, carbon_storage, cyclone_protection, indigenous_restoration

## Data Sources

Stories are sourced from [Mongabay](https://news.mongabay.com/), an environmental news platform publishing under Creative Commons CC BY-ND 4.0 license.

### Mongabay RSS Feeds

For live data integration, Mongabay offers topic-based RSS feeds:
- Restoration: `https://news.mongabay.com/feed/?topic=restoration`
- Rewilding: `https://news.mongabay.com/feed/?topic=rewilding`
- Conservation: `https://news.mongabay.com/feed/?topic=conservation`

## Technologies

- [Leaflet.js](https://leafletjs.com/) - 2D mapping library
- [Leaflet.markercluster](https://github.com/Leaflet/Leaflet.markercluster) - Marker clustering
- [Cesium.js](https://cesium.com/) - 3D globe visualization
- [ESRI World Imagery](https://www.arcgis.com/) - Satellite tiles
- Vanilla JavaScript - No build tools required

## Credits

- Map by [Eco Restoration Alliance](https://EcoRestorationAlliance.org)
- Articles courtesy of [Mongabay](https://Mongabay.com)

## License

Map code is open source. Story content from Mongabay is used under CC BY-ND 4.0 - attribution required, no derivatives.
