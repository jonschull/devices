# Extending the ERA Dataset

This document explains how to add more restoration stories to the CSV dataset.

---

## Casefinder Methodology

This section documents the search strategies, judgment criteria, and implicit knowledge used to curate the initial 500 stories. Use this as a guide for finding more high-quality cases.

### Search Tools Used

The original dataset was compiled using:

1. **WebSearch** (Claude's built-in web search) - Primary discovery tool
2. **WebFetch** - To read and extract details from article pages
3. **Geographic knowledge** - To identify lat/lng coordinates for locations

Google was not used directly; searches went through Claude's WebSearch tool which queries multiple sources.

### Search Query Patterns

**Core query structure:**
```
site:mongabay.com [ecosystem] restoration [climate-keyword] [region]
```

**Effective query examples:**

```
# By ecosystem type
site:mongabay.com forest restoration rainfall
site:mongabay.com mangrove restoration flooding storm surge
site:mongabay.com wetland restoration water table groundwater
site:mongabay.com grassland restoration desertification drought
site:mongabay.com peatland restoration carbon water

# By climate impact
site:mongabay.com restoration "increased rainfall"
site:mongabay.com restoration "water cycle"
site:mongabay.com restoration "flood control" OR "flood prevention"
site:mongabay.com restoration "reversed desertification"
site:mongabay.com restoration "storm protection" OR "cyclone"

# By region (to ensure coverage)
site:mongabay.com restoration climate Africa
site:mongabay.com restoration rainfall Amazon
site:mongabay.com restoration water Southeast Asia
site:mongabay.com restoration indigenous climate Pacific

# By specific phenomena
site:mongabay.com "biotic pump" forest rainfall
site:mongabay.com "flying rivers" Amazon
site:mongabay.com "green wall" Sahel
site:mongabay.com reforestation microclimate temperature
```

**Beyond Mongabay:**
```
restoration project "affected rainfall" site:theguardian.com
ecosystem restoration "water cycle" site:bbc.com
reforestation "local climate" site:nature.com
```

### Selection Criteria (The Judgment Calls)

**INCLUDE a story if it has:**

1. **Explicit climate/water connection** - The article directly states the restoration affected:
   - Rainfall/precipitation patterns
   - Water retention or groundwater levels
   - Flood reduction
   - Drought reversal or desertification halt
   - Storm surge or cyclone protection
   - Local temperature/microclimate
   - Carbon sequestration (if quantified)

2. **Specific location** - Must be mappable to a point:
   - Named region, park, or project area
   - Country + region at minimum
   - Bonus: exact coordinates mentioned

3. **Documented success** - Evidence of positive outcomes:
   - Measured results (hectares, rainfall mm, flood reduction %)
   - Before/after comparisons
   - Scientific studies cited
   - Community testimony

4. **Credible source** - Preference order:
   - Mongabay (primary - CC BY-ND 4.0)
   - Scientific journals
   - Major news outlets (Guardian, BBC, Reuters)
   - NGO reports (IUCN, WWF, TNC)

**EXCLUDE a story if:**

1. **Only carbon focus** - Pure carbon offset projects without other climate benefits
2. **Proposed/planned only** - No actual restoration completed yet
3. **Too vague** - "Somewhere in the Amazon" without specifics
4. **No climate connection** - Restoration for biodiversity only, no weather/water mention
5. **Controversial/disputed** - Claims not supported by evidence
6. **Paywalled** - Can't verify the content

### Implicit Knowledge: What Makes a Great Case

**Strongest cases have these characteristics:**

1. **The "wow factor"** - Dramatic, measurable change
   - "Rainfall increased 20% after reforestation"
   - "Floods reduced by 60% since mangroves restored"
   - "Desert turned green in 20 years"

2. **Scientific backing** - Published research supports claims
   - Links to peer-reviewed studies
   - University involvement
   - Long-term monitoring data

3. **Human story** - Community involvement
   - Indigenous-led projects (prioritize these!)
   - Local economic benefits
   - Generational knowledge preserved

4. **Scale** - Large enough to demonstrate systemic impact
   - Landscape-level projects
   - Watershed-scale restoration
   - National/regional programs

5. **Replicability** - Methods can be applied elsewhere
   - Documented techniques
   - Cost-effective approaches
   - Applicable to similar ecosystems

### The Casefinder Persona Prompt

Use this prompt to have Claude find new cases:

```
You are a Casefinder for the Ecosystem Restoration Atlas (ERA), searching for documented restoration projects that have measurably affected weather, climate, water cycles, or precipitation.

## Your Search Mission

Find restoration success stories that demonstrate climate/hydrological benefits. Each case must be:
- Geographically specific (mappable to coordinates)
- Documented with evidence (not just planned)
- Connected to weather/water impacts (not just biodiversity or carbon)

## Search Strategy

1. Start with targeted queries:
   - site:mongabay.com [ecosystem] restoration [climate-keyword]
   - Vary ecosystems: forest, mangrove, wetland, peatland, grassland, kelp
   - Vary climate keywords: rainfall, precipitation, flood, drought, water table, storm surge

2. Prioritize underrepresented regions:
   - Central Asia (Kazakhstan, Uzbekistan, Mongolia)
   - Small island nations (Pacific, Caribbean, Indian Ocean)
   - Middle East (Jordan, UAE restoration projects)
   - Urban restoration (Singapore, Seoul, etc.)

3. Seek indigenous-led projects:
   - Search: indigenous restoration climate [region]
   - These often have the best long-term outcomes

## For Each Case Found, Extract:

1. **Title**: Compelling headline (you may improve on article title)
2. **Description**: 1-2 sentences focusing on the CLIMATE/WATER impact
3. **Location**: Most specific place name possible
4. **Coordinates**: Look up lat/lng (use major city if project area is large)
5. **Category**: forest | wetland | grassland | marine
6. **Climate Impact**: precipitation | water_retention | flood_control | drought_reversal | carbon_storage | cyclone_protection | indigenous_restoration
7. **Date**: Article publication date (YYYY-MM-DD)
8. **Source**: Publication name
9. **URL**: Full article URL

## Quality Thresholds

- STRONG: Peer-reviewed science, measured outcomes, before/after data
- ACCEPTABLE: Credible journalism, expert quotes, visible results
- REJECT: Vague claims, no specifics, proposed-only, carbon-only

## Output Format

For each case, provide a CSV row:
```csv
id,"Title","Description focusing on climate/water impact",Location,lat,lng,category,climate_impact,YYYY-MM-DD,Source,URL
```

## Example Good Case

Query: site:mongabay.com reforestation rainfall Ethiopia
Found: Article about Tigray region restoration

```csv
501,"Ethiopia's Tigray Restoration Brings Back Springs and Rainfall","After 20 years of community-led reforestation in Tigray, dried springs have returned and local farmers report more reliable rainfall patterns during growing seasons.","Tigray Region, Ethiopia",14.0323,38.3166,forest,precipitation,2023-06-15,Mongabay,https://news.mongabay.com/...
```

Why this is strong:
- Specific region (Tigray)
- Measurable outcome (springs returned)
- Climate connection (rainfall patterns)
- Community-led (credibility)
- Time frame (20 years - demonstrates persistence)

## Begin Searching

Find 10-20 new cases, prioritizing:
1. Regions not well-covered in current dataset
2. Indigenous-led projects
3. Recent stories (2024-2026)
4. Dramatic/measurable climate outcomes
```

### Verification Checklist

Before adding a story, verify:

- [ ] Article URL works and content matches
- [ ] Location can be found on Google Maps
- [ ] Coordinates are accurate (within 50km of actual site)
- [ ] Climate/water benefit is explicitly stated in article
- [ ] Not a duplicate of existing entry
- [ ] Source is credible (not promotional content)
- [ ] Description accurately summarizes the climate impact

---

## CSV Format

File: `restoration_climate_stories.csv`

| Column | Description | Example |
|--------|-------------|---------|
| id | Unique integer | 501 |
| title | Story headline (quoted) | "Mangroves Reduce Flooding in Vietnam" |
| description | 1-2 sentence summary (quoted) | "Restored mangroves along the coast..." |
| location | Place name | Mekong Delta, Vietnam |
| lat | Latitude (decimal) | 10.0452 |
| lng | Longitude (decimal) | 105.7469 |
| category | Ecosystem type | forest, wetland, grassland, marine |
| climate_impact | Primary climate benefit | See list below |
| date | Publication date | 2024-03-15 |
| source | Publication name | Mongabay |
| url | Full article URL | https://news.mongabay.com/... |

### Climate Impact Categories

| Value | Display Name | Use For |
|-------|--------------|---------|
| precipitation | Precipitation | Projects increasing local rainfall |
| water_retention | Water Cycle | Projects improving water retention, groundwater |
| flood_control | Flood Control | Projects reducing flood risk |
| drought_reversal | Drought/Desert | Projects reversing desertification |
| carbon_storage | Carbon/Climate | Projects focused on carbon sequestration |
| cyclone_protection | Storm Protection | Coastal projects reducing storm damage |
| indigenous_restoration | Indigenous-led | Projects led by indigenous communities |

## Method 1: Manual Addition

1. Find a restoration story on Mongabay or similar source
2. Extract the required fields
3. Add a new row to the CSV
4. Ensure the description mentions climate/weather/precipitation impact

Example row:
```csv
501,"Mangrove Restoration Reduces Storm Surge","Replanted mangroves along Vietnam's coast have reduced storm surge heights by 60%, protecting coastal communities.","Mekong Delta, Vietnam",10.0452,105.7469,marine,cyclone_protection,2024-03-15,Mongabay,https://news.mongabay.com/example
```

## Method 2: AI-Assisted Batch Addition

Use this prompt with Claude to find and format new stories:

```
Search for restoration projects that affect weather, climate, or precipitation.
For each story found, extract and format as CSV rows:

Query: site:mongabay.com restoration [TOPIC] climate OR weather OR precipitation OR rainfall

Topics to search:
- mangrove restoration flooding
- forest restoration rainfall
- wetland restoration water
- grassland restoration drought
- indigenous restoration climate

For each story, provide a CSV row with:
id,title,description,location,lat,lng,category,climate_impact,date,source,url

Rules:
- Title in quotes
- Description in quotes, 1-2 sentences, must mention climate/water impact
- Look up accurate lat/lng for the location
- Category: forest, wetland, grassland, or marine
- Climate impact: precipitation, water_retention, flood_control, drought_reversal, carbon_storage, cyclone_protection, or indigenous_restoration
- Date in YYYY-MM-DD format
```

## Method 3: Mongabay RSS Feeds

Mongabay provides RSS feeds that can be monitored for new stories:

```
https://news.mongabay.com/feed/?topic=restoration
https://news.mongabay.com/feed/?topic=rewilding
https://news.mongabay.com/feed/?topic=conservation
```

A future enhancement could parse these feeds automatically.

## Method 4: Python Script Template

```python
#!/usr/bin/env python3
"""
Template for adding stories to the ERA CSV.
Requires: pip install geopy
"""

import csv
from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="era-map")

def get_coordinates(location_name):
    """Get lat/lng for a location name."""
    location = geolocator.geocode(location_name)
    if location:
        return location.latitude, location.longitude
    return None, None

def add_story(csv_path, story):
    """Add a story to the CSV file."""
    with open(csv_path, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            story['id'],
            story['title'],
            story['description'],
            story['location'],
            story['lat'],
            story['lng'],
            story['category'],
            story['climate_impact'],
            story['date'],
            story['source'],
            story['url']
        ])

# Example usage:
if __name__ == "__main__":
    # Get next ID
    with open('restoration_climate_stories.csv', 'r') as f:
        next_id = sum(1 for line in f)  # Count lines = next ID

    # Add a new story
    lat, lng = get_coordinates("Mekong Delta, Vietnam")

    add_story('restoration_climate_stories.csv', {
        'id': next_id,
        'title': 'Mangrove Restoration Reduces Storm Surge',
        'description': 'Replanted mangroves have reduced storm surge by 60%.',
        'location': 'Mekong Delta, Vietnam',
        'lat': lat or 10.0452,
        'lng': lng or 105.7469,
        'category': 'marine',
        'climate_impact': 'cyclone_protection',
        'date': '2024-03-15',
        'source': 'Mongabay',
        'url': 'https://news.mongabay.com/example'
    })
```

## Quality Guidelines

1. **Verify climate connection**: Story must demonstrate impact on weather, climate, water cycle, or precipitation
2. **Accurate coordinates**: Use Google Maps or geocoding to get precise lat/lng
3. **Recent stories preferred**: Focus on stories from 2015-present
4. **Diverse coverage**: Aim for geographic diversity and underrepresented regions
5. **Indigenous projects**: Actively seek indigenous-led restoration stories
6. **No duplicates**: Check existing entries before adding

## Data Sources

- **Primary**: [Mongabay](https://mongabay.com) (CC BY-ND 4.0)
- **Secondary**:
  - [Global Forest Watch](https://globalforestwatch.org)
  - [Ecosystem Restoration Communities](https://www.decadeonrestoration.org)
  - [IUCN Restoration Stories](https://www.iucn.org)
  - Academic papers on restoration ecology

## Current Coverage Statistics

As of January 2026:
- **Total stories**: 500
- **Indigenous-led projects**: 100+
- **Countries covered**: 150+
- **Continents**: All 7

Gaps to fill:
- Central Asia
- Small island nations
- Urban restoration projects
- Recent stories (2025-2026)
