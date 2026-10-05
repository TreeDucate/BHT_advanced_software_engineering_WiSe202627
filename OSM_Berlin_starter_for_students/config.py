p = dict()

# -----------------------------------------------------------------------------
# Static datasets (folder "datasets/")
p["geocode"]        = "PLZ"
p["file_plz"]       = "geodata_berlin_plz.csv"
p["file_dis"]       = "geodata_berlin_dis.csv"
p["file_residents"] = "plz_einwohner.csv"
p["file_info"]      = "osm_download_info.json"     # written by download_osm.py

# -----------------------------------------------------------------------------
# OSM data sources. The pull-down menu "Data source" is generated from this dict.
#   tags   : OSM tags used for the download (key: value or key: list of values)
#   file   : csv file in "datasets/" written by download_osm.py
#   subcat : OSM tag used for the dependent pull-down menu "Category filter"
p["sources"] = {
    "Restaurants":       {"tags": {"amenity": "restaurant"},
                          "file": "osm_restaurants.csv",  "subcat": "cuisine"},
    "Cafes":             {"tags": {"amenity": "cafe"},
                          "file": "osm_cafes.csv",        "subcat": "cuisine"},
    "Fast food":         {"tags": {"amenity": "fast_food"},
                          "file": "osm_fast_food.csv",    "subcat": "cuisine"},
    "Pharmacies":        {"tags": {"amenity": "pharmacy"},
                          "file": "osm_pharmacies.csv",   "subcat": "brand"},
    "Supermarkets":      {"tags": {"shop": "supermarket"},
                          "file": "osm_supermarkets.csv", "subcat": "brand"},
    "Playgrounds":       {"tags": {"leisure": "playground"},
                          "file": "osm_playgrounds.csv",  "subcat": "access"},
    "Charging stations": {"tags": {"amenity": "charging_station"},
                          "file": "osm_charging.csv",     "subcat": "operator"},
    # TODO (team): add at least one source of your own choice (at least six sources in total)
}

# -----------------------------------------------------------------------------
# Options of the other pull-down menus
p["areas"]      = {"Postal code (PLZ)": "PLZ", "District (Bezirk)": "Bezirk"}
p["indicators"] = ["Number", "Number per km2", "Number per 10,000 residents"]
p["maptypes"]   = ["Choropleth", "Heatmap", "Point map (clusters)"]
p["colorscales"] = {"Yellow-Red": ["yellow", "red"],
                    "White-Blue": ["white", "darkblue"],
                    "Green-Purple": ["lightgreen", "purple"]}

# -----------------------------------------------------------------------------
# Parameters
p["min_residents"]  = 500       # PLZ areas with fewer residents: no per-resident value
p["top_n_category"] = 10        # number of entries in the category filter
p["dup_distance_m"] = 10        # near-duplicate threshold (quality check)
p["crs_geo"]        = "EPSG:4326"
p["crs_metric"]     = "EPSG:25833"   # ETRS89 / UTM 33N, metres (for area, distance)
p["berlin_lat"]     = (52.3, 52.7)   # plausibility box for coordinates
p["berlin_lon"]     = (13.0, 13.8)

# -----------------------------------------------------------------------------
# Chat assistant (LLM). Every provider with an OpenAI-compatible API works.
#   secret : name of the API key in .streamlit/secrets.toml or in an environment variable
# Model names change over time: they can also be edited in the sidebar of the app.
p["llm_providers"] = {
    "OpenAI":   {"base_url": "https://api.openai.com/v1",     "model": "gpt-4o-mini",
                 "secret": "OPENAI_API_KEY"},
    "DeepSeek": {"base_url": "https://api.deepseek.com",      "model": "deepseek-chat",
                 "secret": "DEEPSEEK_API_KEY"},
    "Mistral":  {"base_url": "https://api.mistral.ai/v1",     "model": "mistral-small-latest",
                 "secret": "MISTRAL_API_KEY"},
    "Anthropic (Claude)": {"base_url": "https://api.anthropic.com/v1/", "model": "claude-haiku-4-5-20251001",
                 "secret": "ANTHROPIC_API_KEY"},
    "Custom (OpenAI-compatible, e.g. local Ollama)": {
                 "base_url": "http://localhost:11434/v1",     "model": "llama3.1",
                 "secret": "LLM_API_KEY", "editable_url": True},
}
p["llm_default"]     = "OpenAI"
p["llm_max_history"] = 10      # last messages sent to the LLM
p["llm_max_tokens"]  = 800     # maximum length of an answer

# -----------------------------------------------------------------------------
pdict = p.copy()
