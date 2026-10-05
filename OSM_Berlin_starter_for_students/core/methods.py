import os
import json

import numpy                         as np
import pandas                        as pd
import geopandas                     as gpd
import folium
from folium.plugins                  import HeatMap, MarkerCluster
from branca.colormap                 import LinearColormap
import streamlit                     as st
from streamlit_folium                import st_folium

import core.HelperTools              as ht
import core.chat                     as chat
from config                          import pdict as CFG      # only for CRS and thresholds


# =============================================================================
# 1) Loading
# =============================================================================
@st.cache_data
def load_areas(file, key):
    """Polygons (PLZ or Bezirk) from WKT csv -> GeoDataFrame (one row per area, EPSG:4326)"""
    # TODO: read "datasets/" + file (sep=";"), geometry via gpd.GeoSeries.from_wkt, set the CRS,
    #       keep only column <key> + geometry, make sure every area appears only once (dissolve)
    raise NotImplementedError


@st.cache_data
def load_osm_points(file):
    """OSM csv (written by download_osm.py) -> GeoDataFrame of Points (EPSG:4326)"""
    # TODO: read the csv (sep=";", keep "addr:postcode" as string), drop rows without lat / lon,
    #       geometry = gpd.points_from_xy(lon, lat)   <- order: x = longitude, y = latitude!
    raise NotImplementedError


@ht.timer
def preprop_resid(dfr):
    """Preprocessing plz_einwohner.csv: only PLZ and residents, only Berlin range"""
    d = dfr.loc[:, ["plz", "einwohner"]].rename(columns={"plz": "PLZ", "einwohner": "Einwohner"})
    return d[(d["PLZ"] > 10000) & (d["PLZ"] < 14200)].reset_index(drop=True)


# =============================================================================
# 2) Spatial join and category filter
# =============================================================================
def assign_area(gdf_points, gdf_areas, key):
    """Spatial join: adds column <key> (PLZ / Bezirk) to every point. NaN = outside of all areas.
    Points exactly on a border can match twice -> only the first match is kept."""
    # TODO: gpd.sjoin(..., how="left", predicate="within"), remove duplicated index entries,
    #       drop the helper column "index_right"
    raise NotImplementedError


def _split_values(series):
    """'italian;pizza' -> ['italian', 'pizza'] (empty list if missing)"""
    return series.fillna("").astype(str).str.split(";").apply(lambda v: [x.strip() for x in v if x.strip()])


def category_options(gdf, col, n=10):
    """The n most frequent values of a (multi-valued) attribute, for the dependent menu"""
    # TODO: use _split_values, explode, value_counts. Return [] if the column does not exist.
    raise NotImplementedError


def filter_category(gdf, col, category):
    """Keeps objects that have <category> among their values (cuisine=italian;pizza counts for both)"""
    # TODO: "All" -> return gdf unchanged
    raise NotImplementedError


# =============================================================================
# 3) Indicators
# =============================================================================
def residents_by_area(df_res, gdf_plz, gdf_dis, key):
    """Residents per PLZ or per Bezirk (columns <key>, Einwohner)."""
    # TODO: key == "PLZ": merge the PLZ polygons with df_res.
    #       key == "Bezirk": assign every PLZ (by its centre, computed in CFG["crs_metric"]) to a Bezirk
    #       (gpd.sjoin_nearest) and sum the residents per Bezirk. Write down this approximation!
    raise NotImplementedError


def aggregate(gdf_points, gdf_areas, key, indicator, residents):
    """One row per area (also areas without objects = 0) with columns count, area_km2, Einwohner, value"""
    # TODO: count points per area; start from the POLYGONS (left merge) so that empty areas get 0
    #       area_km2: area in CFG["crs_metric"] / 1e6
    #       value   : "Number" | "Number per km2" | "Number per 10,000 residents"
    #                 (no value, NaN, if Einwohner < CFG["min_residents"])
    raise NotImplementedError


# =============================================================================
# 4) Data quality
# =============================================================================
def quality_report(gdf_points, gdf_areas, subcat=None):
    """Automatic checks of one OSM file. Expects column 'PLZ' (from assign_area). Returns DataFrame."""
    # TODO (see Task 5): number of objects, share without name, share without <subcat>,
    #      near-duplicates (same name, closer than CFG["dup_distance_m"] metres - compute in CFG["crs_metric"]),
    #      points outside Berlin (PLZ is NaN), implausible coordinates (CFG["berlin_lat"], CFG["berlin_lon"]),
    #      share of objects with addr:postcode and how often it equals the PLZ of the spatial join,
    #      number of PLZ areas without any object.
    #      Return a DataFrame with the columns "Check" and "Result".
    raise NotImplementedError


# =============================================================================
# 5) Map
# =============================================================================
def make_map(gdf_points, gdf_agg, maptype, key="PLZ", colors=("yellow", "red"), caption="Value"):
    """Folium map: choropleth (areas), heatmap or marker clusters (single points)"""
    m = folium.Map(location=[52.52, 13.40], zoom_start=10, tiles="OpenStreetMap")

    if maptype == "Choropleth":
        # TODO: LinearColormap(colors, vmin, vmax) from the column "value"; areas with value NaN -> grey.
        #       ONE folium.GeoJson layer (gdf_agg.to_json()) with style_function and tooltip. Add the legend.
        pass
    elif maptype == "Heatmap":
        # TODO: HeatMap([[lat, lon], ...])        <- Folium wants [lat, lon]
        pass
    else:   # Point map (clusters)
        # TODO: MarkerCluster with one marker per point, name as tooltip
        pass
    return m


# =============================================================================
# 6) Streamlit app
# =============================================================================
@st.cache_data(show_spinner="Loading data and assigning areas ...")
def prepare_source(label, pdict):
    """Loads one OSM source, assigns PLZ and Bezirk (spatial join) and runs the quality check"""
    cfg = pdict["sources"][label]
    plz = load_areas(pdict["file_plz"], "PLZ")
    dis = load_areas(pdict["file_dis"], "Bezirk")
    pts = load_osm_points(cfg["file"])
    pts = assign_area(pts, plz, "PLZ")
    pts = assign_area(pts, dis, "Bezirk")
    return pts, plz, dis, quality_report(pts, plz, cfg["subcat"])


def _download_date(pdict, label):
    path = "datasets/" + pdict["file_info"]
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f).get(label, "unknown")
    return "unknown"


@ht.timer
def make_streamlit_app(pdict, df_residents):
    """Makes Streamlit App: OSM data of Berlin, controlled by pull-down menus"""
    st.set_page_config(page_title="OpenStreetMap Berlin", layout="wide")
    st.title("OpenStreetMap Berlin: Places and Supply")

    # ---- Menu 1: data source ------------------------------------------------
    src = st.sidebar.selectbox("Data source", list(pdict["sources"].keys()))
    cfg = pdict["sources"][src]
    if not os.path.exists("datasets/" + cfg["file"]):
        st.error("File datasets/" + cfg["file"] + " not found. Run:  python download_osm.py \"" + src + "\"")
        return
    pts, plz, dis, quality = prepare_source(src, pdict)

    # ---- Menu 2: category filter (depends on menu 1) ------------------------
    # TODO: options = ["All"] + category_options(...); use key="cat_" + src so the menu resets with the source
    cat = "All"

    # ---- Menus 3-5 ----------------------------------------------------------
    area_label = st.sidebar.selectbox("Area unit", list(pdict["areas"].keys()))
    ind        = st.sidebar.selectbox("Indicator", pdict["indicators"])
    mtype      = st.sidebar.selectbox("Map type", pdict["maptypes"])
    # optional menu 6: colour scale (only for the choropleth)

    # TODO: key (PLZ / Bezirk) and the matching polygons, filter by category, stop with st.warning if empty,
    #       residents_by_area, aggregate

    # TODO: key figures with st.metric: objects shown, areas without any object, area with the highest value
    # TODO: map with st_folium(m, width=1000, height=600, returned_objects=[])
    # TODO: st.caption with "© OpenStreetMap contributors" and _download_date(pdict, src)
    # TODO: expander "Top 3 areas and data table" with st.dataframe and st.download_button (CSV)
    # TODO: expander "Data quality" showing the quality DataFrame

    # ---- Chat assistant (LLM) - provided, see core/chat.py -------------------
    # Needs the variables src, cat, area_label, ind, mtype, key, pts_f, agg, quality from your code above.
    ctx = chat.build_context(src, cat, area_label, ind, mtype, key, pts_f, agg, quality)
    chat.render_chat(ctx, pdict)
