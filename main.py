import time
from PathletLearningClass import *
from PathletLearningScalableClass import *
import pandas as pd
from ast import literal_eval

start = time.time()
"""
#Thewroume oti Grid 4x4
trajectories=[]

trajectories.append([(0,0),(1,1),(1,2),(2,2)])
trajectories.append([(0,0),(1,1),(1,2),(0,2)])
trajectories.append([(0,0),(1,1),(1,2)])
#trajectories.append([(2,2)])
plclass = PathletLearningScalableClass(trajectories)
print(plclass.ReturnSpecificTrajectoryByIndex(2))
print(plclass.ReturnAllTrajsInAList())
"""
"""
plclass = PathletLearningClass(trajectories)
print(plclass.Pathlets)
print(plclass.TrajsResults)
print(plclass.ReturnSpecificTrajectoryByIndex(2))
print(plclass.ReturnAllTrajsInAList())
"""

trainSet = pd.read_csv(
        'train_set.csv', # replace with the correct path
        converters={"Trajectory": literal_eval},
        index_col='tripId')

trajectories = []
x = 0
for y in trainSet['Trajectory'] :
    traj = []
    [t,lon,lat] = y[0]
    traj.append((round(lon,4),round(lat,4)))

    for [t,lon,lat] in y :
        (prev_lon,prev_lat) = traj[-1]
        lon = round(lon,4)
        lat = round(lat,4)
        if prev_lon == lon and prev_lat == lat :
                continue
        traj.append((lon,lat))

    trajectories.append(traj)

    x = x + 1
    if x == 2 :
        break

print(trajectories)


plclass = PathletLearningClass(trajectories)

print(plclass.TrajsResults,"\n\n\n")


end = time.time()
print("\nRunTime:",(end - start))