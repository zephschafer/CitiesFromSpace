import os
import shutil
import rasterio
from tqdm import tqdm_notebook as tqdm
import matplotlib.cm as cm
import random
import pandas as pd
import numpy as np
import seaborn as sns; sns.set()
import matplotlib.pyplot as plt
import time
from mpl_toolkits.mplot3d import axes3d

graph_start = time.time()

# Set Main Directories
project_folder = '../'
data_folder = project_folder + '1_data/'

print "Loading buildings csv ..."
bldngs = pd.read_csv(data_folder + "bldngs.csv")
bldngs.drop(columns=['Unnamed: 0'], inplace=True)

# Regroup
grouper = float(raw_input('Set aggregation level e.g. 0.05: '))
print "Aggregating data ... "
for place in ['lat','long']:
    bldngs['group_' + str(place)] = bldngs[str(place) + 'itude']\
                            .apply(lambda x: round(x / grouper) * grouper)
bldngs['count'] = 1
bldngs_grps = bldngs.drop(columns=['latitude','longitude'])\
                          .groupby(['group_long', 'group_lat'])\
                            .sum()\
                            .sort_values(by='count', ascending=True)\
                            .reset_index()

print "Total Buildings: " + "{:,}".format(len(bldngs))
print "Total Groups: " + "{:,}".format(len(bldngs_grps))


df = bldngs_grps[:]
range_start = int(raw_input('Rotations Start Angle: '))
range_end = int(raw_input('Rotations End Angle: '))
range_interval = int(raw_input('Rotations Angle Increment: '))
catgs = eval(raw_input("""Categories as list e.g. ['pop', 'count']: """))
colors = eval(raw_input("""Colors as list e.g. ['plasma', 'Blues']: """))


for catg in catgs:
    if os.path.exists("../1_data/gifgraph/" + catg):
        shutil.rmtree("../1_data/gifgraph/" + catg)
    os.makedirs("../1_data/gifgraph/" + catg)
    for color in tqdm(colors):
        os.chdir("../1_data/gifgraph/")
        os.chdir(catg)
        print "__chkpt__" + catg + '_' + color
        for angle in tqdm(range(range_start, range_end, range_interval)):

            fig = plt.figure()
            ax1 = fig.add_subplot(111, projection='3d')

            x3 = df['group_long']
            y3 = df['group_lat']
            z3 = np.zeros(len(df['group_long']))

            dx = np.ones(len(df['group_long']))*grouper
            dy = np.ones(len(df['group_long']))*grouper
            dz = df[catg]

            cmap = cm.get_cmap(color)
            max_height = np.max(dz)
            min_height = np.min(dz)
            rgba = [cmap(((k-min_height)/max_height)**.25) for k in dz]


            angle = angle

            ax1.bar3d(x3, y3, z3, dx, dy, dz, color=rgba, zsort='average'\
                      , edgecolor = "none")

            ax1.set_xlabel('x axis')
            ax1.set_ylabel('y axis')
            ax1.set_zlabel('z axis')
            ax1.view_init(30, angle)


            filename = '3dgraph_' + str(angle) + '_' + str(color) + '_' + str(catg) + '.png'
            plt.savefig(filename, dpi=96)
            plt.gca()


            plt.clf()
            plt.cla()
            plt.close()
        files = " ".join(map(str,['3dgraph_' + str(angle) + '_' \
                                  + str(color) + '_' + str(catg) + '.png'\
                                  for angle in range(range_start, range_end, range_interval)]))
        os.system("convert -delay 20 " + str(files) + " 1_" + str(catg) + str(color) + ".gif")
        os.chdir("..")
        os.chdir("..")
        os.chdir("../2_code")

graph_stop = time.time()

print 'This script took ' \
        + str(int((graph_stop-graph_start)/60/60)) + ' Hours ' \
        + str(int((graph_stop-graph_start)/60)) + ' Minutes ' \
        + 'and ' + str(int(graph_stop-graph_start)%60) + ' Seconds'
