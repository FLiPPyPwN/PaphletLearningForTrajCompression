import time
import gc
import multiprocessing
from functools import partial
import os
import pickle

class PathletLearningScalableDynamicClass :
    def __init__(self, trajectories=[]) :
        if not trajectories :
            self.TrajsResults = []
            self.Pathlets = []
            return

        self.TrajsResults = list()
        self.Pathlets = list()

        self.lamda = 0.001

        self.Results = dict()

        while self.lamda < 100000:
            self.MainFunction(trajectories)

            #Save Results according to lamda
            PathletCounter = 0
            TrajsResultsCounter = 0

            for P in self.Pathlets :
                PathletCounter = PathletCounter + len(P)

            for T in self.TrajsResults :
                TrajsResultsCounter = TrajsResultsCounter + len(T)

            if PathletCounter == (len(trajectories) * len(trajectories[0])) :
                break

            self.Results[self.lamda] = [PathletCounter,TrajsResultsCounter]
        
            self.TrajsResults = list()
            self.Pathlets = list()

            gc.collect()
            self.lamda = self.lamda*10
            

        print(self.Results)


        

        
    def MainFunction(self, trajectories) :
        m = multiprocessing.Manager()
        
        self.l = m.Lock()

        cpu_count = multiprocessing.cpu_count()
        if len(trajectories) < cpu_count :
            cpu_count = len(trajectories)
        p = multiprocessing.Pool(cpu_count)
        #8 -- 1211sec -- 20000 trajectories
        #8 -- 2454sec -- 40000 trajectories

        self.ListForClean = m.list()
        self.ListForClean.append(time.time())
        self.ListForClean.append(cpu_count)
        self.SetForProcs = m.dict()

        self.TpCounterNeededForPathletLearning = m.dict()
        p.map(self.FindTpCounterOfPathlets,list(trajectories[i:i+int(len(trajectories)/cpu_count)] for i in range(0,len(trajectories),int(len(trajectories)/cpu_count))))

        self.TpCounterNeededForPathletLearning = dict(self.TpCounterNeededForPathletLearning)

        print("FoundTpCounters")

        gc.collect()

        self.Pathlets = m.dict()
        self.TrajsResults = list(p.map(self.FindFStarAndTrajRes,trajectories))

        p.close()

        self.Pathlets = list(self.Pathlets) #lista mono me ta keys tou dict #python3.6+ einai ordered opws xreiazomaste !!!

        del self.TpCounterNeededForPathletLearning
        del m
        del p
        del self.ListForClean
        del self.SetForProcs

        gc.collect()


    def FindFStarAndTrajRes(self,traj) :
        FoundValuesOfSubPaths = self.FindFStarForAllSubTrajs(traj)
        TrajResult = self.ReturnTrajResultAfterFindingDecomposition(traj,FoundValuesOfSubPaths)


        del FoundValuesOfSubPaths

        if time.time() - self.ListForClean[0] > 180.0 :
            proc = os.getpid()
            if  proc not in self.SetForProcs :
                if self.ListForClean[1] == 1 :
                    self.ListForClean[1] = multiprocessing.cpu_count()
                    self.SetForProcs.clear()
                    self.ListForClean[0] = time.time()
                else :
                    self.ListForClean[1] = self.ListForClean[1] - 1
                    self.SetForProcs[proc] = 0

                gc.collect()
                

        return TrajResult
        

    def FindTpCounterOfPathlets(self, trajectories) :
        for traj in trajectories :
            for i in range(len(traj) + 1): 

                for j in range(i + 1, i + 3): 

                    sub = tuple(traj[i:j])

                    if (sub not in self.TpCounterNeededForPathletLearning) :
                        self.l.acquire()

                        if (sub not in self.TpCounterNeededForPathletLearning) :
                            self.TpCounterNeededForPathletLearning[sub] = 1
                        else :
                            self.TpCounterNeededForPathletLearning[sub] = self.TpCounterNeededForPathletLearning[sub] + 1

                        self.l.release()
                    else :
                        self.TpCounterNeededForPathletLearning[sub] = self.TpCounterNeededForPathletLearning[sub] + 1

        gc.collect()

                    

    
    def FindFStarForAllSubTrajs(self,traj) :

        FoundValuesOfSubPaths = dict()

        def RecursiveCalculationOfFStar(i,j) :
            if i < j-1:
                sub = tuple(traj[i:j+1])

                if sub in FoundValuesOfSubPaths :
                    return FoundValuesOfSubPaths[sub]

                minValue = float('inf')
                for k in range(i+1,j) :
                    val1 = RecursiveCalculationOfFStar(i,k)
                    val2 = RecursiveCalculationOfFStar(k,j)
                    ReturnValue = val1 + val2
                    if ReturnValue < minValue :
                        minValue = ReturnValue

                FoundValuesOfSubPaths[sub] = minValue

                return minValue
            else :
                sub = tuple(traj[i:i+2])

                if sub in FoundValuesOfSubPaths :
                    return FoundValuesOfSubPaths[sub]
                
                TpResult = self.TpCounterNeededForPathletLearning[sub]
                Value = self.lamda + 1.0/TpResult

                FoundValuesOfSubPaths[sub] = Value

                return Value

        for i in range(len(traj)):
                for j in range(i + 1, len(traj) + 1):

                    subtraj = traj[i:j]

                    FoundValuesOfSubPaths[tuple(subtraj)] = RecursiveCalculationOfFStar(i,j-1)

        return FoundValuesOfSubPaths


    def ReturnTrajResultAfterFindingDecomposition(self,traj,FoundValuesOfSubPaths) :
    
        def BacktrackingToFindBestDecomposition(Path) :
            if len(Path) == 2 :
                Value1 = FoundValuesOfSubPaths[(Path[0],)]
                Value2 = FoundValuesOfSubPaths[(Path[1],)]

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

                    Value = FoundValuesOfSubPaths[tuple(subpath)]
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

        if path not in self.Pathlets :
            self.l.acquire()

            if path not in self.Pathlets :
                index = len(self.Pathlets)
                self.Pathlets[path] = index
            else :
                index = self.Pathlets[path]

            self.l.release()
        else :
            index = self.Pathlets[path]

        return index


    def ReturnRealTraj(self,TrajResult) :
        RealTraj = []
        for i in range(len(TrajResult)) :
            index = TrajResult[i]

            RealTraj = RealTraj + list(self.Pathlets[index])

        return RealTraj

    def ReturnAllTrajectoriesInAList(self) :
        RealTrajs = []
        for i in range(len(self.TrajsResults)) :
            RealTrajs.append(self.ReturnRealTraj(self.TrajsResults[i]))

        return RealTrajs

    def ReturnSpecificTrajectoryByIndex(self, index) :
        if index > len(self.Pathlets) - 1 or index < 0:
            print("There are",len(self.Pathlets),"trajectories but you asked for the",index)
        else :
            return self.ReturnRealTraj(self.TrajsResults[index])
