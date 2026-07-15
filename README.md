# scary-auntie

**A customizable Native knowledge repository with botanical database at the hub, built with tamper-evident blockchain integrity.**

## Overview

scary-auntie is a Flask-based web application that enables communities to record ecological and cultural knowledge using Native names, Latin binomials, and English names. The botanical database is the **hub of the wheel** — the central reference — with extensible knowledge categories as **spokes** connecting back to plants and to each other. Every entry is permanently recorded on an internal blockchain, creating a tamper-evident chain of knowledge.

## Architecture — Hub of the Wheel

```
                        ┌─────────┐
                        │ GLOSSARY │
                        └────┬─────┘
                             │
   ┌───────┐  ┌────────┐  ┌──┴──────┐  ┌───────┐
   │ELDERS │  │CALENDAR│  │BOTANICAL│  │ USES  │
   └───┬───┘  └───┬────┘  └────┬────┘  └───┬───┘
       │          │            │            │
       │     ┌────┴────┐  ┌────┴────┐  ┌────┴────┐
       │     │ WEATHER │  │ STORIES │  │ANIMALS │
       │     └─────────┘  └─────────┘  └─────────┘
       │
  ┌────┴─────┐
  │CURRICULUM│
  └──────────┘
```

- **Plants (Botanicals)** = the HUB. The prepopulated, verified reference database of 292 Alaskan Native botanicals. Every other module connects back to specific plants.
- **Knowledge Categories** = the SPOKES. Extensible topics: animals, weather, stories & oral history, place names, crafts, and more.
- **Knowledge Records** = observations within any category, contributed by community members and reviewed by teachers/admins.
- **Groups** = community customization. Each clan, tribe, village, or school can customize their name, languages, territory, map center, branding colors, and which categories they use.

## Modules

### Core Botanical Database (The Hub)
- **292 verified plants** with three-name system (Native/Latin/English)
- Search by name, family, use type (medicinal/food/tea/tool/spiritual)
- Plant typeahead search for 292 plants with keyboard navigation
- Print-friendly plant detail pages
- Admin: add, edit, export (CSV/JSON) plants
- Pagination (24/page) on all plant lists

### Knowledge Categories (Spokes)
- 6 default categories: botanicals (hub), animals, weather, stories, places, crafts
- Admin-creatable custom categories
- Browse observations by category
- Category counts on the Knowledge Wheel

### Seasonal Calendar
- Plants grouped by seasonal availability (spring/summer/fall/winter)
- Text-mines `traditional_uses` and `parts_used` fields for seasonal keywords
- `season_start` / `season_end` columns on plants table for explicit seasonal data
- Filterable by season with visual tabs

### Plant Uses Cross-Reference
- Records how specific groups/clans use specific plants for what purposes
- Use categories: food, medicinal, fiber, dye, tool, spiritual, construction, other
- Filterable by group and use category
- Summary dashboard with use-category counts
- Comparable to Moerman's Native American Ethnobotany Database

### Glossary / Dictionary
- Native language terms with definitions
- Optional link to specific plants from the hub
- Search by term or language
- Teacher/admin can add terms
- Comparable to FirstVoices dictionary entries

### Elder / Knowledge-Holder Profiles
- Biographies of elders and knowledge holders
- Consent-based access control: public, community, restricted
- Records community, role, languages, region, birth year
- Respects cultural protocols — restricted profiles are admin-only
- Comparable to ANKN elder biographies and Mukurtu digital heritage

### Curriculum / Lesson Plans
- Educational lesson plans linked to specific plants
- Fields: grade level, subject, duration, objectives, materials, activities, assessment
- Filterable by grade and subject
- Print-friendly lesson detail pages
- Comparable to ANKN curriculum resources

### Cultural Protocols
- `cultural_protocol` field on plants and knowledge records
- Access control for sacred/restricted knowledge
- Respects Indigenous data sovereignty principles
- Comparable to Mukurtu CMS protocol-based access

### Community Observations
- Unified observation form for any knowledge category
- Optional plant link back to the hub
- Photo upload with validation
- GPS coordinates with geolocation helper
- Teacher/admin review system with bulk approve/flag
- Blockchain-recorded for tamper evidence

### Interactive Map
- Leaflet-based map of approved observations
- XSS-safe popups (all user content escaped)
- GPS coordinates for geotagged observations

### Photo Gallery
- Grid of approved observation photos
- Captions with plant and category info

### Blockchain Integrity
- Every database operation is hashed into a SHA-256 blockchain
- Each block references the previous block's hash
- Built-in verification detects any tampering
- Atomic transactions — plant + block committed together
- All new modules (glossary, elders, plant_uses, lesson_plans) are blockchain-integrated

### Security
- Salted password hashing (Werkzeug PBKDF2)
- Session ID regeneration on login
- All API endpoints require authentication (except public categories)
- Debug mode off by default
- File upload validation + secure filename
- Cultural protocol access control

## Prepopulated Database

**292 verified plants** (250 original + 42 from gap analysis) from authoritative sources:

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
| **Gap Analysis (2026)** | 42 species from Garibaldi PDF gap analysis: ferns, lichens, mosses, seaweeds, fungi, herbs | 42 |

**Sources**: Garibaldi (1999) — Medicinal Flora of the Alaska Natives (primary source for gap analysis), Kari (1987), Jones (1983), Schofield (1993), Heller (1976), USFS Alaska Region TEK, UAF Museum of the North Ethnobotany Film Series, State of Alaska Ethnobotany Project, Wikipedia ethnobotanical articles, Telander (2012), Olson (1997)

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

## Gap Analysis — How scary-auntie Compares

| Feature | scary-auntie | Moerman DB | Mukurtu | FirstVoices | ANKN |
|---------|:---:|:---:|:---:|:---:|:---:|
| Plant database with Native names | ✅ | ✅ | — | — | — |
| Cross-reference tribe↔plant uses | ✅ | ✅ | — | — | — |
| Seasonal calendar | ✅ | — | — | — | — |
| Cultural protocols / access control | ✅ | — | ✅ | — | — |
| Glossary / dictionary | ✅ | — | ✅ | ✅ | — |
| Elder/knowledge-holder profiles | ✅ | — | ✅ | — | ✅ |
| Curriculum / lesson plans | ✅ | — | — | — | ✅ |
| Blockchain integrity | ✅ | — | — | — | — |
| Community groups/clans | ✅ | ✅ | ✅ | — | — |
| Interactive map | ✅ | — | — | — | — |
| Photo gallery | ✅ | — | ✅ | — | — |
| Open source / self-hosted | ✅ | — | ✅ | — | — |

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
├── app.py                  # Flask application — routes, auth, API, modules
├── database.py             # Database + blockchain + all module functions
├── seed_data.py            # 292 verified Alaskan botanical seed entries
├── dedup_plants.py         # One-time deduplication script (8 merge pairs)
├── requirements.txt        # Python dependencies
├── data/
│   └── scary_auntie.db     # SQLite database (not tracked in git)
├── static/
│   ├── css/
│   │   └── style.css       # Application styles + print styles
│   └── uploads/            # User-submitted photos
└── templates/
    ├── base.html           # Base template with nav
    ├── index.html          # Public landing — wheel + recent observations
    ├── plants.html         # Plant browser (paginated + filters)
    ├── plant_detail.html   # Plant detail (print-friendly)
    ├── add_observation.html # Unified observation form (typeahead)
    ├── map.html            # Interactive map
    ├── knowledge_wheel.html # Category overview
    ├── category_view.html  # Browse observations by category
    ├── record_detail.html  # Single observation detail
    ├── calendar.html       # Seasonal availability calendar
    ├── glossary.html       # Native language dictionary
    ├── elders.html         # Elder/knowledge-holder profiles
    ├── elder_detail.html   # Single elder profile
    ├── uses.html           # Cross-reference: group↔plant uses
    ├── curriculum.html     # Lesson plan browser
    ├── lesson_detail.html  # Single lesson plan (print-friendly)
    ├── gallery.html        # Photo gallery
    └── admin/              # Teacher/admin templates
        ├── login.html
        ├── dashboard.html
        ├── entries.html       # Legacy botanical entries
        ├── entry_detail.html  # Legacy entry review
        ├── records.html       # Knowledge records (bulk review)
        ├── record_detail.html # New record review
        ├── plants.html        # Plant management (paginated)
        ├── edit_plant.html    # Plant editor
        ├── add_plant.html
        ├── categories.html    # Knowledge category management
        ├── groups.html        # Community group management
        ├── add_lesson.html    # Lesson plan editor
        ├── blockchain.html
        ├── audit.html         # Audit log viewer
        └── users.html
```

## Database Schema

- **plants** — Verified botanical information with source attribution (THE HUB)
- **knowledge_categories** — Extensible knowledge domains (spokes)
- **knowledge_records** — Community observations within any category
- **knowledge_entries** — Legacy botanical observations (backward compatible)
- **groups** — Community/clan/tribe customization
- **group_category_activations** — Which categories each group has activated
- **glossary** — Native language terms and definitions
- **elders** — Elder/knowledge-holder profiles with consent-based access
- **plant_uses** — Cross-reference: which groups use which plants for what
- **lesson_plans** — Curriculum resources linked to plants
- **users** — Teacher/admin accounts with optional group assignment
- **block_chain** — Tamper-evident hash chain for all operations
- **audit_log** — Activity logging

## Customizing for Your Community

1. **Create a Group** — Admin panel → Groups → Create New Group
2. Set your community name, type (clan/tribe/village/school), Native language(s), and geographic region
3. Customize the map center coordinates and zoom for your territory
4. Choose your branding colors (primary + accent)
5. **Activate Categories** — Select which knowledge categories your group uses
6. **Record Plant Uses** — Document how your community uses specific plants
7. **Add Glossary Terms** — Preserve your Native language plant names and terms
8. **Add Elder Profiles** — Honor knowledge holders (always with consent)
9. **Create Lesson Plans** — Build curriculum tied to your local plants
10. **Add Observations** — Community members contribute through the unified form

## License

MIT License — Honor the knowledge, protect the data, teach the children.