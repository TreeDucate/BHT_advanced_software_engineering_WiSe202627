import os
# works locally and on Streamlit Community Cloud (no absolute path needed)
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import pandas                        as pd
from core import methods             as m1
from core import HelperTools         as ht

from config                          import pdict

# -----------------------------------------------------------------------------
@ht.timer
def main():
    """Main: Generation of Streamlit App for visualizing OpenStreetMap data in Berlin"""

    # residents per PLZ; the OSM data is loaded inside the app, depending on the pull-down menus
    df_residents = #   TODO: read "datasets/" + pdict["file_residents"]  (sep=",", decimal=".")
    df_residents = #   TODO: m1.preprop_resid(...)

    m1.make_streamlit_app(pdict, df_residents)


if __name__ == "__main__":
    main()
