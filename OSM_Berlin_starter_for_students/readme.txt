# -------------------------------
# Installation (Python 3.10+):
python -m venv .venv
.venv\Scripts\activate          (Windows)     source .venv/bin/activate   (Mac / Linux)
pip install -r requirements.txt

# -------------------------------
# Step 1: download the OSM data (Task 1), once per data source
python download_osm.py
python download_osm.py Restaurants        # only one source

# -------------------------------
# Step 2: start the Streamlit app
streamlit run main.py

# -------------------------------
# Files
config.py        data sources and options of the pull-down menus
download_osm.py  OSM download (Overpass via osmnx)
main.py          entry point of the app
core/methods.py  loading, spatial join, indicators, data quality, map, app
datasets/        PLZ and Bezirk polygons, residents, (downloaded) OSM csv files
