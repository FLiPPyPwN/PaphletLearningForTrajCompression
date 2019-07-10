import time
import gc
class PathletLearningScalableDynamicClass :
    def __init__(self, trajectories) :
        self.NumOfTrajs = len(trajectories)
        TpCounterNeededForPathletLearning = self.FindTpCounterOfPathlets(trajectories)

        #Use for faster execution of Recursion
        self.FoundValuesOfSubPaths = dict()

        for i in range(len(trajectories)) :
            self.FindFStarForAllSubTrajs(trajectories[i],TpCounterNeededForPathletLearning)

        del TpCounterNeededForPathletLearning
        gc.collect()

        self.Pathlets = []
        self.TrajsResults = []
        self.PathletIndexes = dict()

        for i in range(len(trajectories)) :
            self.TrajsResults.append(self.ReturnTrajResultAfterFindingDecomposition(trajectories[i]))

        del self.FoundValuesOfSubPaths
        del self.PathletIndexes

        gc.collect()


    def FindTpCounterOfPathlets(self, trajectories) :
        NumOfPathlets = 0
        TpCounterNeededForPathletLearning = dict()
        
        for traj in trajectories :

            for i in range(len(traj) + 1): 

                for j in range(i + 1, i + 3): 

                    sub = tuple(traj[i:j])

                    if (sub not in TpCounterNeededForPathletLearning) :
                        TpCounterNeededForPathletLearning[sub] = 1
                        NumOfPathlets + NumOfPathlets + 1
                    else :
                        TpCounterNeededForPathletLearning[sub] = TpCounterNeededForPathletLearning[sub] + 1

        return TpCounterNeededForPathletLearning

    
    def FindFStarForAllSubTrajs(self,traj,TpCounterNeededForPathletLearning) :

        def RecursiveCalculationOfFStar(i,j) :
            if i < j-1:
                sub = tuple(traj[i:j+1])

                if sub in self.FoundValuesOfSubPaths :
                    return self.FoundValuesOfSubPaths[sub]

                minValue = float('inf')
                for k in range(i+1,j) :
                    val1 = RecursiveCalculationOfFStar(i,k)
                    val2 = RecursiveCalculationOfFStar(k,j)
                    ReturnValue = val1 + val2
                    if ReturnValue < minValue :
                        minValue = ReturnValue

                self.FoundValuesOfSubPaths[sub] = minValue

                return minValue
            else :
                sub = tuple(traj[i:i+2])

                if sub in self.FoundValuesOfSubPaths :
                    return self.FoundValuesOfSubPaths[sub]
                
                TpResult = TpCounterNeededForPathletLearning[sub]
                l = 1
                Value = l + 1.0/TpResult

                self.FoundValuesOfSubPaths[sub] = Value
                del TpCounterNeededForPathletLearning[sub]

                return Value

        for i in range(len(traj)):
                for j in range(i + 1, len(traj) + 1):

                    subtraj = traj[i:j]

                    self.FoundValuesOfSubPaths[tuple(subtraj)] = RecursiveCalculationOfFStar(i,j-1)


    def ReturnTrajResultAfterFindingDecomposition(self,traj) :
    
        def BacktrackingToFindBestDecomposition(Path) :
            if len(Path) == 2 :
                Value1 = self.FoundValuesOfSubPaths[(Path[0],)]
                Value2 = self.FoundValuesOfSubPaths[(Path[1],)]

                if Value1 == Value2 :
                    return [self.PathToPathletIndex((Path[0],Path[1]))]
                return [self.PathToPathletIndex((Path[0],)),self.PathToPathletIndex((Path[1],))]
            elif len(Path) == 1 :
                return [self.PathToPathletIndex(tuple(Path))]
            elif len(Path) == 0 :
                return []

            BestpathDec = []
            left = []
            right = []

            counter = len(Path) - 1
            flag = True
            while flag :
                MinValue = float('inf')
                Min_i = -1
                FoundBetterSubPath = False
                for i in range(len(Path) - counter + 1) :
                    subpath = Path[i:i+counter]

                    Value = self.FoundValuesOfSubPaths[tuple(subpath)]
                    if MinValue == Value :
                        continue
                    elif Value < MinValue and MinValue == float('inf') :
                        MinValue = Value
                        Min_i = i
                    elif Value > MinValue :
                        FoundBetterSubPath = True
                    else :
                        MinValue = Value
                        Min_i = i
                        FoundBetterSubPath = True

                if FoundBetterSubPath :
                    if Min_i > 0 :
                        left = left + Path[0:Min_i]
                    if Min_i + counter < len(Path) :
                        right =  Path[Min_i+counter:len(Path)]+right 
                    Path = Path[Min_i:Min_i+counter]

                counter = counter - 1
                if counter == 1 :
                    flag = False


            left = BacktrackingToFindBestDecomposition(left)
            right = BacktrackingToFindBestDecomposition(right)
            
            if left :
                BestpathDec = left
            BestpathDec = BestpathDec + [self.PathToPathletIndex(tuple(Path))]
            if right :
                BestpathDec = BestpathDec + right

            return BestpathDec


        BestDecTrajViaPathlet = BacktrackingToFindBestDecomposition(traj)          

        return BestDecTrajViaPathlet

    def PathToPathletIndex(self,path) :
        index = -1
        if path not in self.PathletIndexes :
            index = len(self.PathletIndexes)
            self.PathletIndexes[path] = index
            self.Pathlets.append(path)
        else :
            index = self.PathletIndexes[path]

        return index


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
