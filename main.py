import time
from PathletLearningClass import *
from PathletLearningScalableClass import *
import pandas as pd
from ast import literal_eval

start = time.time()

#Thewroume oti Grid 4x4
trajectories=[]

trajectories.append([(0,0),(1,1),(1,2),(2,2)])
trajectories.append([(0,0),(1,1),(1,2),(0,2)])
trajectories.append([(0,0),(1,1),(1,2)])
#trajectories.append([(2,2)])
plclass = PathletLearningScalableClass(trajectories)

"""
plclass = PathletLearningClass(trajectories)
print(plclass.Pathlets)
print(plclass.TrajsResults)
print(plclass.ReturnSpecificTrajectoryByIndex(2))
print(plclass.ReturnAllTrajsInAList())
"""
"""
trainSet = pd.read_csv(
        'train_set.csv', # replace with the correct path
        converters={"Trajectory": literal_eval},
        index_col='tripId')

trajectories = []
x = 0
for y in trainSet['Trajectory'] :
    traj = []
    for [t,lon,lat] in y :
        traj.append((round(lon,4),round(lat,4)))

    trajectories.append(traj)

    x = x + 1
    if x == 2 :
        break


plclass = PathletLearningClass(trajectories)
print(trajectories)

print(plclass.ReturnSpecificTrajectoryByIndex(2),"\n\n\n")
print(plclass.ReturnAllTrajsInAList())
"""

end = time.time()
print("\nRunTime:",(end - start))