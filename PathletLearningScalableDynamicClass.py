class PathletLearningScalableDynamicClass :
    def __init__(self, trajectories) :
        self.NumOfTrajs = len(trajectories)

        self.Pathlets,TpIndexesNeededForPathletLearning= self.FindAllPossiblePathlets(trajectories)
        print(len(self.Pathlets))
        print(self.Pathlets,"\n")
        print(TpIndexesNeededForPathletLearning)

        FStarSubTrajs = []

        for i in range(len(trajectories)) :
            FStarSubTrajs.append(self.FindFStarForAllSubTrajs(trajectories[i],TpIndexesNeededForPathletLearning))


    def FindAllPossiblePathlets(self, trajectories) :
        print("STARTFINDPOSSIBLEPATHLETS")
        AllPossiblePathlets = []
        TpIndexesNeededForPathletLearning = dict()

        seenSet = set()

        trajCounter = 0
        for traj in trajectories :

            for i in range(len(traj) + 1): 

                for j in range(i + 1, len(traj) + 1): 

                    sub = tuple(traj[i:j])
                    #print(sub)
                    if (sub not in seenSet) :
                        TpIndexesNeededForPathletLearning[sub] = [trajCounter]
                        AllPossiblePathlets.append(sub)
                        seenSet.add(sub)
                    else :
                        TpIndexesNeededForPathletLearning[sub].append(trajCounter)

            trajCounter = trajCounter + 1

        print("FoundAllPossiblePathlets")
        return AllPossiblePathlets, TpIndexesNeededForPathletLearning

    def FindFStarForAllSubTrajs(self,traj,TpIndexesNeededForPathletLearning) :
        l = 1
        ValuesdictSubTraj = dict()

        SubTraj = []

        def RecursiveCalculationOfFStar(i,j) :
            if i < j-1 :
                minValue = float('inf')
                for k in range(i+1,j) :
                    val1 = RecursiveCalculationOfFStar(i,k)
                    val2 = RecursiveCalculationOfFStar(k,j)
                    ReturnValue = val1 + val2
                    #print(sub1,"   ",sub2,"  ==== ",ReturnValue)
                    if ReturnValue < minValue :
                        minValue = ReturnValue

                return minValue

            else :
                sub = tuple(traj[i:j]) 
                TpResult = TpIndexesNeededForPathletLearning[sub]
                return round((10 + 1/(len(TpResult))),5)


        AllSubPaths = dict()
        seen = set()
        for i in range(len(traj) + 1): 
                for j in range(i + 1, len(traj) + 1):
                    subtraj = traj[i:j]

                    if j - i in seen :
                        AllSubPaths[j - i].append(tuple(subtraj))
                    else :
                        AllSubPaths[j - i] = [tuple(subtraj)]
                    seen.add(j - i)

                    print(subtraj)

                    minVal = RecursiveCalculationOfFStar(i,j)

                    ValuesdictSubTraj[tuple(subtraj)] = minVal

        print(AllSubPaths)

        PathsToCheck = []
        

        print(ValuesdictSubTraj)
        print(minVal,"\n")

