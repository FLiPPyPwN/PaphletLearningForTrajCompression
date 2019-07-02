class PathletLearningScalableDynamicClass :
    def __init__(self, trajectories) :
        self.NumOfTrajs = len(trajectories)

        self.Pathlets,TpIndexesNeededForPathletLearning,PositionOfPathlets = self.FindAllPossiblePathlets(trajectories)

        TrajBestDecomposition = []
        #TA 2 PARAKATW PROSTETHIKAN GIA TAXUTHTA EFOSON UPARXOUN KOINA PATHS
        self.FoundFStarOf = dict()
        self.seenFStarOf = set()

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
                        TpIndexesNeededForPathletLearning[sub] = [trajCounter]
                        seen[sub] = len(AllPossiblePathlets)
                        AllPossiblePathlets.append(sub)
                        seenSet.add(sub)
                    else :
                        TpIndexesNeededForPathletLearning[sub].append(trajCounter)

            trajCounter = trajCounter + 1

        print("FoundAllPossiblePathlets")
        return AllPossiblePathlets, TpIndexesNeededForPathletLearning,seen

    def FindFStarForAllSubTrajsAndReturnTrajDec(self,traj,TpIndexesNeededForPathletLearning) :
        l = 1
        ValuesdictSubTraj = dict()

        SubTraj = []

        def RecursiveCalculationOfFStar(i,j) :
            sub = tuple(traj[i:j])
            if sub in self.seenFStarOf :
                return self.FoundFStarOf[sub]

            if i < j-1 :
                minValue = float('inf')
                for k in range(i+1,j) :
                    val1 = RecursiveCalculationOfFStar(i,k)
                    val2 = RecursiveCalculationOfFStar(k,j)
                    ReturnValue = val1 + val2
                    if ReturnValue < minValue :
                        minValue = ReturnValue

                self.FoundFStarOf[sub] = minValue
                self.seenFStarOf.add(sub)
                return minValue
            else :
                TpResult = TpIndexesNeededForPathletLearning[sub]
                Value = round((1 + 1/(len(TpResult))),5)
                self.FoundFStarOf[sub] = Value
                self.seenFStarOf.add(sub)
                return Value


        AllSubPaths = dict()
        seen = set()
        print("STARTING RECURSION")
        for i in range(len(traj) + 1): 
                for j in range(i + 1, len(traj) + 1):
                    subtraj = traj[i:j]

                    if j - i in seen :
                        AllSubPaths[j - i].append(tuple(subtraj))
                    else :
                        AllSubPaths[j - i] = [tuple(subtraj)]
                    seen.add(j - i)

                    minVal = RecursiveCalculationOfFStar(i,j)

                    ValuesdictSubTraj[tuple(subtraj)] = minVal
        print("DONE WITH RECURSIVE")

        Counter = len(traj) - 1
        PathsToCheck = [traj]

        while Counter > 0 :
            NewPathToCheck = []
            for Path in PathsToCheck :

                min = float('inf')
                sub = []
                flag = False
                for SubPath in AllSubPaths[Counter] :
                    if len(tuple(set(SubPath)-set(Path))) is not 0 :
                        continue

                    Value = ValuesdictSubTraj[SubPath]
                    if Value < min :
                        if len(sub) is not 0 :
                            flag = True
                        min = Value
                        sub = SubPath
                    elif Value > min :
                        flag = True

                if flag == True :
                    NewPathToCheck.append(sub)
                    NewPathToCheck.append(tuple(set(Path)-set(sub)))
                else :
                    NewPathToCheck.append(tuple(Path))

            PathsToCheck = NewPathToCheck
            Counter = Counter - 1

        return PathsToCheck  

    def TurnTrajDecompositionToXtp(self, trajDec,PositionOfPathlets) :
        Xtp = [0]*len(self.Pathlets)
        for sub in trajDec :
            index = PositionOfPathlets[sub]
            Xtp[index] = 1
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
            for traj in self.TrajsResults :
                del traj[i - k]
            k = k + 1

        NewTrajsResults = []
        for traj in self.TrajsResults :
            NewTraj = []
            for i in range(len(traj)) :
                if traj[i] is 1 :
                    NewTraj.append(i)
            NewTrajsResults.append(NewTraj)

        self.TrajsResults = NewTrajsResults


    def ReturnPartRealTraj(self, subtraj1,subtraj2) :
        if subtraj1 == [] :
            return subtraj2
        (x1,y1) = subtraj1[-1]
        (x2,y2) = subtraj2[0]
        dist1 = ((x1-x2)**2 + (y1-y2)**2)**(0.5)

        (x1,y1) = subtraj1[0]
        (x2,y2) = subtraj2[-1]
        dist2 = ((x1-x2)**2 + (y1-y2)**2)**(0.5)

        if dist1 < dist2 :
            return subtraj1 + subtraj2
        else :
            return subtraj2 + subtraj1

    def ReturnRealTraj(self,TrajResult) :
        RealTraj = []
        for i in range(len(TrajResult)) :
            index = TrajResult[i]

            RealTraj = self.ReturnPartRealTraj(RealTraj,self.Pathlets[index])

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
