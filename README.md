# scary-auntie

**A customizable Native knowledge repository with botanical database at the hub, built with tamper-evident blockchain integrity.**

## Overview

scary-auntie is a Flask-based web application that enables communities to record ecological and cultural knowledge using Native names, Latin binomials, and English names. The botanical database is the **hub of the wheel** — the central reference — with extensible knowledge categories as **spokes** connecting back to plants and to each other. Every entry is permanently recorded on an internal blockchain, creating a tamper-evident chain of knowledge.

## Architecture — Hub of the Wheel

```
                    ┌─────────┐
                    │  WEATHER │
                    └────┬─────┘
                         │
         ┌──────┐  ┌─────┴─────┐  ┌───────┐
         │STORIES│──┤ BOTANICALS├──│ANIMALS│
         └──────┘  └─────┬─────┘  └───────┘
                         │
              ┌──────────┼──────────┐
              │          │          │
         ┌────┴───┐ ┌───┴───┐ ┌────┴───┐
         │PLACES  │ │CRAFTS │ │  ...   │
         └────────┘ └───────┘ └────────┘
```

- **Plants (Botanicals)** = the HUB. The prepopulated, verified reference database of 250 Alaskan Native botanicals. Every other category can link back to specific plants.
- **Knowledge Categories** = the SPOKES. Extensible topics: animals, weather, stories & oral history, place names, crafts, and more. Each group activates the categories relevant to their community.
- **Knowledge Records** = observations within any category, contributed by community members (children, youth, elders) and reviewed by teachers/admins.
- **Groups** = community customization. Each clan, tribe, village, or school can customize their name, languages, geographic territory, map center, branding colors, and which categories they use.

## Features

### Public Site (for children, youth, elders)
- **Browse Plants**: 250 verified Alaskan Native botanicals with Native names, Latin binomials, and English names
- **Knowledge Wheel**: Visual overview of all knowledge categories with observation counts
- **Add Observation**: Unified entry form for any knowledge category, with optional plant link
- **Interactive Map**: Explore approved observations across Alaska
- **Three-Name System**: Every plant supports Native name, Latin binomial, and English name
- **Category Browsing**: View observations by knowledge category (botanicals, animals, weather, etc.)

### Teacher/Admin Backend
- **Dashboard**: Overview stats, pending reviews, blockchain status, recent records
- **Review Records**: Approve or flag community submissions across all categories
- **Manage Plants**: Add new verified botanicals (with pagination + search for 250+ plants)
- **Categories**: Create and manage knowledge categories (spokes of the wheel)
- **Groups**: Create community groups with custom branding, languages, and territory
- **Blockchain Monitor**: Verify integrity of the entire chain
- **User Management**: Create teacher and admin accounts with group assignment

### Blockchain Integrity
- Every database operation is hashed into a SHA-256 blockchain
- Each block references the previous block's hash
- Built-in verification detects any tampering
- Atomic transactions — plant + block are committed together
- Author attribution preserved for all scraped/cited data

### Security
- Passwords hashed with Werkzeug's `generate_password_hash` (salted PBKDF2)
- Session ID regenerated on login (prevents session fixation)
- All API endpoints require authentication (except public category list)
- Debug mode off by default (set `FLASK_DEBUG=1` to enable)
- XSS-safe map popups (all user content escaped)
- File upload validation (extension whitelist + secure filename)
- Configurable admin password via `ADMIN_PASSWORD` environment variable

## Prepopulated Database

**250 verified plants** (deduplicated from 258 across 6 seed batches) from authoritative sources:

| Category | Examples | Count |
|----------|----------|-------|
| **Berries** | Cloudberry, Blueberry, Crowberry, Haskap, Rose Hips, Highbush Cranberry, Bunchberry, Sitka Mountain Ash, Wild Strawberry | 9 |
| **Medicinal Herbs** | Labrador Tea, Yarrow, Coltsfoot, Fireweed, Goldthread, Arnica, Chamomile, Horsetail, Valerian, Buckbean, Lousewort, Paintbrush, Avens, Bluebells, Twinflower | 15 |
| **Root/Tuber Foods** | Alpine Sweetvetch, Eskimo Potato, Silverweed | 3 |
| **Trees** | White Spruce, Balsam Poplar, Paper Birch | 3 |
| **Mushrooms** | Tinder Fungus, Chaga | 2 |
| **Spring Greens** | Cow Parsnip, Nettle, Fireweed Shoots, Solomon's Seal, Watermelon Berry, Mountain Sorrel, Oysterplant | 7 |
| **Other** | Kinnikinnick, Soapberry, Prickly Rose, Narcissus Anemone, Arctic Lupine, Prairie Smoke | 6 |
| **Additional Batches 3–6** | 205 more botanicals from Wikipedia, USFS, and ethnobotanical literature | 205 |

**Sources**: Garibaldi (1999), Kari (1987), Jones (1983), Schofield (1993), Heller (1976), USFS Alaska Region TEK, Wikipedia ethnobotanical articles, Telander (2012), Olson (1997)

**Languages represented**: Yupik, Inupiaq, Dena'ina, Ahtna, Tlingit, Haida, Alutiiq/Sugpiaq, Aleut/Unangan, Athabascan (multiple dialects), Gwich'in, Tsimshian, and others

## Default Knowledge Categories

| Slug | Display Name | Icon | Type |
|------|-------------|------|------|
| `botanicals` | Botanical Knowledge | 🌿 | **HUB** |
| `animals` | Animal Knowledge | 🐺 | Spoke |
| `weather` | Weather & Seasons | 🌧️ | Spoke |
| `stories` | Stories & Oral History | 🗣️ | Spoke |
| `places` | Place Names & Geography | 🗺️ | Spoke |
| `crafts` | Crafts & Material Culture | 🪢 | Spoke |

Custom categories can be created from the admin panel.

## Installation

```bash
cd ~/projects/scary-auntie
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running the App

```bash
python app.py
```

The app runs on `http://0.0.0.0:9192`

Default admin credentials (change in production):
- **Username**: `admin`
- **Password**: `scary-auntie-admin` (or set `ADMIN_PASSWORD` env var)

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | Random token | Flask session secret key |
| `ADMIN_PASSWORD` | `scary-auntie-admin` | Default admin password (first run only) |
| `FLASK_DEBUG` | `0` | Set to `1` to enable debug mode |

## Project Structure

```
scary-auntie/
├── app.py                  # Flask application — routes, auth, API
├── database.py             # Database + blockchain layer + migrations
├── seed_data.py            # 250 verified Alaskan botanical seed entries
├── dedup_plants.py         # One-time deduplication script (8 merge pairs)
├── requirements.txt        # Python dependencies
├── data/
│   └── scary_auntie.db     # SQLite database (not tracked in git)
├── static/
│   ├── css/
│   │   └── style.css       # Application styles
│   └── uploads/            # User-submitted photos
└── templates/
    ├── base.html           # Base template
    ├── index.html          # Public landing — wheel overview
    ├── plants.html         # Plant browser (paginated)
    ├── plant_detail.html   # Plant detail page
    ├── add_observation.html # Unified observation form
    ├── map.html            # Interactive map
    ├── knowledge_wheel.html # Category overview
    ├── category_view.html  # Browse observations by category
    ├── record_detail.html  # Single observation detail
    └── admin/              # Teacher/admin templates
        ├── login.html
        ├── dashboard.html
        ├── entries.html       # Legacy botanical entries
        ├── entry_detail.html  # Legacy entry review
        ├── records.html       # New knowledge records
        ├── record_detail.html # New record review
        ├── plants.html        # Plant management (paginated)
        ├── add_plant.html
        ├── categories.html    # Knowledge category management
        ├── groups.html        # Community group management
        ├── blockchain.html
        └── users.html
```

## Database Schema

- **plants** — Verified botanical information with source attribution (THE HUB)
- **knowledge_categories** — Extensible knowledge domains (spokes)
- **knowledge_records** — Community observations within any category
- **knowledge_entries** — Legacy botanical observations (backward compatible)
- **groups** — Community/clan/tribe customization
- **group_category_activations** — Which categories each group has activated
- **users** — Teacher/admin accounts with optional group assignment
- **block_chain** — Tamper-evident hash chain for all operations
- **audit_log** — Activity logging

## Customizing for Your Community

1. **Create a Group** — Admin panel → Groups → Create New Group
2. Set your community name, type (clan/tribe/village/school), Native language(s), and geographic region
3. Customize the map center coordinates and zoom for your territory
4. Choose your branding colors (primary + accent)
5. **Activate Categories** — Select which knowledge categories your group uses
6. **Add Observations** — Community members contribute through the unified form

## License

MIT License — Honor the knowledge, protect the data, teach the children.