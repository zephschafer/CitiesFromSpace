def slice_files(state, state_abbv, data_folder, slice_length):
    import os, os.path
    from io import BytesIO
    from zipfile import ZipFile
    from urllib2 import urlopen
    # Set State
    # filepath = data_folder + 'states_full/' + state + '.geojson'
    url = urlopen("https://usbuildingdata.blob.core.windows.net/usbuildings-v1-1/" + str(state) + ".zip")
    my_zip_file = ZipFile(BytesIO(url.read()))
    contained_file = my_zip_file.namelist()
    raw_file = my_zip_file.open(contained_file[0])
    chkpt = '___1___' + state

    # Create output path
    state_slice_folder = data_folder + 'states_slices/'\
                        + state_abbv + '/'
    try:
        os.mkdir(state_slice_folder)
    except:
        print "Slice folder already exists. Will overwrite existing slices."
    chkpt = '___2___' + state

    # Count Total Lines in File (Represents no. of buildings)
    lines = 0.0
    # raw_file.seek(0)
    raw_file = my_zip_file.open(contained_file[0])
    for line in raw_file:
        lines += 1
    print 'The ' + "{:,}".format(int(lines-6)) + ' buildings from '\
            + state_abbv + ' will go into ' \
            + str(int((lines-6) / slice_length) + 1) \
            + ' slice files'
    chkpt = '___3___' + state

    # Define GeoJSON Open and Close contents
    # raw_file.seek(0)
    raw_file = my_zip_file.open(contained_file[0])
    list_start = []
    for line in raw_file.readlines()[0:4]:
        list_start.append(line)
    # raw_file.seek(0)
    raw_file = my_zip_file.open(contained_file[0])
    list_end = []
    for line in raw_file.readlines()[-2:]:
        list_end.append(line)
    chkpt = '___4___' + state

    # Read and Export Building Data
    # raw_file.seek(0)
    raw_file = my_zip_file.open(contained_file[0])
    i = 4
    start = 4
    end = int(lines-2)
    export_n = 1
    buildings = []
    for line in raw_file.readlines()[start:end]: # First 4 lines are filetyp & last 2 lines are closing brackts
        buildings.append(line)
        i += 1
        if (i % slice_length == 0) or (i == end-1):
            export_name = str(state_abbv + '_' + str(export_n))
            with open(state_slice_folder + export_name\
                      , 'w') as file:
                for item in list_start:
                    file.write("%s\n" % item)
                for item in buildings:
                    file.write("%s\n" % item)
                for item in list_end:
                    file.write("%s\n" % item)
            export_n += 1
            buildings = []





# -------------------PandasDF_to_GeoJSON-------------------
# Define Function to Save Coordinates as GeoJSON
# Adapted from source below
# Source: <https://github.com/gboeing/urban-data-science/blob/3faf7e028d48cb03ddb999c5a910213c5384e7dc/17-Leaflet-Web-Mapping/leaflet-simple-demo/pandas-to-geojson.ipynb>

def df_to_geojson(df, properties, lat='latitude', lon='longitude'):
    # Create python dict to hold our data in GeoJSON format
    geojson = {'type':'FeatureCollection', 'features':[]}
    # Make each row of the df a feature in geojson
    for _, row in tqdm(df.iterrows()):
        # create a feature template to fill in
        feature = {'type':'Feature',
                   'properties':{},
                   'geometry':{'type':'Point',
                               'coordinates':[]}}
        # Fill in the Coordinates
        feature['geometry']['coordinates'] = [row[lon],row[lat]]
        # Fill in the Properties
        for prop in properties:
            feature['properties'][prop] = row[prop]
        # Add the Feature to the Dict
        geojson['features'].append(feature)
    return geojson


# Example Usage:
# # Choose Any Row-Level Features we want Retained (For now, none)
# useful_columns = []
# # Define Dict Version for Reference
# geojson_dict = df_to_geojson(df, properties=useful_columns)
# # Define Str Version for Export
# geojson_str = json.dumps(geojson_dict, indent=2)
# # Save the GeoJSON Result to a File
# output_filename = data_folder + 'states_coordinates/' + state + '.geojson'
# with open(output_filename, 'w') as output_file:
#     output_file.write(geojson_str)
# # Count Obs
# print('Observations: ' + str(len(geojson_dict['features'])))
