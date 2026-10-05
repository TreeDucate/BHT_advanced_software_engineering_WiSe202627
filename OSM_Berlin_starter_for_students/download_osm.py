"""
Downloads one csv file per OSM data source defined in config.py (Task 1).

Usage:
    python download_osm.py                 # all sources
    python download_osm.py Restaurants     # only one source (menu label)

The app never calls the Overpass API itself: run this script once, commit the csv files.
"""
import os
import sys
import json
import datetime

import pandas as pd
import osmnx as ox

from config import pdict

# Columns that are kept (if they exist for the downloaded objects)
KEEP = ["name", "cuisine", "brand", "operator", "access", "opening_hours", "wheelchair", "addr:postcode"]


def download_source(label, cfg):
    """Downloads all OSM objects of one source and stores them as csv (one point per object)"""
    print("Downloading:", label, cfg["tags"])
    gdf = ox.features_from_place("Berlin, Germany", tags=cfg["tags"])

    # The index is (element type, id). Turn it into normal columns "osm_type" and "osm_id".
    # Hint: gdf.reset_index(); the column names differ between osmnx versions -> use gdf.columns[0], [1]
    # TODO

    # Nodes are points, ways / relations are polygons. We need ONE point per object:
    # centroid in a projected CRS (pdict["crs_metric"]), then back to lat / lon (pdict["crs_geo"]).
    # TODO: add columns "lat" and "lon"

    # Tags do not exist for every object. Add missing columns from KEEP and cfg["subcat"] (filled with
    # pd.NA), so that later code never fails on a missing column.
    # TODO

    # TODO: select osm_type, osm_id, name, lat, lon + the KEEP columns, remove duplicates,
    #       save to "datasets/" + cfg["file"]  (sep=";", index=False, encoding="utf-8")


def write_info(label):
    """Remember the download date per source (shown in the app)"""
    path = "datasets/" + pdict["file_info"]
    info = {}
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            info = json.load(f)
    info[label] = datetime.date.today().isoformat()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(info, f, indent=2)


if __name__ == "__main__":
    labels = sys.argv[1:] or list(pdict["sources"].keys())
    for label in labels:
        download_source(label, pdict["sources"][label])
        write_info(label)
