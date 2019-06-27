import time
from PathletLearningClass import *

start = time.time()

#Thewroume oti Grid 4x4
trajectories=[]

trajectories.append([[0,0],[1,1],[1,2],[2,2]])
trajectories.append([[0,0],[1,1],[1,2],[0,2]])
trajectories.append([[0,0],[1,1],[1,2]])
trajectories.append([[2,2]])

plclass = PathletLearningClass(trajectories)

print(plclass.ReturnAllTrajsInAList())

end = time.time()
print("\nRunTime:",(end - start))