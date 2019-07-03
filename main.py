import time
from PathletLearningClass import *
from PathletLearningScalableClass import *
from PathletLearningScalableDynamicClass import *
import pandas as pd
from ast import literal_eval

start = time.time()

#Thewroume oti Grid 4x4
trajectories=[]

trajectories.append([(0,0),(1,1),(1,2),(2,2),(2,3)])
trajectories.append([(0,0),(1,1),(1,2),(2,2),(3,2)])
#trajectories.append([(0,0),(1,1),(0,1),(2,2)])
#trajectories.append([(1,1),(1,2),(0,2)])
#trajectories.append([(2,7),(2,8),(2,9)])
plclass = PathletLearningScalableDynamicClass(trajectories)
print("\n\n\n\n")
print(plclass.Pathlets,"   ",plclass.TrajsResults)
print("PrintingAllTrajectories\n",plclass.ReturnAllTrajsInAList())


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
    traj.append((round(lon,2),round(lat,2)))

    for [t,lon,lat] in y :
        (prv_lon,prv_lat) = traj[-1]
        lon = round(lon,2)
        lat = round(lat,2)
        if lon is not prv_lon and lat is not prv_lat :
                traj.append((lon,lat))

    trajectories.append(traj)

    x = x + 1
    if x == 1 :
        break

print(trajectories[0][0],trajectories[0][-1])
plclass = PathletLearningScalableDynamicClass(trajectories)

print("\n\n\n\n")
#print(plclass.Pathlets,"   ",plclass.TrajsResults)

print("PrintingTrajwithIndex2",plclass.ReturnSpecificTrajectoryByIndex(0)[0])

"""


end = time.time()
print("\nRunTime:",(end - start))