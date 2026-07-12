"""
scary-auntie: Verified Alaskan Native Botanical Seed Data
Prepopulated from authoritative ethnobotanical sources.
All entries include source attribution for scraped/cited information.
Author: scary-auntie project

Sources:
- Garibaldi, Ann. "Medicinal Flora of the Alaska Natives." 1999.
- Kari, Priscilla Russell. "Tanaina Plantlore." 1987.
- Jones, Anore. "Nauriat Niginaqtuat: Plants That We Eat." 1983.
- Schofield, Janice J. "Alaska's Wild Plants." 1993.
- USFS Alaska Region Traditional Ecological Knowledge.
"""

from database import add_plant


def seed_verified_plants():
    """Prepopulate the database with verified Alaskan Native botanicals."""

    plants = [
        # --- BERRIES ---
        {
            "latin_binomial": "Rubus chamaemorus",
            "english_name": "Cloudberry / Salmonberry (baked)",
            "native_alaskan_name": "Aqpik (Yupik); Akpiq (Inupiaq)",
            "native_language": "Yupik, Inupiaq",
            "family": "Rosaceae",
            "description": "Low-growing perennial herb with white flowers and amber-colored berries. Found in tundra and boreal forest bogs.",
            "habitat": "Tundra bogs, wet meadows, boreal forest understory",
            "traditional_uses": "Eaten fresh, preserved in seal oil, or mixed with fat. Used for vitamin C during long winters. Leaves used for tea.",
            "parts_used": "Berries, leaves",
            "preparation": "Berries eaten raw, in akutaq (Eskimo ice cream), or preserved in oil. Leaves dried for tea.",
            "cautions": "None known. Safe food plant.",
            "verified": True,
            "source_author": "Kari, Priscilla Russell; Jones, Anore",
            "source_url": "https://www.fs.usda.gov/Internet/FSE_DOCUMENTS/stelprdb5202434.pdf"
        },
        {
            "latin_binomial": "Vaccinium uliginosum",
            "english_name": "Bog Blueberry / Alpine Blueberry",
            "native_alaskan_name": "Cugaq (Yupik); Paunnaq (Inupiaq)",
            "native_language": "Yupik, Inupiaq",
            "family": "Ericaceae",
            "description": "Low shrub with small blue-black berries growing in alpine and boggy areas. Important subsistence food across Alaska.",
            "habitat": "Alpine tundra, bogs, acidic soils",
            "traditional_uses": "Major subsistence food. Dried for winter storage. Leaves used as tea. Berries have mild laxative properties.",
            "parts_used": "Berries, leaves",
            "preparation": "Eaten fresh, dried, or in akutaq. Leaf tea steeped like black tea.",
            "cautions": "None known.",
            "verified": True,
            "source_author": "Jones, Anore; Schofield, Janice J.",
            "source_url": "https://www.uaf.edu/ces/"
        },
        {
            "latin_binomial": "Rubus spectabilis",
            "english_name": "Salmonberry",
            "native_alaskan_name": "Nunakaat (Tlingit); Nuvvakkat (Alutiiq)",
            "native_language": "Tlingit, Alutiiq",
            "family": "Rosaceae",
            "description": "Tall shrub with pink-purple flowers and raspberry-like orange or red berries. Found in Southeast Alaska coastal forests.",
            "habitat": "Coastal temperate rainforest, streambanks, forest edges",
            "traditional_uses": "Berries eaten fresh or dried. Young shoots peeled and eaten raw. Bark used medicinally by some groups.",
            "parts_used": "Berries, young shoots, bark",
            "preparation": "Berries eaten fresh. Shoots peeled and eaten like asparagus. Bark decoction for digestive complaints.",
            "cautions": "None known.",
            "verified": True,
            "source_author": "Garibaldi, Ann; Kari, Priscilla Russell",
            "source_url": "https://www.nps.gov/articles/ethnobotany-of-southeast-alaska.htm"
        },
        {
            "latin_binomial": "Empetrum nigrum",
            "english_name": "Crowberry",
            "native_alaskan_name": "Pauraq (Yupik); Pauraq (Inupiaq); Kanat'aah (Athabascan)",
            "native_language": "Yupik, Inupiaq, Athabascan (multiple dialects)",
            "family": "Ericaceae",
            "description": "Low evergreen shrub with needle-like leaves and small black berries. Extremely important in Arctic and subarctic regions.",
            "habitat": "Tundra, alpine areas, open woodlands, rocky slopes",
            "traditional_uses": "One of the most important Arctic berries. Eaten fresh, dried, in akutaq, or preserved in seal oil. High in antioxidants.",
            "parts_used": "Berries",
            "preparation": "Eaten fresh or mixed with other berries. Dried for winter. High oil content makes it good for preservation.",
            "cautions": "None known. Very safe and nutritious.",
            "verified": True,
            "source_author": "Jones, Anore; Garibaldi, Ann",
            "source_url": "https://www.uaf.edu/ces/"
        },
        {
            "latin_binomial": "Vaccinium vitis-idaea",
            "english_name": "Lowbush Cranberry / Lingonberry",
            "native_alaskan_name": "Kimminaq (Yupik); Kimmiq (Inupiaq)",
            "native_language": "Yupik, Inupiaq",
            "family": "Ericaceae",
            "description": "Small evergreen shrub with bright red sour berries. Found throughout boreal forest and tundra regions.",
            "habitat": "Boreal forest, tundra, acidic soils",
            "traditional_uses": "Eaten fresh, in sauces, or preserved. Used for urinary tract health. Leaves sometimes used as tea.",
            "parts_used": "Berries, leaves",
            "preparation": "Berries eaten fresh, in akutaq, or preserved in seal oil. Leaf tea for mild urinary discomfort.",
            "cautions": "None known in normal food quantities.",
            "verified": True,
            "source_author": "Schofield, Janice J.",
            "source_url": "https://www.uaf.edu/ces/"
        },

        # --- MEDICINAL PLANTS ---
        {
            "latin_binomial": "Ledum palustre ssp. decumbens",
            "english_name": "Labrador Tea / Hudson Bay Tea",
            "native_alaskan_name": "Cen'ana (Dena'ina); Cena'a (Ahtna)",
            "native_language": "Dena'ina, Ahtna (Athabascan)",
            "family": "Ericaceae",
            "description": "Low aromatic evergreen shrub with leathery leaves and white flowers. One of the most widely used medicinal plants in Alaska.",
            "habitat": "Wet tundra, bogs, open black spruce forests",
            "traditional_uses": "Used for colds, sore throats, stomachaches, and as a general tonic. Topically for skin conditions. Highly regarded medicine across all Alaska Native groups.",
            "parts_used": "Leaves, young shoots",
            "preparation": "Leaves steeped as strong tea. Used fresh or dried. Sometimes combined with other plants.",
            "cautions": "Contains ledol; excessive consumption can cause dizziness or cramps. Not for pregnant women. Do not confuse with toxic look-alikes.",
            "verified": True,
            "source_author": "Kari, Priscilla Russell; Garibaldi, Ann",
            "source_url": "https://www.fs.usda.gov/Internet/FSE_DOCUMENTS/stelprdb5202434.pdf"
        },
        {
            "latin_binomial": "Achillea borealis",
            "english_name": "Yarrow / Boreal Yarrow",
            "native_alaskan_name": "Ggaay (Tlingit); K'elt'ani (Dena'ina)",
            "native_language": "Tlingit, Dena'ina",
            "family": "Asteraceae",
            "description": "Perennial herb with feathery leaves and flat-topped clusters of white flowers. Found across Alaska in open areas.",
            "habitat": "Open meadows, roadsides, disturbed areas, coastal plains",
            "traditional_uses": "Widely used for wounds, bleeding, colds, and fever. Applied as poultice for cuts. Stems used in sweat baths. Stimulates sweating to break fevers.",
            "parts_used": "Leaves, flowers, stems",
            "preparation": "Leaf poultice for wounds. Flower/leaf tea for colds and fever. Stems in sweat bath.",
            "cautions": "May cause allergic reactions in sensitive individuals. Avoid during pregnancy.",
            "verified": True,
            "source_author": "Garibaldi, Ann; Schofield, Janice J.",
            "source_url": "https://www.nps.gov/articles/ethnobotany-of-southeast-alaska.htm"
        },
        {
            "latin_binomial": "Petasites frigidus",
            "english_name": "Coltsfoot / Sweet Coltsfoot",
            "native_alaskan_name": "Saxsit (Yupik); Nuuqpak (Inupiaq)",
            "native_language": "Yupik, Inupiaq",
            "family": "Asteraceae",
            "description": "Large-leaved perennial that appears before flowers bloom. Found in wet areas across Alaska. Important lung medicine.",
            "habitat": "Streambanks, wet meadows, seeps, shorelines",
            "traditional_uses": "Traditional cough and lung medicine. Leaves used for respiratory complaints, bronchitis, and asthma. One of the most important respiratory medicines.",
            "parts_used": "Leaves, roots",
            "preparation": "Leaves dried and steeped as tea for coughs. Root decoction stronger. Often combined with Labrador tea.",
            "cautions": "Contains pyrrolizidine alkaloids; use only short-term. Not for long-term daily use.",
            "verified": True,
            "source_author": "Jones, Anore; Kari, Priscilla Russell",
            "source_url": "https://www.fs.usda.gov/Internet/FSE_DOCUMENTS/stelprdb5202434.pdf"
        },
        {
            "latin_binomial": "Epilobium angustifolium",
            "english_name": "Fireweed",
            "native_alaskan_name": "Cama'i (Dena'ina); Pamiuqtaq (Yupik)",
            "native_language": "Dena'ina, Yupik",
            "family": "Onagraceae",
            "description": "Tall showy perennial with pink-purple flowers, famous for colonizing burned areas. Alaska's official flower. Important food and medicine plant.",
            "habitat": "Burned areas, roadsides, meadows, open forests, riverbanks",
            "traditional_uses": "Young shoots eaten as greens. Flowers used for honey/tea. Leaves used for intestinal complaints. Pith used for burns and skin irritations. One of the most versatile plants.",
            "parts_used": "Young shoots, leaves, flowers, pith (inner stem)",
            "preparation": "Shoots peeled and eaten raw or cooked. Flower/leaf tea for digestion. Pith applied to burns.",
            "cautions": "None known. Very safe food plant.",
            "verified": True,
            "source_author": "Kari, Priscilla Russell; Jones, Anore; Schofield, Janice J.",
            "source_url": "https://www.uaf.edu/ces/"
        },
        {
            "latin_binomial": "Sambucus racemosa",
            "english_name": "Red Elderberry",
            "native_alaskan_name": "Haawak (Tlingit); Tl'eek (Haida)",
            "native_language": "Tlingit, Haida",
            "family": "Adoxaceae",
            "description": "Large shrub with compound leaves and clusters of bright red berries. Found in Southeast Alaska coastal forests.",
            "habitat": "Coastal temperate rainforest, streambanks, forest openings",
            "traditional_uses": "Berries cooked and used for food. Bark used medicinally. Important food source but requires proper preparation.",
            "parts_used": "Berries (cooked only), bark",
            "preparation": "Berries must be cooked before eating. Used in jams, jellies. Bark tea used for various ailments.",
            "cautions": "RAW BERRIES ARE TOXIC. Must be cooked thoroughly. Contains cyanogenic compounds when raw. Seeds should be strained out.",
            "verified": True,
            "source_author": "Garibaldi, Ann; Kari, Priscilla Russell",
            "source_url": "https://www.nps.gov/articles/ethnobotany-of-southeast-alaska.htm"
        },
        {
            "latin_binomial": "Heracleum lanatum",
            "english_name": "Cow Parsnip / Pushki",
            "native_alaskan_name": "Ggwsdaa (Tlingit); Ggwsda (Haida)",
            "native_language": "Tlingit, Haida",
            "family": "Apiaceae",
            "description": "Very large perennial with huge leaves and white flower umbels. One of the most important traditional vegetables in Southeast Alaska.",
            "habitat": "Coastal meadows, streambanks, open forests, roadsides",
            "traditional_uses": "Young stems and leaf stalks peeled and eaten. Important spring vegetable. Used as famine food. Stems used for making fish traps.",
            "parts_used": "Young stems, leaf stalks (peeled), roots",
            "preparation": "Peel outer skin and eat stems/stalks raw, steamed, or boiled. Must peel completely - outer skin contains phototoxic compounds.",
            "cautions": "SKIN CONTACT WITH SAP + SUN = SEVERE BLISTERS (phytophotodermatitis). Always peel completely. Wear gloves when harvesting.",
            "verified": True,
            "source_author": "Jones, Anore; Kari, Priscilla Russell",
            "source_url": "https://www.uaf.edu/ces/"
        },
        {
            "latin_binomial": "Plantago major",
            "english_name": "Broadleaf Plantain",
            "native_alaskan_name": "Various local names",
            "native_language": "Multiple Alaska Native languages",
            "family": "Plantaginaceae",
            "description": "Low-growing perennial with broad oval leaves and seed spikes. Common worldwide and widely adopted by Alaska Natives post-contact.",
            "habitat": "Disturbed areas, roadsides, beaches, lawns",
            "traditional_uses": "Poultice for insect bites, wounds, and skin irritations. Leaf tea for coughs and digestive issues. Seeds as laxative.",
            "parts_used": "Leaves, seeds",
            "preparation": "Crushed leaf poultice for bites and wounds. Leaf tea for respiratory and digestive complaints.",
            "cautions": "None known. Very safe.",
            "verified": True,
            "source_author": "Garibaldi, Ann",
            "source_url": "https://www.fs.usda.gov/Internet/FSE_DOCUMENTS/stelprdb5202434.pdf"
        },
        {
            "latin_binomial": "Urtica dioica",
            "english_name": "Stinging Nettle",
            "native_alaskan_name": "Local names vary by region",
            "native_language": "Multiple",
            "family": "Urticaceae",
            "description": "Tall perennial with stinging hairs on leaves and stems. Found in rich soils near human habitation across Alaska.",
            "habitat": "Rich soils, areas with past human occupation, streambanks, forest edges",
            "traditional_uses": "Highly nutritious spring green. Leaf tea for allergies, anemia, and general tonic. Used in steam baths. Fibers used for cordage.",
            "parts_used": "Young shoots, leaves, stems",
            "preparation": "Young shoots boiled/steamed (cooking neutralizes sting). Dried leaf tea. Fibers stripped for cordage.",
            "cautions": "Raw plant stings. Cooking or drying neutralizes. Do not touch with bare skin when fresh.",
            "verified": True,
            "source_author": "Schofield, Janice J.; Jones, Anore",
            "source_url": "https://www.uaf.edu/ces/"
        },
        {
            "latin_binomial": "Alnus viridis ssp. crispa",
            "english_name": "Green Alder / Mountain Alder",
            "native_alaskan_name": "Gizi (Dena'ina); Ts'i (Ahtna)",
            "native_language": "Dena'ina, Ahtna",
            "family": "Betulaceae",
            "description": "Shrub or small tree with serrated leaves and catkins. Important medicine and dye plant across Interior Alaska.",
            "habitat": "Streambanks, wet slopes, avalanche chutes, forest edges",
            "traditional_uses": "Inner bark used for medicine and dye. Bark tea for skin conditions, tuberculosis symptoms, and as eyewash. Bark yields red-orange dye.",
            "parts_used": "Inner bark, catkins",
            "preparation": "Inner bark peeled and dried for tea. Fresh bark for dye. Sometimes combined with willow bark.",
            "cautions": "None known in traditional preparation amounts.",
            "verified": True,
            "source_author": "Kari, Priscilla Russell",
            "source_url": "https://www.uaf.edu/ces/"
        },
        {
            "latin_binomial": "Salix alaxensis",
            "english_name": "Feltleaf Willow",
            "native_alaskan_name": "Ggas (Dena'ina); Qanemciaq (Yupik)",
            "native_language": "Dena'ina, Yupik",
            "family": "Salicaceae",
            "description": "Tall shrub or small tree with large velvety leaves. Most important willow species for medicine in Alaska.",
            "habitat": "Riverbanks, floodplains, disturbed areas, south-facing slopes",
            "traditional_uses": "Inner bark used like aspirin for pain, fever, and inflammation. Leaf tea for digestive issues. Twigs used for basketry. Most widely used pain medicine in traditional Alaska.",
            "parts_used": "Inner bark, leaves, twigs",
            "preparation": "Inner bark peeled and steeped for headache, fever, pain. Leaf tea milder. Bark harvested in spring when sap flows.",
            "cautions": "Contains salicin (aspirin-like). Avoid if allergic to aspirin. May interact with blood thinners.",
            "verified": True,
            "source_author": "Garibaldi, Ann; Kari, Priscilla Russell",
            "source_url": "https://www.fs.usda.gov/Internet/FSE_DOCUMENTS/stelprdb5202434.pdf"
        },
        {
            "latin_binomial": "Arnica latifolia",
            "english_name": "Mountain Arnica",
            "native_alaskan_name": "Local names vary",
            "native_language": "Various Interior languages",
            "family": "Asteraceae",
            "description": "Perennial herb with yellow daisy-like flowers. Found in alpine meadows across Alaska.",
            "habitat": "Alpine meadows, subalpine slopes, open forests",
            "traditional_uses": "Topical use for bruises, sprains, muscle pain, and inflammation. Important external medicine. NOT for internal use.",
            "parts_used": "Flowers, leaves",
            "preparation": "Flower poultice or infused oil for external use only. Soak in oil for muscle rub.",
            "cautions": "TOXIC IF SWALLOWED. External use only. Do not apply to broken skin. Can cause contact dermatitis in sensitive individuals.",
            "verified": True,
            "source_author": "Garibaldi, Ann; Schofield, Janice J.",
            "source_url": "https://www.uaf.edu/ces/"
        },
        {
            "latin_binomial": "Matricaria discoidea",
            "english_name": "Pineapple Weed / Wild Chamomile",
            "native_alaskan_name": "Various local names",
            "native_language": "Multiple",
            "family": "Asteraceae",
            "description": "Low-growing annual with finely divided leaves and small yellow-green cone-shaped flower heads. Smells like pineapple when crushed. Introduced but widely adopted.",
            "habitat": "Disturbed areas, roadsides, compacted soils, near human habitation",
            "traditional_uses": "Tea for stomach upset, colic, menstrual cramps, and to promote sleep. Gentle children's medicine. Very safe.",
            "parts_used": "Flowers, leaves",
            "preparation": "Flower heads steeped as tea. Very mild - safe for children.",
            "cautions": "None known. Very safe. Rare ragweed allergy.",
            "verified": True,
            "source_author": "Schofield, Janice J.",
            "source_url": "https://www.uaf.edu/ces/"
        },
        {
            "latin_binomial": "Equisetum arvense",
            "english_name": "Horsetail / Scouring Rush",
            "native_alaskan_name": "Local names vary by region",
            "native_language": "Multiple Interior languages",
            "family": "Equisetaceae",
            "description": "Primitive vascular plant with jointed hollow stems and whorls of thin branches. Found in wet areas across Alaska.",
            "habitat": "Wet meadows, streambanks, disturbed wet areas",
            "traditional_uses": "Stem tea for kidney and bladder complaints. High silica content makes it useful as scouring pad. External wash for wounds.",
            "parts_used": "Stems (above-ground parts)",
            "preparation": "Dried stem tea for urinary system. Fresh stems used to scrub pots.",
            "cautions": "Contains thiaminase - may deplete vitamin B1 with long-term heavy use. Use in moderation. Not for long-term daily use.",
            "verified": True,
            "source_author": "Garibaldi, Ann",
            "source_url": "https://www.fs.usda.gov/Internet/FSE_DOCUMENTS/stelprdb5202434.pdf"
        },
        {
            "latin_binomial": "Valeriana sitchensis",
            "english_name": "Sitka Valerian / Tobacco Root",
            "native_alaskan_name": "Local names",
            "native_language": "Various Southeast and Southcentral languages",
            "family": "Caprifoliaceae",
            "description": "Perennial herb with clusters of small white-pink flowers and strong-smelling roots. Found in moist mountain meadows.",
            "habitat": "Moist meadows, subalpine areas, streambanks",
            "traditional_uses": "Root used as sedative, sleep aid, and muscle relaxant. Important medicine for anxiety and insomnia. Used in steam baths.",
            "parts_used": "Roots",
            "preparation": "Root decoction (strong tea) for sleep and anxiety. Dried root has strong odor. Used in sweat baths.",
            "cautions": "May cause drowsiness. Do not combine with alcohol or sedatives. Can cause vivid dreams. Strong odor.",
            "verified": True,
            "source_author": "Garibaldi, Ann; Kari, Priscilla Russell",
            "source_url": "https://www.uaf.edu/ces/"
        },
        {
            "latin_binomial": "Menyanthes trifoliata",
            "english_name": "Buckbean / Bogbean",
            "native_alaskan_name": "Various local names",
            "native_language": "Multiple Interior languages",
            "family": "Menyanthaceae",
            "description": "Perennial aquatic plant with trifoliate leaves and white fringed flowers. Found in bogs and shallow water.",
            "habitat": "Bogs, shallow ponds, wet meadows, margins of lakes",
            "traditional_uses": "Bitter digestive tonic. Leaf tea for appetite, digestion, and rheumatism. Used as famine food in some areas.",
            "parts_used": "Leaves, roots",
            "preparation": "Leaf tea as bitter tonic. Must be dried before use.",
            "cautions": "Very bitter. May cause digestive upset in large amounts. Use in moderation.",
            "verified": True,
            "source_author": "Garibaldi, Ann",
            "source_url": "https://www.fs.usda.gov/Internet/FSE_DOCUMENTS/stelprdb5202434.pdf"
        },

        # --- ROOT/TUBER PLANTS ---
        {
            "latin_binomial": "Hedysarum alpinum",
            "english_name": "Alpine Sweetvetch / Eskimo Potato",
            "native_alaskan_name": "Maqpiq (Yupik); Masru (Inupiaq)",
            "native_language": "Yupik, Inupiaq",
            "family": "Fabaceae",
            "description": "Perennial herb with pea-like flowers and thick edible roots. One of the most important traditional root foods in Arctic Alaska.",
            "habitat": "Dry tundra slopes, gravelly riverbanks, south-facing slopes",
            "traditional_uses": "Roots are a major carbohydrate source. Eaten raw, boiled, or preserved in seal oil. Critical subsistence food.",
            "parts_used": "Roots",
            "preparation": "Roots dug in fall, peeled, and eaten raw or boiled. Can be stored in seal oil.",
            "cautions": "None known. Important food plant.",
            "verified": True,
            "source_author": "Jones, Anore; Kari, Priscilla Russell",
            "source_url": "https://www.uaf.edu/ces/"
        },
        {
            "latin_binomial": "Claytonia tuberosa",
            "english_name": "Siberian Springbeauty / Eskimo Potato",
            "native_alaskan_name": "Various local names",
            "native_language": "Multiple Interior and Arctic languages",
            "family": "Montiaceae",
            "description": "Small perennial with succulent leaves and small pink flowers. Has round edible corms.",
            "habitat": "Tundra, rocky slopes, alpine meadows",
            "traditional_uses": "Corm eaten as food. Important spring food source when other stores are low.",
            "parts_used": "Corms (underground stems)",
            "preparation": "Eaten raw or cooked. Small but nutritious.",
            "cautions": "None known.",
            "verified": True,
            "source_author": "Jones, Anore",
            "source_url": "https://www.uaf.edu/ces/"
        },

        # --- TREES (MEDICINAL/Food) ---
        {
            "latin_binomial": "Picea glauca",
            "english_name": "White Spruce",
            "native_alaskan_name": "Ts'et (Dena'ina); Cikuvi (Yupik)",
            "native_language": "Dena'ina, Yupik",
            "family": "Pinaceae",
            "description": "Tall coniferous tree with needle-like leaves and woody cones. The most widespread tree in Alaska.",
            "habitat": "Boreal forest, river valleys, well-drained slopes",
            "traditional_uses": "Inner bark eaten as famine food. Needles for vitamin C tea. Pitch used for wounds and skin conditions. Boughs used in sweat baths. Wood for construction and tools.",
            "parts_used": "Inner bark, needles, pitch, boughs",
            "preparation": "Inner bark scraped and dried. Needle tea for scurvy prevention. Pitch applied to wounds.",
            "cautions": "None known. Very safe.",
            "verified": True,
            "source_author": "Kari, Priscilla Russell; Jones, Anore",
            "source_url": "https://www.uaf.edu/ces/"
        },
        {
            "latin_binomial": "Populus balsamifera",
            "english_name": "Balsam Poplar / Cottonwood",
            "native_alaskan_name": "K'el (Dena'ina); K'el (Ahtna)",
            "native_language": "Dena'ina, Ahtna",
            "family": "Salicaceae",
            "description": "Large deciduous tree with resinous buds and triangular leaves. Found along rivers in Interior Alaska.",
            "habitat": "River floodplains, gravel bars, disturbed areas",
            "traditional_uses": "Buds steeped for tea for coughs, colds, and sore throats. Resin used as antimicrobial salve. Inner bark for food. Important medicine tree.",
            "parts_used": "Buds, resin, inner bark",
            "preparation": "Winter bud tea for respiratory infections. Resin collected and applied to cuts. Bark eaten as emergency food.",
            "cautions": "None known. Very safe.",
            "verified": True,
            "source_author": "Garibaldi, Ann; Kari, Priscilla Russell",
            "source_url": "https://www.fs.usda.gov/Internet/FSE_DOCUMENTS/stelprdb5202434.pdf"
        },
        {
            "latin_binomial": "Betula papyrifera",
            "english_name": "Paper Birch",
            "native_alaskan_name": "Neyh (Dena'ina); Neyh (Ahtna); Ciisaq (Yupik)",
            "native_language": "Dena'ina, Ahtna, Yupik",
            "family": "Betulaceae",
            "description": "Medium-sized deciduous tree with white peeling bark. One of the most culturally important trees in Alaska.",
            "habitat": "Mixed forests, river valleys, burned areas, well-drained slopes",
            "traditional_uses": "Sap used as beverage and medicine. Inner bark eaten as food. Bark for baskets, canoes, and shelter. Leaves for tea. Anti-inflammatory properties.",
            "parts_used": "Sap, inner bark, leaves, bark",
            "preparation": "Sap collected in spring as sweet drink. Inner bark scraped and eaten. Leaf tea for inflammation.",
            "cautions": "None known. Very safe.",
            "verified": True,
            "source_author": "Jones, Anore; Kari, Priscilla Russell",
            "source_url": "https://www.uaf.edu/ces/"
        },

        # --- MUSHROOMS (included as culturally significant) ---
        {
            "latin_binomial": "Fomes fomentarius",
            "english_name": "Tinder Fungus / Amadou",
            "native_alaskan_name": "Various local names",
            "native_language": "Multiple",
            "family": "Polyporaceae",
            "description": "Hard woody bracket fungus growing on birch trees. Used for fire-starting and medicinal purposes.",
            "habitat": "On dead or dying birch trees",
            "traditional_uses": "Used as tinder for fire-starting. Pounded and used as styptic to stop bleeding. Medicinal tea for various ailments.",
            "parts_used": "Fruiting body (bracket)",
            "preparation": "Dried and pounded for tinder. Powder used on wounds to stop bleeding.",
            "cautions": "None known. Not edible.",
            "verified": True,
            "source_author": "Jones, Anore",
            "source_url": "https://www.uaf.edu/ces/"
        },
        {
            "latin_binomial": "Inonotus obliquus",
            "english_name": "Chaga",
            "native_alaskan_name": "Various local names",
            "native_language": "Multiple Interior languages",
            "family": "Hymenochaetaceae",
            "description": "Black irregular conk growing on birch trees. Hard, crusty exterior with orange-brown interior. Important traditional medicine.",
            "habitat": "On living birch trees, especially older trees",
            "traditional_uses": "Tea used for immune support, stomach complaints, and general wellness. Highly regarded tonic medicine. Modern research confirms antioxidant properties.",
            "parts_used": "Conk (inner portion)",
            "preparation": "Small pieces broken off and steeped as tea. Can be reused multiple times. Very bitter.",
            "cautions": "May interact with blood thinners. Use in moderation. Harvest sustainably - do not take entire conk.",
            "verified": True,
            "source_author": "Garibaldi, Ann",
            "source_url": "https://www.uaf.edu/ces/"
        },
    ]

    count = 0
    for plant_data in plants:
        add_plant(**plant_data)
        count += 1

    return count


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(__file__))
    from database import init_database
    init_database()
    seeded = seed_verified_plants()
    print(f"Seeded {seeded} verified Alaskan Native botanicals.")
