import itertools
import time

#DL = DescriptionLength
def DLTraj(trajectory, PathletDic) :
    MinNewTraj = [0] * 1000000
    OnesOfMin = len(MinNewTraj)

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
            
        if OnesOfMin < len(PathletIndexesToCheck) :
            continue
        
        for i in range(0,len(PathletIndexesToCheck)) :
            CertainIndexes = list(itertools.combinations(PathletIndexesToCheck, i + 1))
       
            for indexes in CertainIndexes :
                CheckPathlet = []

                for index in indexes :
                    CheckPathlet = CheckPathlet + PathletDic[index]
                

                if len(CheckPathlet) != len(trajectory) :
                    continue
                else :
                    if trajectory == CheckPathlet :
                        
                        if OnesOfMin > len(PathletIndexesToCheck) :
                            
                            MinNewTraj = NewTraj
                            OnesOfMin = len(PathletIndexesToCheck)


    return MinNewTraj,OnesOfMin

def DLPathlDic(PathletDic) :
    dl = 0
    for pathlet in PathletDic :
        dl += len(pathlet)
    return dl


def MakePathletDirAndNewTrajs(trajectories) :
    PathletDic = []

    for trajectory in trajectories :

        #Parakatw prosthetw sto PathletDic ola ta puthana subpathes
        for i in range(len(trajectory)) :
            for j in range(i + 1,len(trajectory) + 1) :
                if (trajectory[i:j] not in PathletDic) :
                    PathletDic.append(trajectory[i:j])

                    
    NewTrajectories = []
    MinPathletDic = []
    MinResult = 100000000000

    for i in range(0,len(PathletDic)) :
        CertainPathletDics = list(itertools.combinations(PathletDic, i + 1))
        for PathletD in CertainPathletDics :
            NewTrajs = []
            Result = DLPathlDic(PathletD)
            if (Result > MinResult) :
                continue
            for j in range(len(trajectories)) :
                NewTraj,res = DLTraj(trajectories[j],PathletD)
                NewTrajs.append(NewTraj)
                Result += res
                if (Result > MinResult) :
                    break

            if (Result < MinResult) :
                NewTrajectories = NewTrajs
                MinPathletDic = PathletD
                MinResult = Result

    return NewTrajectories,MinPathletDic

#---------------------------------------------------------------------------
#---------------------------------------------------------------------------
#---------------------------------------------------------------------------
#---------------------------------------------------------------------------

start = time.time()

#Thewroume oti Grid 4x4
trajectories=[]

trajectories.append([(0,0),(1,1),(1,2),(3,2)])
trajectories.append([(0,0),(1,1),(1,3)])
trajectories.append([(1,2),(3,2),(3,3)])

NewTrajectories,MinPathletDic = MakePathletDirAndNewTrajs(trajectories)

print(NewTrajectories)
print(MinPathletDic)

end = time.time()
print(end - start)
