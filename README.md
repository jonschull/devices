# Global Restoration Stories Map

An interactive world map showcasing successful ecosystem restoration projects worldwide, featuring stories from Mongabay and other conservation sources.

## Features

- Interactive satellite map (ESRI World Imagery) with multiple base layer options
- 18 curated restoration success stories across 5 categories:
  - Forest Restoration
  - Marine/Coastal
  - Wetlands
  - Grasslands
  - Wildlife Recovery
- Category filtering to focus on specific restoration types
- Click markers to view story details, descriptions, and links to full articles
- Responsive design works on desktop and mobile

## Usage

### View the Map

Simply open `index.html` in any modern web browser. No server required.

### Host on GitHub Pages

1. Push this repository to GitHub
2. Go to Settings > Pages
3. Select "Deploy from a branch" and choose `main`
4. Your map will be available at `https://[username].github.io/[repo-name]/`

## Adding Stories

Edit `stories.json` to add new restoration stories. Each story requires:

```json
{
  "id": 19,
  "title": "Story Title",
  "description": "Brief description of the restoration project and its success.",
  "location": "Location Name",
  "lat": 0.0000,
  "lng": 0.0000,
  "category": "forest|marine|wetland|grassland|wildlife",
  "date": "YYYY-MM-DD",
  "source": "Source Name",
  "url": "https://link-to-full-story.com"
}
```

## Data Sources

Stories are sourced from [Mongabay](https://news.mongabay.com/), an environmental news platform publishing under Creative Commons CC BY-ND 4.0 license.

### Mongabay RSS Feeds

For live data integration, Mongabay offers topic-based RSS feeds:
- Restoration: `https://news.mongabay.com/feed/?topic=restoration`
- Rewilding: `https://news.mongabay.com/feed/?topic=rewilding`
- Conservation: `https://news.mongabay.com/feed/?topic=conservation`

## Technologies

- [Leaflet.js](https://leafletjs.com/) - Open-source mapping library
- [ESRI World Imagery](https://www.arcgis.com/) - Satellite tile layer
- Vanilla JavaScript - No build tools required

## License

Map code is open source. Story content from Mongabay is used under CC BY-ND 4.0 - attribution required, no derivatives.
