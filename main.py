import itertools
import time
import numpy as np
from pulp import *

#DL = DescriptionLength
def DLTraj(trajectory, PathletDic,MinResult) :
    MinNewTraj = [0] * 1000000

    #Pithanes kathgories gia to trajectory se sxesh me to PathletDic
    NewTrajs = list(itertools.product([0, 1], repeat=len(PathletDic)))
    
    for NewTraj in NewTrajs :
        
        #Pairnw olous tous dunatous sundiasmous twn Pathlets
        PathletIndexesToCheck = []
        index = 0
        for i in NewTraj :
            if i == 1 :
                PathletIndexesToCheck.append(index)
            index += 1
        
        #An exoume vrei me ligotera tote dn xreiazetai na to psaksoume kai pame sto epomeno
        if MinResult < len(PathletIndexesToCheck) :
            continue
        
        for i in range(0,len(PathletIndexesToCheck)) :
            #pairnoume ola ta combinations gia na vroume an sumplhrwnete to trajectory
            CertainIndexes = list(itertools.combinations(PathletIndexesToCheck, i + 1))
       
            for indexes in CertainIndexes :
                CheckPathlet = []

                #Ftiaxnw gia na dw an dhmiourgite to idio Path me to trajectory
                for index in indexes :
                    CheckPathlet = CheckPathlet + PathletDic[index]
                
                #Elegxos omoiothtas me to trajectory
                if len(CheckPathlet) != len(trajectory) :
                    continue
                else :
                    if trajectory == CheckPathlet :
                        
                        if MinResult > i + 1 :
                            
                            MinNewTraj = NewTraj
                            MinResult = i + 1

    #Epistrefw to allagmeno Trajectory me 0/1 gia kathe Pathlet tou dictionary
    #kai ton arithmo twn 1
    return MinNewTraj,MinResult

#Epistrefei to DL tou Pathdic
def DLPathlDic(PathletDic) :
    dl = 0
    for pathlet in PathletDic :
        dl += len(pathlet)
    return dl


#Vasikh sunarthsh Vriskw PathletDic kai NewTrajectories
def MakePathletDicAndNewTrajs(trajectories) :
    PathletDic = []

    for trajectory in trajectories :

        #Parakatw prosthetw sto PathletDic ola ta puthana subpathes
        for i in range(len(trajectory)) :
            for j in range(i + 1,len(trajectory) + 1) :
                if (trajectory[i:j] not in PathletDic) :
                    PathletDic.append(trajectory[i:j])

                    
    NewTrajectories = []
    MinPathletDic = []
    MinResult = 1000000

    for i in range(0,len(PathletDic)) :
        #Pairnw ola ta Combinations gia to PathletDic sumfwna me to oliko
        CertainPathletDics = list(itertools.combinations(PathletDic, i + 1))
        for PathletD in CertainPathletDics :
            NewTrajs = []
            #Sumfwna me ton algorithmo to DL tou PathletDic
            Result = DLPathlDic(PathletD)
            #An exoume hdh kalutero apotelesma psaxnoume to epomeno PathletDic
            if (Result > MinResult) :
                continue
            #Parakatw trexoume to DLtraj gia kathe trajectory
            for j in range(len(trajectories)) :
                NewTraj,res = DLTraj(trajectories[j],PathletD,MinResult)
                NewTrajs.append(NewTraj)
                #Prosthetoume to apotelesma sumfwna me ton tupo
                Result += res
                #An opoiadhpote stigmh exoume kalutero result pame sto epomeno
                if (Result > MinResult) :
                    break

            if (Result < MinResult) :
                NewTrajectories = NewTrajs
                MinPathletDic = PathletD
                MinResult = Result

    #Epistrefw ta kalutera Newtrajectories kai To PathletDic
    return NewTrajectories,MinPathletDic


#---------------------------------------------------------------------------
#---------------------------------------------------------------------------
#---------------------------------------------------------------------------
#---------------------------------------------------------------------------
#---------------------------------------------------------------------------
#PARAKATW LINEAR PROGRAMMING

def FindAllPossiblePathlets(trajectories) :
    AllPossiblePathlets = []

    for traj in trajectories :
        for PathletLength in range(1,len(traj) + 1) :
            for i in range(0,len(traj)) :

                temp = []
                temp.append(traj[i])
                for j in range(i + 1, i + PathletLength) :
                    if (j < len(traj)) :
                        temp.append(traj[j])
                
                if (len(temp) == PathletLength and temp not in AllPossiblePathlets) :
                    AllPossiblePathlets.append(temp)

    return AllPossiblePathlets


def ExistsIndexesInPathlets(AllPossiblePathlets,traj,e) :
    indexes = []
    for i in range(len(AllPossiblePathlets)) :
        flag = False
        for j in AllPossiblePathlets[i] :
            if j not in traj :
                flag = True
                break

        if flag :
            continue
        if e in AllPossiblePathlets[i] :
            indexes.append(i)

    return indexes


#---------------------------------------------------------------------------

start = time.time()

#Thewroume oti Grid 4x4
trajectories=[]

trajectories.append([(0,0),(1,1),(1,2),(3,2)])
trajectories.append([(0,0),(1,1),(1,2),(4,4)])
trajectories.append([(0,0),(1,1),(1,2)])
trajectories.append([(3,2)])

AllPossiblePathlets = FindAllPossiblePathlets(trajectories)

problem = LpProblem("problemName", LpMinimize)

Xp = LpVariable.dicts("Xp", list(range(len(AllPossiblePathlets))), cat="Binary")

Xtp = []
for i in range(len(trajectories)) :
    Xtp.append(LpVariable.dicts("Xtp"+str(i), list(range(len(AllPossiblePathlets))), cat="Binary"))
    
    #constraint
    for j in range(len(Xtp[i])) :
        problem += Xtp[i][j] <= Xp[j]

print(AllPossiblePathlets)
for i in range(len(trajectories)) :

    for j in trajectories[i] :
        indexes = []
        indexes = ExistsIndexesInPathlets(AllPossiblePathlets,trajectories[i],j)

        temp = 0
        for k in indexes :
            temp += Xtp[i][k]

        problem += temp == 1

    

#-------------------
#objective function
temp = 0
for i in range(len(Xp)) :
    temp += Xp[i]

l = 1; #lamda
for i in range(len(Xtp)) :
    for j in range(len(Xtp[i])) :
        temp += l*Xtp[i][j]

problem += temp

#print(problem)

problem.solve()

PathletResults = []
for i in range(len(AllPossiblePathlets)) :
    PathletResults.append(Xp[i].varValue)
print(PathletResults)

TrajsResults = []
for i in range(len(trajectories)) :
    trajResult = []
    for j in range(len(AllPossiblePathlets)) :
        trajResult.append(Xtp[i][j].varValue)
    TrajsResults.append(trajResult)
print(TrajsResults)

"""
NewTrajectories,MinPathletDic = MakePathletDicAndNewTrajs(trajectories)
print(NewTrajectories)
print(MinPathletDic)
"""

end = time.time()
print("\nRunTime:",(end - start))

