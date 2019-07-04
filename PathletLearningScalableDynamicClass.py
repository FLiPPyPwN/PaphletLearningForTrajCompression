import time
class PathletLearningScalableDynamicClass :
    def __init__(self, trajectories) :
        self.NumOfTrajs = len(trajectories)
        start = time.time()
        self.Pathlets,TpIndexesNeededForPathletLearning,PositionOfPathlets = self.FindAllPossiblePathlets(trajectories)
        end = time.time()
        print("\nRunTime:",(end - start))

        print(len(self.Pathlets))

        TrajBestDecomposition = []

        for i in range(len(trajectories)) :
            TrajBestDecomposition.append(self.FindFStarForAllSubTrajsAndReturnTrajDec(trajectories[i],TpIndexesNeededForPathletLearning))
            print("Done Traj",i)

        self.TrajsResults = []#Xtp
        self.PathletResults = [0]*len(self.Pathlets)#Xp

        for trajDec in TrajBestDecomposition :
            self.TrajsResults.append(self.TurnTrajDecompositionToXtp(trajDec,PositionOfPathlets))

        self.MinimizePathletLearningResults(self.PathletResults)


    def FindAllPossiblePathlets(self, trajectories) :
        print("STARTFINDPOSSIBLEPATHLETS")
        AllPossiblePathlets = []
        TpIndexesNeededForPathletLearning = dict()

        seenSet = set()
        seen = dict()

        trajCounter = 0
        for traj in trajectories :

            for i in range(len(traj) + 1): 

                for j in range(i + 1, len(traj) + 1): 

                    sub = tuple(traj[i:j])
                    #print(sub)
                    if (sub not in seenSet) :
                        TpIndexesNeededForPathletLearning[sub] = {trajCounter}
                        seen[sub] = len(AllPossiblePathlets)
                        AllPossiblePathlets.append(sub)
                        seenSet.add(sub)
                    else :
                        TpIndexesNeededForPathletLearning[sub].add(trajCounter)

            trajCounter = trajCounter + 1

        print("FoundAllPossiblePathlets")
        return AllPossiblePathlets, TpIndexesNeededForPathletLearning,seen

    def FindFStarForAllSubTrajsAndReturnTrajDec(self,traj,TpIndexesNeededForPathletLearning) :
        l = 1
        ValuesdictSubTraj = dict()

        SubTraj = []
        #print(TpIndexesNeededForPathletLearning)
        def RecursiveCalculationOfFStar(i,j) :
            if i < j-1 :
                sub = tuple(traj[i:j])

                minValue = float('inf')
                for k in range(i+1,j) :

                    val1 = RecursiveCalculationOfFStar(i,k)
                    val2 = RecursiveCalculationOfFStar(k,j)
                    ReturnValue = val1 + val2
                    if ReturnValue < minValue :
                        minValue = ReturnValue

                return minValue
            else :
                sub = tuple(traj[i:i+2])
                
                TpResult = TpIndexesNeededForPathletLearning[sub]
                l = 1
                Value = l + 1.0/(len(TpResult))
                print(sub,len(sub),Value)
                return Value


        AllSubPaths = dict()
        seen = set()
        print("STARTING RECURSION")
        start = time.time()

        ChoicesInCertainStep = dict()
        MaxIndexInCertainStep = dict()
        for i in range(len(traj) + 1):
                if (i < len(traj)) :
                    subtraj222 = traj[i]
                    ChoicesInCertainStep[subtraj222] = list()
                    MaxIndexInCertainStep[subtraj222] = len(traj) - i
                for j in range(i + 1, len(traj) + 1):
                    subtraj = traj[i:j]

                    if (i < len(traj)) :
                        ChoicesInCertainStep[subtraj222].append(subtraj)

                    if j - i in seen :
                        AllSubPaths[j - i].append(tuple(subtraj))
                    else :
                        AllSubPaths[j - i] = [tuple(subtraj)]
                    seen.add(j - i)
                    print("AAAA:  ",subtraj,i,j-1)
                    minVal = RecursiveCalculationOfFStar(i,j-1)

                    ValuesdictSubTraj[tuple(subtraj)] = minVal
        print("DONE WITH RECURSIVE")
        end = time.time()
        print("\nRunTime:",(end - start))

        print(ValuesdictSubTraj,"\n")
        #print(AllSubPaths)
        #print(ChoicesInCertainStep,"\n")
        
        #print(MaxIndexInCertainStep,"\n")
        
        BestCompleteDecompositionValue = ValuesdictSubTraj[tuple(traj)]

        def BacktrackingToFindBestDecomposition(subpath,Value) :
            index = 0
            while index < MaxIndexInCertainStep[subpath] :
                SubPathNow = tuple(ChoicesInCertainStep[subpath][index])
                print(SubPathNow)

                if index + 1 < MaxIndexInCertainStep[subpath] :
                    Nextsubpath = ChoicesInCertainStep[subpath][index + 1][-1]
                    ValueNow = ValuesdictSubTraj[SubPathNow]
                    if Value + ValueNow > BestCompleteDecompositionValue :
                        return [],False
                    else :
                        SubPathForward,flag = BacktrackingToFindBestDecomposition(Nextsubpath,Value+ValueNow)
                        if flag :
                            Result = list()
                            Result.append(SubPathNow)
                            Result = Result + SubPathForward

                            return Result,True

                else :
                    ValueNow = ValuesdictSubTraj[SubPathNow]
                    if Value + ValueNow == BestCompleteDecompositionValue :
                        return [SubPathNow],True
                    else :
                        return [],False

                index = index + 1

            return [],False
        start = time.time()
        BestDecTraj,temp = BacktrackingToFindBestDecomposition(traj[0],0)
        end = time.time()
        print("\nRunTime:",(end - start))
        #print("LOLOLOLO   ",BestDecTraj)
        return BestDecTraj



    def TurnTrajDecompositionToXtp(self, trajDec,PositionOfPathlets) :
        Xtp = [0]*len(trajDec)
        #print(trajDec)

        for i in range(len(trajDec)) :
            index = PositionOfPathlets[trajDec[i]]
            Xtp[i] = index
            self.PathletResults[index] = 1

        return Xtp
        
    def MinimizePathletLearningResults(self,PathletResults) :
        #----------------------------------------------
        #Parakatw meiwnw to megethos twn dedomenwn mas
        indexes = []
        for i in range(len(PathletResults)) :
            if PathletResults[i] == 0 :
                indexes.append(i)

        #print("\nIndexes to Remove: ",indexes)

        k = 0
        for i in indexes :
            del self.Pathlets[i - k]
            del PathletResults[i - k]

            for f in range(len(self.TrajsResults)) :
                for ff in range(len(self.TrajsResults[f])) :
                    index = self.TrajsResults[f][ff]
                    if index > i - k :
                        
                        self.TrajsResults[f][ff] = index - 1
                
            k = k + 1

    def ReturnRealTraj(self,TrajResult) :
        RealTraj = []
        for i in range(len(TrajResult)) :
            index = TrajResult[i]

            RealTraj = RealTraj + list(self.Pathlets[index])

        return RealTraj

    def ReturnAllTrajsInAList(self) :
        RealTrajs = []
        for i in range(len(self.TrajsResults)) :
            RealTrajs.append(self.ReturnRealTraj(self.TrajsResults[i]))

        return RealTrajs

    def ReturnSpecificTrajectoryByIndex(self, index) :
        if index > self.NumOfTrajs - 1 or index < 0:
            print("There are",self.NumOfTrajs,"trajectories but you asked for the",index)
        else :
            return self.ReturnRealTraj(self.TrajsResults[index])
