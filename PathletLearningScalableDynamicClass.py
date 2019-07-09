import time
import gc
class PathletLearningScalableDynamicClass :
    def __init__(self, trajectories) :
        self.NumOfTrajs = len(trajectories)
        start = time.time()
        self.Pathlets,TpIndexesNeededForPathletLearning,PositionOfPathlets = self.FindAllPossiblePathlets(trajectories)
        end = time.time()
        print("RunTime FindAllPossiblePathlets:",(end - start))

        print(len(self.Pathlets))

        TrajBestDecomposition = []

        #Use for faster execution of Recursion
        self.FoundValuesOfSubPaths = dict()
        self.seen = set()

        for i in range(len(trajectories)) :
            TrajBestDecomposition.append(self.FindFStarForAllSubTrajsAndReturnTrajDec(trajectories[i],TpIndexesNeededForPathletLearning))
            print("Done Traj",i)

        del self.FoundValuesOfSubPaths
        del self.seen
        del TpIndexesNeededForPathletLearning

        gc.collect()

        self.TrajsResults = []#Xtp
        self.PathletResults = [0]*len(self.Pathlets)#Xp

        start = time.time()

        for trajDec in TrajBestDecomposition :
            self.TrajsResults.append(self.TurnTrajDecompositionToXtp(trajDec,PositionOfPathlets))

        end = time.time()
        print("RunTime TrajDecomposition:",(end - start))

        del PositionOfPathlets
        del TrajBestDecomposition

        gc.collect()

        start = time.time()

        self.MinimizePathletLearningResults()

        end = time.time()
        print("RunTime MinimizeResults:",(end - start))

        del self.PathletResults

        print(len(self.Pathlets))


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

        
        def RecursiveCalculationOfFStar(i,j) :
            if i < j-1:
                sub = tuple(traj[i:j+1])

                if sub in self.seen :
                    return self.FoundValuesOfSubPaths[sub]

                minValue = float('inf')
                for k in range(i+1,j) :
                    val1 = RecursiveCalculationOfFStar(i,k)
                    val2 = RecursiveCalculationOfFStar(k,j)
                    ReturnValue = val1 + val2
                    if ReturnValue < minValue :
                        minValue = ReturnValue

                self.seen.add(sub)
                self.FoundValuesOfSubPaths[sub] = minValue

                return minValue
            else :
                sub = tuple(traj[i:i+2])

                if sub in self.seen :
                    return self.FoundValuesOfSubPaths[sub]
                
                
                TpResult = TpIndexesNeededForPathletLearning[sub]
                l = 0.0001
                Value = l + 1.0/(len(TpResult))

                self.seen.add(sub)
                self.FoundValuesOfSubPaths[sub] = Value

                return Value

        print("\nSTARTING RECURSION")
        start = time.time()

        for i in range(len(traj) + 1):
                for j in range(i + 1, len(traj) + 1):

                    subtraj = traj[i:j]

                    minVal = RecursiveCalculationOfFStar(i,j-1)

                    ValuesdictSubTraj[tuple(subtraj)] = minVal
        print("DONE WITH RECURSIVE")
        end = time.time()
        print("RunTime Recursion:",(end - start))

        
        def BacktrackingToFindBestDecomposition(Path) :
            if len(Path) == 2 :
                Value1 = ValuesdictSubTraj[(Path[0],)]
                Value2 = ValuesdictSubTraj[(Path[1],)]

                if Value1 == Value2 :
                    return [(Path[0],Path[1])]
                return Path

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

                    Value = ValuesdictSubTraj[tuple(subpath)]
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
            if len(left) > 1 :
                left = BacktrackingToFindBestDecomposition(left)
            if len(right) > 1 :
                right = BacktrackingToFindBestDecomposition(right)

            if left :
                for t in left :
                    if type(t[0]) is not tuple :
                        BestpathDec.append((t,))
                    else :
                        BestpathDec.append(t)
            BestpathDec.append(tuple(Path))
            if right :
                for t in right :
                    if type(t[0]) is not tuple :
                        BestpathDec.append((t,))
                    else :
                        BestpathDec.append(t)

            return BestpathDec
        
        print("\nFindingBestDecompositionofT")
        start = time.time()

        BestDecTraj = BacktrackingToFindBestDecomposition(traj)
        
        print("DONE WITH BestDecompositionBacktrack")

        print("Best Decomposition : ",BestDecTraj)
        
        #BestDecTraj = BacktrackingToFindBestDecomposition()
        end = time.time()
        print("RunTime BestDecomposition:",(end - start))
        print(BestDecTraj)             

        return BestDecTraj



    def TurnTrajDecompositionToXtp(self, trajDec,PositionOfPathlets) :
        Xtp = [0]*len(trajDec)

        for i in range(len(trajDec)) :
            index = PositionOfPathlets[trajDec[i]]
            Xtp[i] = index
            self.PathletResults[index] = 1

        return Xtp
        
    def MinimizePathletLearningResults(self) :
        #----------------------------------------------
        #Parakatw meiwnw to megethos twn dedomenwn mas
        indexes = []
        indexes1 = []
        DictionaryForIndexReduction = dict()
        counter = 0

        start = time.time()
        
        for i in range(len(self.PathletResults)) :
            if self.PathletResults[i] == 0 :
                indexes.append(i)
                counter = counter + 1
            else :
                indexes1.append(i)
                DictionaryForIndexReduction[i] = counter

        end = time.time()
        print("RunTime Found Indexes For Minimize:",(end - start))

        start = time.time()

        NewPathlets = []
        k = 0
        for i in indexes1 :
            NewPathlets.append(self.Pathlets[i - k])
            k = k + 1

        self.Pathlets = NewPathlets

        end = time.time()
        print("RunTime Done NewPathlets For Minimzie:",(end - start))

        start = time.time()

        for i in range(len(self.TrajsResults)) :
            for f in range(len(self.TrajsResults[i])) :
                index = self.TrajsResults[i][f]
                self.TrajsResults[i][f] = self.TrajsResults[i][f] - DictionaryForIndexReduction[index]

        end = time.time()
        print("RunTime Recalculated TrajsResults:",(end - start)) 

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
