# scary-auntie Gap Analysis
## Comparison with Comparable Ethnobotanical & Native Knowledge Database Projects

**Date:** July 2026
**Purpose:** Identify modules/features missing from scary-auntie that comparable projects have, with prioritized recommendations for the botanicals-hub architecture.

---

## Methodology

Analyzed the full scary-auntie codebase (`app.py` 987 lines, `database.py` 1601 lines, 25 templates) to map current capabilities. Compared against seven established projects in the ethnobotanical and Indigenous knowledge domain. Gaps are grouped into five categories and prioritized by impact on the project's mission: a Native knowledge repository with botanicals as the hub of an extensible knowledge wheel.

---

## Current scary-auntie Capabilities (Baseline)

| Feature | Status |
|---------|--------|
| 250 verified plants, three-name system (Native/Latin/English) | ✅ |
| 6 knowledge categories (botanicals/animals/weather/stories/places/crafts) | ✅ |
| Extensible category system (admin can create new spokes) | ✅ |
| Community groups with branding, language, region, map center | ✅ |
| Knowledge records with optional plant-hub linkage | ✅ |
| Teacher/admin review workflow (pending/approved/flagged) | ✅ |
| Bulk review of records | ✅ |
| Blockchain integrity (SHA-256 hash chain) | ✅ |
| Interactive Leaflet map with approved observations | ✅ |
| Photo gallery (images only: png/jpg/jpeg/gif/webp) | ✅ |
| Plant typeahead search (inline JS, all three name types) | ✅ |
| Use-type filters (keyword-derived: medicinal/food/tea/tool/spiritual) | ✅ |
| Language filter on plants | ✅ |
| CSV/JSON export (plants + records) | ✅ |
| Audit log | ✅ |
| Print-friendly pages | ✅ |
| Pagination (24/page default) | ✅ |
| User roles: student < teacher < admin | ✅ |
| Plant CRUD (add + edit) | ✅ |
| Source attribution (author + URL per plant) | ✅ |
| XSS-safe map popups, file upload validation | ✅ |

---

## Gap Categories

### CATEGORY A: Data Sovereignty & Cultural Protocol Control
*Comparable projects: Mukurtu CMS, TEK Clearinghouse / Local Contexts*

This is the highest-priority gap cluster. scary-auntie currently has a binary review system (pending → approved/flagged) but no mechanism for cultural access control — the ability to restrict who can see what based on cultural protocols. This is the single most important feature distinguishing Indigenous knowledge platforms from generic databases.

---

#### A1. Cultural Protocol-Based Access Control
**Comparable projects:** Mukurtu CMS (core feature), TEK Clearinghouse / Local Contexts
**What it is:** Granular access control based on cultural protocols — e.g., "sacred knowledge visible only to initiated elders," "women's medicine visible only to women of the community," "seasonal knowledge visible only during appropriate times." Each knowledge record can be tagged with one or more cultural protocols, and user accounts are associated with protocol access levels.
**Current scary-auntie state:** Review workflow is binary (approved = public, flagged = hidden). No cultural sensitivity tagging. No per-record access control beyond the review status. All approved records are visible to everyone.
**Value for botanicals-hub:** Many plant uses are culturally sensitive — ceremonial, sacred, or restricted to certain groups. Without protocol-based access, communities will withhold their most valuable knowledge, making the hub shallow. This is the #1 feature that Mukurtu built its entire architecture around.
**Implementation scope:** New `cultural_protocols` table (name, description, access_level, group_id). New `record_protocols` junction table linking records to protocols. User-protocol mapping in the users table. Middleware/decorator checking protocol access before rendering records.

---

#### A2. Traditional Knowledge (TK) Labels
**Comparable projects:** TEK Clearinghouse / Local Contexts (originators), Mukurtu CMS (implementer)
**What it is:** A standardized labeling system developed by Local Contexts that tags digital heritage items with cultural context — e.g., "TK Culturally Sensitive," "TK Seasonal," "TK Community Verified," "TK Non-Commercial," "TK Clan." Labels communicate to users how knowledge should be treated, viewed, and shared.
**Current scary-auntie state:** No labeling system. The `tags` field is free-text and user-contributed, not standardized or protocol-linked.
**Value for botanicals-hub:** TK labels are the metadata layer that makes a database trustworthy to Indigenous communities. They signal cultural context at a glance — "this plant knowledge is seasonal, don't share it out of season" or "this is sacred knowledge, handle with respect." This enables the knowledge wheel to be shared more widely while preserving cultural norms.
**Implementation scope:** `tk_labels` table (label_code, display_name, description, icon, community_defined). Link to records via `record_tk_labels` junction. Display labels on record detail pages and plant pages. Admin UI to assign labels.

---

#### A3. Data Sovereignty / Community Governance Framework
**Comparable projects:** TEK Clearinghouse / Local Contexts, Mukurtu CMS
**What it is:** Formal mechanisms for communities to assert sovereignty over their data — consent for sharing, community-controlled publication/removal, data export to community-owned copies, and provenance tracking that links knowledge to the community that holds it.
**Current scary-auntie state:** The blockchain provides integrity (tamper evidence) but not governance (consent, ownership, withdrawal). Groups exist but have no sovereignty controls — an admin can publish any group's knowledge without that group's consent. No mechanism for a community to remove their data or restrict its export.
**Value for botanicals-hub:** Sovereignty is what distinguishes a community-owned repository from an extractive one. Without it, communities won't contribute their deepest knowledge. The blockchain could be extended to record consent and provenance, making it a sovereignty chain, not just an integrity chain.
**Implementation scope:** Add `consent_status` and `consent_given_by` to knowledge_records. Add group-level data governance settings (can_export, can_share_externally, requires_elder_approval). Add community withdrawal workflow with blockchain-recorded consent changes.

---

### CATEGORY B: Linguistic & Multimedia Enrichment
*Comparable projects: FirstVoices, Mukurtu CMS, Alaska Native Knowledge Network*

scary-auntie stores Native names as plain text strings with a `native_language` field. There is no structured linguistic data, no audio, no video, and no language learning module. For a project focused on Alaskan Native knowledge across 10+ languages, this is a significant gap.

---

#### B1. Audio/Video Multimedia Support
**Comparable projects:** Mukurtu CMS (full multimedia), FirstVoices (audio pronunciation), ANKN (oral history audio/video)
**What it is:** Support for audio recordings (elder pronunciations, oral history, songs, stories) and video (ceremonies, demonstrations of plant preparation, field observations). Beyond the current image-only upload.
**Current scary-auntie state:** Upload whitelist is `{png, jpg, jpeg, gif, webp}`. No audio/video support. The `photo_path` field is the only media field. No media player in templates.
**Value for botanicals-hub:** Botanical knowledge in Alaska Native communities is oral. Plant names, uses, and preparation methods are taught by speaking, not writing. Without audio/video, the database captures a text shadow of the knowledge, not the knowledge itself. The "stories" category is particularly hollow without audio — it's a text box for what should be recorded oral history.
**Implementation scope:** Expand `ALLOWED_EXTENSIONS` to include `mp3, wav, ogg, mp4, webm`. Add `media_type` field to knowledge_records (photo/audio/video). Add HTML5 `<audio>`/`<video>` players to `record_detail.html` and `plant_detail.html`. Increase `MAX_CONTENT_LENGTH` or add per-type limits. Add audio upload to the add-observation form.

---

#### B2. Language/Dictionary Module
**Comparable projects:** FirstVoices (core feature), Mukurtu CMS (dictionary module)
**What it is:** A structured language module with: alphabet/orthography display, word dictionary with translations, phrase collection, and audio pronunciation. For each Native language represented (Yupik, Inupiaq, Dena'ina, Ahtna, Tlingit, Haida, Alutiiq, etc.), the module would store words, their English translations, audio pronunciations, and cultural context.
**Current scary-auntie state:** `native_alaskan_name` is a free-text field on plants. `native_language` is a free-text field. No dictionary, no alphabet, no phrase collection, no audio. The typeahead search matches against these text fields but there's no linguistic structure.
**Value for botanicals-hub:** Plant names are the entry point to language revitalization — a child learning "tunuu" for salmonberry is learning Unangam tunuu. A dictionary module linked to plants creates a botanical language resource. Each plant page could show not just the name but the word's linguistic context — part of speech, root morphemes, related words. This makes the hub a language hub, not just a biology hub.
**Implementation scope:** New `languages` table (name, iso_code, alphabet, region, num_speakers). New `dictionary_entries` table (language_id, native_word, english_translation, part_of_speech, audio_path, cultural_context, plant_id optional). New `language_alphabets` table. New routes: `/language/<slug>`, `/language/<slug>/dictionary`. New templates for dictionary browse and word detail. Link plants to dictionary entries.

---

#### B3. Audio Pronunciation for Native Plant Names
**Comparable projects:** FirstVoices (core feature — every word has audio)
**What it is:** Each plant's Native name should have an audio recording of a fluent speaker pronouncing it, playable directly on the plant detail page.
**Current scary-auntie state:** No audio at all. Native names are text only.
**Value for botanicals-hub:** Correct pronunciation is essential for respect and for language learning. A plant name mispronounced by a student is worse than not knowing it. Audio pronunciation on every plant page would make the hub a language teaching tool.
**Implementation scope:** Add `pronunciation_audio_path` to plants table. Add audio upload to `add_plant.html` and `edit_plant.html`. Add `<audio controls>` element to `plant_detail.html` Native Name section.

---

### CATEGORY C: Structured Taxonomy & Deep Botanical Data
*Comparable projects: Native American Ethnobotany Database (Moerman), INVENT, American Indian Health and Diet Project*

scary-auntie stores botanical data in free-text fields (`traditional_uses`, `parts_used`, `preparation`). The use-type filter works by keyword matching against these free-text fields. Comparable projects use structured taxonomies that enable precise querying, cross-referencing, and statistical analysis.

---

#### C1. Structured Use-Category Taxonomy
**Comparable projects:** Native American Ethnobotany Database (Moerman — structured use categories: drug, food, fiber, dye, etc.), INVENT
**What it is:** A structured taxonomy of use categories (medicinal, food, fiber, dye, tool/craft, ceremonial/spiritual, construction, etc.) with many-to-many relationships between plants and use categories. Each plant-use association can have its own metadata (which group uses it this way, preparation details, plant part used).
**Current scary-auntie state:** `traditional_uses` is free text. `get_plant_use_types()` derives categories by keyword matching (`LIKE '%medicinal%'` → "Medicinal"). This is fragile — a plant whose uses mention "tea for colds" is categorized as "Tea" rather than "Medicinal." No structured relationships. Can't query "show me all plants used for dye" reliably.
**Value for botanicals-hub:** Structured use categories transform the hub from a text reference into a queryable database. Moerman's database is valuable because you can ask "which plants do 5+ tribes use for fiber?" scary-auntie can't answer that question. Structured categories also enable the knowledge wheel spokes to reference specific use-cases, making cross-category navigation meaningful.
**Implementation scope:** New `use_categories` table (slug, display_name, parent_id for hierarchy). New `plant_uses` junction table (plant_id, use_category_id, group_id, notes, source). Migration to parse existing `traditional_uses` text into structured records. New filter UI on plants page. Update `plant_detail.html` to show structured uses.

---

#### C2. Plant Part Use Tracking (Structured)
**Comparable projects:** INVENT (core feature), Moerman (structured)
**What it is:** A structured taxonomy of plant parts (root, rhizome, bark, inner bark, stem, leaf, flower, fruit, seed, resin, sap, etc.) with per-use tracking — "for medicinal use, the root is decocted; for food, the berries are eaten raw."
**Current scary-auntie state:** `parts_used` is a single free-text field per plant ("roots, leaves, berries"). No structured taxonomy. Can't filter by plant part. Can't see which parts are used for which purpose.
**Value for botanicals-hub:** Plant part tracking is critical for sustainable harvesting guidance — "only harvest the bark in spring, only harvest the berries in fall." It also enables safety information ("the seeds are toxic but the fruit is edible"). Structured part tracking lets the hub answer "which plants have edible roots?" — a question children and teachers will actually ask.
**Implementation scope:** New `plant_parts` table (slug, display_name). Modify `plant_uses` junction (from C1) to include `plant_part_id`. Or new `plant_parts_used` table (plant_id, part_id, use_category_id, season, notes). Migration from free-text `parts_used`.

---

#### C3. Preparation Method Taxonomy
**Comparable projects:** INVENT (core feature)
**What it is:** A structured taxonomy of preparation methods (decoction, infusion, poultice, tincture, dried, smoked, fermented, raw, roasted, boiled, pounded, etc.) linked to specific plant-use-part combinations.
**Current scary-auntie state:** `preparation` is a single free-text field per plant. No structured taxonomy. Can't filter by preparation method.
**Value for botanicals-hub:** Preparation methods carry cultural knowledge — a decoction implies a different tradition than a poultice. Structured preparation tracking lets the hub teach methods, not just plant identities. It also enables safety ("this plant must be boiled before eating to remove toxins").
**Implementation scope:** New `preparation_methods` table (slug, display_name, description, safety_notes). Link through the `plant_uses` junction table. Migration from free-text `preparation`.

---

#### C4. Cross-Group / Inter-Tribal Reference System
**Comparable projects:** Native American Ethnobotany Database (Moerman — core feature: cross-reference between 291 tribes)
**What it is:** The ability to see which groups/tribes use the same plant, and how their uses differ or converge. Search by group → see all plants they use. Search by plant → see all groups that use it, and how.
**Current scary-auntie state:** Groups exist but have no relationship to plants. The `group_category_activations` table links groups to knowledge categories, not to plants. You can't ask "which groups use spruce for medicine?" or "what plants does the Yupik community use?" There's no group-plant-use connection in the data model.
**Value for botanicals-hub:** This is Moerman's killer feature — cross-tribal comparison reveals shared knowledge and unique innovations. For scary-auntie, it would show that Dena'ina and Ahtna both use Labrador Tea for the same purpose, but Tlingit use it differently. This is the anthropological value of the hub.
**Implementation scope:** Extend the `plant_uses` junction (from C1) to include `group_id`. New routes: `/group/<id>/plants` (plants used by a group), `/plant/<id>/groups` (groups that use a plant). New views on plant_detail and group pages showing cross-references.

---

#### C5. Nutritional Data Module
**Comparable projects:** American Indian Health and Diet Project (core feature)
**What it is:** Nutritional analysis for edible plants — calories, macronutrients, micronutrients, vitamins, minerals per serving. Traditional diet composition analysis.
**Current scary-auntie state:** No nutritional data whatsoever. The `traditional_uses` field may mention "edible" but provides no nutritional context.
**Value for botanicals-hub:** Traditional diets are a major health topic. Nutritional data links botanical knowledge to contemporary health outcomes — "cloudberries have more vitamin C than oranges." This gives the hub public health relevance beyond cultural preservation. Especially important for a project that involves children and schools.
**Implementation scope:** New `plant_nutrition` table (plant_id, calories_per_100g, protein_g, fat_g, carbs_g, fiber_g, vitamin_c_mg, vitamin_a_iu, iron_mg, calcium_mg, notes, source). Admin UI to add/edit nutritional data. Display on `plant_detail.html`. Optional: traditional diet visualization showing nutritional profile of a seasonal subsistence diet.

---

### CATEGORY D: Temporal & Ecological Tracking
*Comparable projects: TEK Clearinghouse, INVENT, American Indian Health and Diet Project*

scary-auntie has no temporal dimension. Plants are static records. Observations have an `entry_date` but no phenological data. There's no way to track when plants are available, how seasons affect their use, or how climate change is affecting them.

---

#### D1. Seasonal Calendar / Seasonal Round
**Comparable projects:** TEK Clearinghouse (seasonal calendars), INVENT (seasonal use calendar), American Indian Health and Diet Project (seasonal food availability)
**What it is:** A visual seasonal calendar showing when each plant is available, when it's harvested, when it flowers, when it fruits. A "seasonal round" view showing the annual cycle of plant-related activities across all categories (berry picking in August, medicine harvesting in spring, etc.).
**Current scary-auntie state:** No seasonal data at all. No `season` or `harvest_time` field on plants. No calendar visualization. The "weather" category has no seasonal structure.
**Value for botanicals-hub:** The seasonal round is the heartbeat of traditional ecological knowledge. Plants aren't just data points — they're available at specific times, and traditional life is organized around their seasonal availability. A seasonal calendar makes the hub a living calendar, not a static list. It also serves as a climate change baseline.
**Implementation scope:** Add `season_start` and `season_end` fields to plants (or to `plant_uses` — availability varies by use). New `seasonal_calendar` route/template showing a 12-month grid with plants color-coded by availability. Filter plants by season on the browse page. Optionally link to the weather category for phenological observations.

---

#### D2. Climate Change Observation Tracking
**Comparable projects:** TEK Clearinghouse / Local Contexts (core feature)
**What it is:** Longitudinal tracking of phenological changes — earlier blooming, range shifts, new species appearing, traditional species disappearing. Elders note "the berries are ripe two weeks earlier than when I was young." The system tracks these observations over time and links them to plants.
**Current scary-auntie state:** Observations have an `entry_date` but no phenological metadata. The "weather" category could hold climate observations, but there's no structured way to track changes over time or link them to specific plants.
**Value for botanicals-hub:** Climate change is the most urgent issue for Alaska Native communities. Plant ranges are shifting north. Berry seasons are changing. This data is irreplaceable — observations recorded now will be invaluable in 50 years. The blockchain makes it tamper-evident, which is exactly what longitudinal climate data needs.
**Implementation scope:** Add `phenology` fields to knowledge_records (observed_season, compared_to_normal, year_first_observed). New `climate_observations` view filtering records tagged as phenological. Time-series visualization on plant_detail showing observations over multiple years. Optionally: baseline data from seed sources for historical comparison.

---

#### D3. Phenological / Seasonal Observation Fields
**Comparable projects:** INVENT (seasonal use tracking), TEK Clearinghouse
**What it is:** When adding an observation, the contributor specifies the season/phenological stage — "plant was flowering," "berries were ripe," "leaves had fallen." This creates structured seasonal data.
**Current scary-auntie state:** The observation form has a date but no phenological fields. You can't filter "show me all observations of ripe berries in August."
**Value for botanicals-hub:** Adds ecological context to every observation, making the knowledge wheel's weather/seasons spoke meaningful. Enables phenological analysis over time.
**Implementation scope:** Add `phenological_stage` field to knowledge_records (enum: budding, flowering, fruiting, seeding, dormant, etc.). Add to add-observation form. Add as filter on category views.

---

### CATEGORY E: Knowledge Organization & Community
*Comparable projects: Alaska Native Knowledge Network, Mukurtu CMS*

scary-auntie has the structural framework for community knowledge (groups, categories, records) but lacks the organizational layer that makes a knowledge repository useful for education, cultural preservation, and intergenerational transmission.

---

#### E1. Oral History Repository (Structured)
**Comparable projects:** ANKN (core feature), Mukurtu CMS (digital heritage items)
**What it is:** A dedicated repository for oral history recordings — audio/video with transcripts, metadata (elder name, date, location, language, topic), and cultural protocol access control. Not just a text box in the "stories" category, but a structured oral history system with transcription support, time-coded segments, and keyword indexing.
**Current scary-auntie state:** The "stories" category is just another knowledge_records bucket with the same fields as every other category. No transcript support, no audio/video, no elder metadata, no time-coded segments. It's a text box.
**Value for botanicals-hub:** Oral history is where the deepest plant knowledge lives — "my grandmother told me that when the fireweed blooms to the top, it's time to pick berries." These stories connect plants to people to seasons to places. A structured oral history repository makes the stories spoke a real archive, not a suggestion box.
**Implementation scope:** New `oral_history` table (elder_name, language, recording_date, recording_path, transcript_path, duration, topics, plant_ids, cultural_protocol_id). New routes and templates for oral history browse and detail. Transcript viewer with time-coded segments. Integration with audio/video upload (from B1) and cultural protocols (from A1).

---

#### E2. Cultural Atlas
**Comparable projects:** ANKN (core feature)
**What it is:** The existing interactive map elevated to a structured cultural atlas — not just observation points, but layered cultural geography: traditional place names, seasonal camp locations, harvest areas, sacred sites (with access control), trails, waterways, vegetation zones. Each layer can be toggled. Place names connect to the "places" knowledge category.
**Current scary-auntie state:** The map shows approved observation points with popups. No layers, no place names, no cultural geography. The "places" category is another text bucket, not a geographic layer.
**Value for botanicals-hub:** A cultural atlas makes the map a knowledge tool, not just a pin display. Botanical knowledge is geographic — plants grow in specific places, and those places have Native names and cultural significance. The atlas connects the botanical hub to the places spoke through geography.
**Implementation scope:** New `place_names` table (native_name, english_name, latitude, longitude, cultural_significance, group_id, protocol_id). Layer toggle UI on map. Integration with the "places" knowledge category. GeoJSON API for place name layers.

---

#### E3. Curriculum Resources Module
**Comparable projects:** ANKN (core feature)
**What it is:** A module for teachers to create and share curriculum resources — lesson plans, learning units, worksheets, activity guides — linked to specific plants and knowledge categories. Each resource specifies target grade level, cultural context, and learning objectives.
**Current scary-auntie state:** No curriculum module. Teachers can review records and manage plants, but can't create educational content within the system. The README mentions "for children, youth, elders" but provides no structured educational content.
**Value for botanicals-hub:** If the hub is for schools (the README mentions schools as group types), curriculum resources are essential. A teacher using scary-auntie in a classroom needs lesson plans, not just a plant database. Curriculum linked to plants makes the hub a teaching hub.
**Implementation scope:** New `curriculum_resources` table (title, description, grade_level, subject, plant_ids, category_id, body, attachments, author_id, status). New routes: `/curriculum`, `/curriculum/<id>`. Admin UI for creating resources. Link from plant_detail to associated curriculum.

---

#### E4. Elder / Contributor Profiles & Biographies
**Comparable projects:** ANKN (elder biographies — core feature)
**What it is:** Structured contributor profiles — especially for elders — with biographical information, language(s), community, areas of expertise, and a catalog of their contributions. Elder profiles link their observations, oral histories, and plant knowledge together.
**Current scary-auntie state:** `recorder_name` is a free-text string on every record. There's no concept of a contributor profile. The same elder's observations across different records can't be linked. No way to see "all knowledge contributed by [elder name]."
**Value for botanicals-hub:** Knowledge comes from people. Honoring the people who hold knowledge is central to Indigenous knowledge systems. Elder profiles make the hub a living connection between plants and the people who know them. They also create an attribution system — knowledge isn't anonymous, it's attributed to the elder who shared it.
**Implementation scope:** New `contributors` table (display_name, native_name, community, languages, bio, photo, role_elder, birth_year, areas_of_expertise). Link to knowledge_records via `contributor_id` (replacing or supplementing `recorder_name`). New routes: `/contributor/<id>`, `/elders`. Contributor catalog on plant_detail showing who has shared knowledge about this plant.

---

#### E5. Collection Narratives
**Comparable projects:** Mukurtu CMS (collection narratives — core feature)
**What it is:** Curated collections of knowledge records with a narrative frame — e.g., "Our Community's Berry Harvest Through the Year" pulls together plant records, weather observations, stories, and photos into a guided narrative. Not just a category filter, but an editorially curated journey through the knowledge wheel.
**Current scary-auntie state:** No collection or curation mechanism. Knowledge is organized by category (spokes) and by plant (hub), but there's no way to create a curated path through the knowledge.
**Value for botanicals-hub:** Collections make the knowledge wheel navigable for learners. A child doesn't browse "all botanicals" — they follow "Grandma's berry patch story" which links plants, weather, stories, and places. Collections are the editorial layer that connects hub to spokes into meaningful journeys.
**Implementation scope:** New `collections` table (title, description, cover_image, author_id, group_id, status). New `collection_items` table (collection_id, record_id, plant_id, display_order, annotation). New routes: `/collections`, `/collection/<id>`. Admin UI for creating and managing collections.

---

## Prioritized Build Recommendations

### Tier 1 — Build First (Critical for Mission Alignment)

| Priority | Module | Comparable Projects | Est. Effort | Rationale |
|----------|--------|---------------------|-------------|-----------|
| **1** | A1: Cultural Protocol Access Control | Mukurtu, TEK/Local Contexts | Large | Without this, communities won't contribute sensitive knowledge. This is the #1 feature that distinguishes Indigenous platforms. |
| **2** | B1: Audio/Video Multimedia Support | Mukurtu, FirstVoices, ANKN | Medium | Botanical knowledge is oral. The "stories" category is meaningless without audio. Low technical complexity, high impact. |
| **3** | A2: Traditional Knowledge Labels | TEK/Local Contexts, Mukurtu | Small-Medium | Standardized labels are the trust layer. Relatively easy to implement; large cultural value. |
| **4** | D1: Seasonal Calendar / Seasonal Round | TEK, INVENT, AIHDP | Medium | The seasonal round is the organizing principle of TEK. Makes the hub a living calendar. |
| **5** | C1: Structured Use-Category Taxonomy | Moerman, INVENT | Medium | Transforms free-text into queryable data. Foundation for C2, C3, C4. |

### Tier 2 — Build Second (High Value, Moderate Effort)

| Priority | Module | Comparable Projects | Est. Effort | Rationale |
|----------|--------|---------------------|-------------|-----------|
| **6** | E4: Elder / Contributor Profiles | ANKN | Medium | Knowledge comes from people. Attribution is a cultural imperative. |
| **7** | C4: Cross-Group / Inter-Tribal Reference | Moerman | Medium | Depends on C1. Moerman's killer feature — comparative ethnobotany. |
| **8** | E1: Oral History Repository (Structured) | ANKN, Mukurtu | Large | Depends on B1 (audio/video). Makes the "stories" spoke real. |
| **9** | B2: Language/Dictionary Module | FirstVoices, Mukurtu | Large | 10+ languages represented; no linguistic structure exists. High cultural value. |
| **10** | D2: Climate Change Observation Tracking | TEK Clearinghouse | Medium | Urgent for Alaska. Blockchain makes longitudinal data trustworthy. |

### Tier 3 — Build Third (Valuable Enhancements)

| Priority | Module | Comparable Projects | Est. Effort | Rationale |
|----------|--------|---------------------|-------------|-----------|
| **11** | C2: Plant Part Use Tracking (Structured) | INVENT | Medium | Depends on C1. Safety + harvesting guidance. |
| **12** | C3: Preparation Method Taxonomy | INVENT | Medium | Depends on C1. Cultural knowledge of methods. |
| **13** | E3: Curriculum Resources Module | ANKN | Medium | Important if schools are target users. |
| **14** | E5: Collection Narratives | Mukurtu | Medium | Editorial layer for guided learning journeys. |
| **15** | E2: Cultural Atlas | ANKN | Large | Elevates existing map to structured cultural geography. |
| **16** | A3: Data Sovereignty / Governance Framework | TEK, Mukurtu | Large | Policy/UX work more than code. Blockchain can be extended. |
| **17** | B3: Audio Pronunciation for Plant Names | FirstVoices | Small | Subset of B1/B2. Quick win once audio upload exists. |
| **18** | C5: Nutritional Data Module | AIHDP | Medium | Public health angle. Standalone — no dependencies. |
| **19** | D3: Phenological Observation Fields | INVENT, TEK | Small | Quick add-on to observation form. |

---

## Dependency Graph

```
A1 (Cultural Protocols) ──┬── E1 (Oral History Repository)
                           ├── E2 (Cultural Atlas — sacred sites)
                           └── A3 (Data Sovereignty)

B1 (Audio/Video Upload) ──┬── E1 (Oral History)
                           ├── B3 (Pronunciation Audio)
                           └── B2 (Dictionary — audio for words)

C1 (Use Taxonomy) ──┬── C2 (Plant Part Tracking)
                     ├── C3 (Preparation Method Taxonomy)
                     └── C4 (Cross-Group References)

D1 (Seasonal Calendar) ──┬── D2 (Climate Change Tracking)
                          └── D3 (Phenological Fields)

A2 (TK Labels) — standalone, but should integrate with A1

E4 (Contributor Profiles) — standalone, but integrates with everything
E3 (Curriculum Resources) — standalone
E5 (Collection Narratives) — standalone, but benefits from all other modules
C5 (Nutritional Data) — fully standalone
```

---

## Summary

scary-auntie has a solid architectural foundation — the hub-and-spoke model, blockchain integrity, group customization, and review workflow are well-built. The gaps fall into five clusters:

1. **Data sovereignty & cultural protocol control** (A1-A3) — the most important gap. Mukurtu and TEK/Local Contexts built their entire platforms around this. scary-auntie has no cultural access control.

2. **Linguistic & multimedia enrichment** (B1-B3) — scary-auntie is text-and-images only. Audio is essential for oral knowledge and language. FirstVoices and Mukurtu treat audio as foundational.

3. **Structured botanical taxonomy** (C1-C5) — scary-auntie's free-text fields (`traditional_uses`, `parts_used`, `preparation`) can't be reliably queried. Moerman and INVENT use structured taxonomies.

4. **Temporal & ecological tracking** (D1-D3) — no seasonal data, no climate change tracking. TEK Clearinghouse treats these as core features.

5. **Knowledge organization & community** (E1-E5) — no oral history structure, no elder profiles, no curriculum resources, no cultural atlas, no collection narratives. ANKN and Mukurtu have all of these.

The recommended build order prioritizes cultural protocol access control (A1) and audio/video support (B1) as the two gaps that most fundamentally limit the project's ability to serve as a Native knowledge repository. These are followed by TK labels (A2), seasonal calendars (D1), and structured use taxonomy (C1) — all of which are achievable in the current Flask/SQLite architecture without major infrastructure changes.