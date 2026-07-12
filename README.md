# scary-auntie

**A community ecological knowledge database for Alaskan Native botanicals, built with tamper-evident blockchain integrity.**

## Overview

scary-auntie is a Flask-based web application that enables children and adolescents to record observations about Alaskan plants using Native Alaskan names, Latin binomials, and English names. Every entry is permanently recorded on an internal blockchain, creating a tamper-evident chain of ecological knowledge.

## Features

### Public Site (for children/adolescents)
- **Browse Plants**: View 24 verified Alaskan Native botanicals with Native names, Latin binomials, and English names
- **Add Observation**: Submit plant observations with name, age, location, GPS coordinates, photos, and personal knowledge
- **Interactive Map**: Explore approved observations across Alaska
- **Three-Name System**: Every plant supports Native Alaskan name, Latin binomial, and English common name

### Teacher/Admin Backend
- **Dashboard**: Overview stats, pending reviews, blockchain status
- **Review Entries**: Approve or flag student submissions
- **Manage Plants**: Add new verified botanicals to the database
- **Blockchain Monitor**: Verify integrity of the entire chain
- **User Management**: Create teacher and admin accounts (admin only)

### Blockchain Integrity
- Every database operation is hashed into a SHA-256 blockchain
- Each block references the previous block's hash
- Built-in verification detects any tampering
- Author attribution preserved for all scraped/cited data

## Prepopulated Database

24 verified plants from authoritative sources:

| Plant | Native Name(s) | Language |
|-------|---------------|----------|
| Cloudberry | Aqpik, Akpiq | Yupik, Inupiaq |
| Labrador Tea | Cen'ana, Cena'a | Dena'ina, Ahtna |
| Fireweed | Cama'i, Pamiuqtaq | Dena'ina, Yupik |
| Crowberry | Pauraq, Kanat'aah | Yupik, Athabascan |
| Sitka Valerian | Various | Southeast/Southcentral |
| ...and 19 more | | |

Sources: Garibaldi (1999), Kari (1987), Jones (1983), Schofield (1993), USFS Alaska Region TEK

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
- **Password**: `scary-auntie-admin`

## Project Structure

```
scary-auntie/
├── app.py                  # Flask application
├── database.py             # Database + blockchain layer
├── seed_data.py            # Verified Alaskan botanical seed data
├── requirements.txt        # Python dependencies
├── data/
│   └── scary_auntie.db     # SQLite database
├── static/
│   ├── css/
│   │   └── style.css       # Application styles
│   └── uploads/            # User-submitted photos
└── templates/
    ├── base.html           # Base template
    ├── index.html          # Public landing
    ├── plants.html         # Plant browser
    ├── plant_detail.html   # Plant detail page
    ├── add_entry.html      # Observation entry form
    ├── map.html            # Interactive map
    └── admin/              # Teacher/admin templates
        ├── login.html
        ├── dashboard.html
        ├── entries.html
        ├── entry_detail.html
        ├── plants.html
        ├── add_plant.html
        ├── blockchain.html
        └── users.html
```

## Database Schema

- **plants** — Verified botanical information with source attribution
- **knowledge_entries** — Community observations by children/adolescents
- **block_chain** — Tamper-evident hash chain for all operations
- **users** — Teacher/admin accounts
- **audit_log** — Activity logging

## License

MIT License — Honor the knowledge, protect the data, teach the children.
