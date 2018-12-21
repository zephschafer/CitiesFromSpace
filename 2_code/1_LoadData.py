#!/usr/bin/env python
# coding: utf-8

# # Load, Shrink, Compile
#
# The GeoJSON source files are large and slow to open. To circumvent that delay, this notebook reads bits of them into slices and then recompiles the slices as CSVs where each polygon (formerly) becomes the coordinates of the polygon's centroid with an associated "area" value which represents the area of the polygon (i.e. the building footprint).
#
# The slicer function is "slice_files". It is defined in slicer.py, which is located in the same directory as this notebook.
#
# ### Steps:
# #### 1 - Import Modules and Data
# #### 2 - Slice the GeoJSONs
# #### 3 - Compile Slices as CSVs with centroids and area
# ####
#

# ### Import Modules, Set Paths, and Start the Clock

import datetime
from tqdm import tqdm_notebook as tqdm
from slicer import slice_files
import json
import os, os.path
import geopandas as gpd
import pandas as pd
import time

# Set Main Directories
project_folder = '../'
data_folder = project_folder + '1_data/'

# Start the clock
start_time = time.time()

# ### Slice Files
# states = [('Oregon','OR'), ('California', 'CA'),          ('Washington','WA')]
states = raw_input("""
        Input desired states as list of tuples, no spaces.
        e.g.: [('Oregon','OR'), ('California', 'CA'), ('Washington','WA')]
        or [('DistrictofColumbia','DC')]:

        """)
print states
# Set State
slice_length = 50000

# Get the data from Miscrosoft's GitHub and save in Slices
for state, state_abbv in tqdm(states):
    slice_files(state, state_abbv, data_folder, slice_length)


# ### Compile Slices info to CSVs
for state, state_abbv in states:
    state_slice_folder = data_folder + 'states_slices/'                        + state_abbv + '/'
    slices = os.listdir(state_slice_folder)
    i = 0
    print "Compiling " + state + ":"
    for file_name in tqdm(slices):
        # Read Slice
        file = gpd.read_file(state_slice_folder + file_name)
        # Get Area Meters^2 from Slice Using Cartesian(?) Projection <https://gis.stackexchange.com/questions/218450/getting-polygon-areas-using-geopandas>
        area_slice = file.to_crs({'init': 'epsg:3857'}).area
        area_slice = area_slice.apply(lambda footprint: round(footprint,4)).tolist()
        # Get Centroids from Slice
        centroids = file.geometry.centroid
        lat_slice = centroids.apply(lambda coordinate: round(coordinate.x,6)).tolist()
        lon_slice = centroids.apply(lambda coordinate: round(coordinate.y,6)).tolist()
        # On First Pass: Start List of Centroid
        if i == 0:
            lat = lat_slice
            lon = lon_slice
            area = area_slice
        # On Subsequent Passes: Append to List of Centroids
        else:
            for point in lat_slice:
                lat.append(point)
            for point in lon_slice:
                lon.append(point)
            for footprint in area_slice:
                area.append(round(footprint,4))
        i += 1
    # Given Centroids, Define Dataframe
    df = pd.DataFrame({'longitude':lat, 'latitude':lon, 'area':area})
    # Export Centroids in csv
    df.to_csv(data_folder + 'states_csv/' + state + '.csv')
    print 'Recorded: ' + str(df.columns.tolist()) + ' for '        + str(round(len(df)/1000000.0,2))         + ' Million Buildings from ' + state
    # Now remove df from mem. for next iteration
    del df


# Stop the clock
stop_time = time.time()
print 'This notebook took ' \
        + str(int((stop_time-start_time)/60/60)) + ' Hours ' \
        + str(int((stop_time-start_time)/60)) + ' Minutes ' \
        + 'and ' + str(int(stop_time-start_time)%60) + ' Seconds'
