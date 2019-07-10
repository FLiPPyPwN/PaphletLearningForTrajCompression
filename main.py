import time
from PathletLearningClass import *
from PathletLearningScalableClass import *
from PathletLearningScalableDynamicClass import *
import pandas as pd
from ast import literal_eval

start = time.time()
"""
#Thewroume oti Grid 4x4
trajectories=[]

trajectories.append([0,1,2,3,4,5,6])
trajectories.append([0,1,2,3,4])
trajectories.append([3,4,5,6])

plclass = PathletLearningScalableDynamicClass(trajectories)
print("\n\n\n\n")
print(plclass.Pathlets,"   ",plclass.TrajsResults)
print("PrintingAllTrajectories\n",plclass.ReturnAllTrajsInAList())

"""

trainSet = pd.read_csv(
        'newTrips.csv', # replace with the correct path
        converters={"barefootSegmentsSequence": literal_eval},
        index_col='newTripID')

end = time.time()
print("\nRunTime to ReadCsvFile:",(end - start))

start = time.time()

trajectories = []
x = 0
for y in trainSet['barefootSegmentsSequence'] :
    trajectories.append(y)

    x = x + 1
    if x == 1000 :
        break

plclass = PathletLearningScalableDynamicClass(trajectories)

print("\n\n")


AllTrajs = plclass.ReturnAllTrajsInAList()

flag = False
for i in range(len(AllTrajs)) :
        if not(set(AllTrajs[i]) == set(trajectories[i])) :
                flag = True

if flag :
        print("trajectories not the same")



end = time.time()
print("\nRunTime:",(end - start))