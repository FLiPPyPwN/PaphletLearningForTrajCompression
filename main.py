import time
from PathletLearningClass import *
from PathletLearningScalableClass import *
from PathletLearningScalableDynamicClass import *
import pandas as pd
from ast import literal_eval
import gc

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

trajectories = []
x = 0
for y in trainSet['barefootSegmentsSequence'] :
    trajectories.append(y)

    x = x + 1
    if x == 100 :
        break

del trainSet
gc.collect()

plclass = PathletLearningScalableDynamicClass(trajectories)

AllTrajs = plclass.ReturnAllTrajectoriessInAList()

flag = False
for i in range(len(AllTrajs)) :
        if not(set(AllTrajs[i]) == set(trajectories[i])) :
                flag = True

if flag :
        print("trajectories not the same")


"""
Results = {'Pathlets' : plclass.Pathlets}

df = pd.DataFrame(Results, columns= ['Pathlets'])

print(df)

df.to_csv (r'Pathlets.csv', index = None, header=True)


Results = {'TrajectoriesResults' : plclass.TrajsResults}

df = pd.DataFrame(Results, columns= ['TrajectoriesResults'])

print(df)

df.to_csv (r'TrajectoryResults.csv', index = None, header=True)



data = pd.read_csv (r'Pathlets.csv')

ReadPathlets = data['Pathlets'].tolist()

print(ReadPathlets)
print(plclass.Pathlets)
"""




end = time.time()
print("\nRunTime:",(end - start))