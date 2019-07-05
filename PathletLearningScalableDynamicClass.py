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
            if i < j-1:
                sub = tuple(traj[i:j+1])

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
                return Value


        AllSubPaths = dict()
        seen = set()
        print("STARTING RECURSION")
        start = time.time()

        MinValuePerLen = dict()

        for i in range(len(traj) + 1):
                for j in range(i + 1, len(traj) + 1):
                    if i == j - 1 : continue
                    subtraj = traj[i:j]

                    if j - i in seen :
                        AllSubPaths[j - i].append(tuple(subtraj))
                    else :
                        AllSubPaths[j - i] = [tuple(subtraj)]
                    seen.add(j - i)

                    minVal = RecursiveCalculationOfFStar(i,j-1)

                    if j-i not in MinValuePerLen :
                        MinValuePerLen[j-i] =  (minVal,False)
                    else :
                        v,f = MinValuePerLen[j-i]
                        if v > minVal :
                            MinValuePerLen[j-i] = (minVal,True)
                        elif v < minVal:
                            MinValuePerLen[j-i] = (v,True)

                    ValuesdictSubTraj[tuple(subtraj)] = minVal
        print("DONE WITH RECURSIVE")
        end = time.time()
        print("\nRunTime:",(end - start))

        print(TpIndexesNeededForPathletLearning)
        print(ValuesdictSubTraj,"\n")
        #print(AllSubPaths)
        
        def BacktrackingToFindBestDecomposition() :

            BestTrajDec = []  #!!!
            
            def SearchAndAddToOnePathLonelyElements() :
                temp = len(BestTrajDec)
                SubPToAdd = []
                flag = True
                for j in range(len(BestTrajDec) - 1,-1,-1) :
                    if len(BestTrajDec[j]) == 1:
                        (x,) = BestTrajDec[j]
                        SubPToAdd.append(x)
                        continue
                    elif j < temp - 2 :
                        del BestTrajDec[len(BestTrajDec)-len(SubPToAdd):len(SubPToAdd)+1]
                        SubPToAdd = reversed(SubPToAdd)
                        BestTrajDec.append(tuple(SubPToAdd))
                        flag = False
                        break
                    else : 
                        flag = False
                        break
                if flag and SubPToAdd:
                    del BestTrajDec[len(BestTrajDec)-len(SubPToAdd):len(SubPToAdd)+1]
                    SubPToAdd = reversed(SubPToAdd)
                    BestTrajDec.append(tuple(SubPToAdd))


            i = 0
            while i < len(traj) :
                if i == len(traj) - 1 :
                    BestTrajDec.append((traj[i],))
                    i = i + 1
                    continue

                count = 1

                sub = traj[i:i+count+1]

                (MinValueL,f) = MinValuePerLen[2]

                Value = ValuesdictSubTraj[tuple(sub)]
                
                if not(MinValueL == Value)  or i == len(traj) - 1 or not(f) :
                    BestTrajDec.append((traj[i],))
                    i = i + 1
                    continue
                else :
                    SearchAndAddToOnePathLonelyElements()

                    count = count + 1
                    while True :
                        sub = traj[i:i+count+1]
                        sub1 = traj[i:i+count]
                        sub2 = traj[i+1:i+count+1]

                        (MinValueLL,ff) = MinValuePerLen[count+1]

                        (MinValueL,f) = MinValuePerLen[count]

                        Value = ValuesdictSubTraj[tuple(sub)]

                        if not(MinValueLL == Value) or not(ff):
                            BestTrajDec.append(tuple(traj[i:i+count]))
                            i = i + count
                            break
                        else:
                            Value1 = ValuesdictSubTraj[tuple(sub1)]
                            Value2 = ValuesdictSubTraj[tuple(sub2)]
                            if not(MinValueL == Value1 and MinValueL == Value2) or not(f):
                                BestTrajDec.append(tuple(traj[i:i+count]))
                                i = i + count
                                break
                            else :
                                count = count + 1
                                if i + count == len(traj) :
                                    BestTrajDec.append(tuple(traj[i:i+count]))
                                    i = i + count
                                    break
                                    
            SearchAndAddToOnePathLonelyElements()

            return BestTrajDec

        print("\n\n\n",MinValuePerLen,"\n\n\n")
        
        start = time.time()
        BestDecTraj = BacktrackingToFindBestDecomposition()
        end = time.time()
        print("\nRunTime:",(end - start))
        print(BestDecTraj)             

        return BestDecTraj



    def TurnTrajDecompositionToXtp(self, trajDec,PositionOfPathlets) :
        Xtp = [0]*len(trajDec)
        #print(trajDec)
        print(trajDec)
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
