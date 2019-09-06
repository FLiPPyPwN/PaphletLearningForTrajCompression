import time
import gc
import multiprocessing
from functools import partial
import os
import pickle
import matplotlib.pyplot as plt
import numpy as np
import copy

class PathletLearningScalableDynamicClass :
    def __init__(self, trajectories=[],l = -1) :
        if not trajectories :
            self.TrajsResults = []
            self.Pathlets = []
            return

        RealTrajListCounter = 0
        for T in trajectories :
                RealTrajListCounter = RealTrajListCounter + len(T)

        self.NormalTrajectories = list()

        self.TrajsResults = list()
        self.Pathlets = list()

        self.lamda = 0.001
        if not(l == -1) :
            self.lamda = l

        Results = dict()
        
        self.BestResultCounter = RealTrajListCounter
        self.BestResult = ()

        if l == - 1 :
            while self.lamda < 100000:
                self.MainFunction(trajectories)

                #Save Results according to lamda
                PathletCounter = 0
                TrajsResultsCounter = 0

                for P in self.Pathlets :
                    PathletCounter = PathletCounter + len(P)

                for T in self.TrajsResults :
                    TrajsResultsCounter = TrajsResultsCounter + len(T)

                if PathletCounter == RealTrajListCounter :
                    break

                Results[self.lamda] = [PathletCounter,TrajsResultsCounter]


                if PathletCounter + TrajsResultsCounter < self.BestResultCounter :
                    self.BestResult = (self.Pathlets,self.TrajsResults)
            
                self.TrajsResults = list()
                self.Pathlets = list()

                gc.collect()
                self.lamda = self.lamda*10

        else :
            self.MainFunction(trajectories)

            PathletCounter = 0
            TrajsResultsCounter = 0

            for P in self.Pathlets :
                PathletCounter = PathletCounter + len(P)

            for T in self.TrajsResults :
                TrajsResultsCounter = TrajsResultsCounter + len(T)

            Results[self.lamda] = [PathletCounter,TrajsResultsCounter]

            if PathletCounter + TrajsResultsCounter < self.BestResultCounter :
                self.BestResult = (self.Pathlets,self.TrajsResults)

            gc.collect()
            

        if self.BestResult is not () :
            (self.Pathlets,self.TrajsResults) = self.BestResult
        else :
            print("Pathlet Learning is not worth it cause not many common subpaths")
            self.NormalTrajectories = trajectories
            self.Pathlets = list()
            self.TrajsResults = list()
            gc.collect()



        

        
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

        print("FoundTpCounters for lamda =",self.lamda)

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

        RealTrajs = RealTrajs + self.NormalTrajectories

        return RealTrajs

    def ReturnSpecificTrajectoryByIndex(self, index) :
        if index > len(self.Pathlets) - 1 or index < 0:
            print("There are",len(self.Pathlets),"trajectories but you asked for the",index)
        else :
            return self.ReturnRealTraj(self.TrajsResults[index])

    def TimesPathletsUsed(self) :

        TrajectoriesThatUsePathlet = [[] for _ in range(len(self.Pathlets))]

        TimesPathletsUsed = [0]*len(self.Pathlets)
        for trajIndex in range(len(self.TrajsResults)) :
            for PathletIndex in self.TrajsResults[trajIndex] :
                TimesPathletsUsed[PathletIndex] = TimesPathletsUsed[PathletIndex] + 1

                TrajectoriesThatUsePathlet[PathletIndex].append(trajIndex)


        #calculate percentage of reconstructable trajectories by deleting methodically from pathlets
        TrajectoriesDeclined = set()
        CalculatedResult = [(100,100)]

        PathletsRemovedCounter = 1
        while TimesPathletsUsed :
            minIndex = TimesPathletsUsed.index(min(TimesPathletsUsed))

            TrajectoriesDeclined.update(TrajectoriesThatUsePathlet[minIndex])

            del TrajectoriesThatUsePathlet[minIndex]
            del TimesPathletsUsed[minIndex]

            if ((len(self.Pathlets) - PathletsRemovedCounter)/len(self.Pathlets)) == 0 or ((len(self.TrajsResults) - len(TrajectoriesDeclined))/len(self.TrajsResults)) == 0 :
                break

            CalculatedResult.append((((len(self.Pathlets) - PathletsRemovedCounter)/len(self.Pathlets))*100, ((len(self.TrajsResults) - len(TrajectoriesDeclined))/len(self.TrajsResults))*100))

            PathletsRemovedCounter = PathletsRemovedCounter + 1


        xaxis = list()
        yaxis = list()

        for (x,y) in CalculatedResult :
            xaxis.append(x)
            yaxis.append(y)

        BestDifference = 0
        BestDifResult = ()
        for index in range(len(xaxis)) :
            if yaxis[index] - xaxis[index] > BestDifference or not BestDifResult:
                BestDifference = yaxis[index] - xaxis[index]
                BestDifResult = (xaxis[index],yaxis[index])

        (x,y) = BestDifResult

        plt.annotate('BestResult: ('+str(round(x,3))+","+str(round(y,3))+")", xy=BestDifResult, xytext=(5, 95),
            arrowprops=dict(facecolor='black', shrink=0.05))

        plt.title('PercentageOfReconstrutedTrajectoriesByPathlets')
        plt.xlabel('Percentage of Dictionary in Use')
        plt.ylabel('Percentage of Reconstructable Trajectories')

        plt.plot(xaxis, yaxis,'--bo')
        plt.axis([0, 100, 0, 100])
        plt.show()


    def TimesPathletsUsed(self,flag) :
        if not self.Pathlets :
            print("There are no Pathlets!")
            return

        TrajectoriesThatUsePathlet = [[] for _ in range(len(self.Pathlets))]

        TimesPathletsUsed = [0]*len(self.Pathlets)
        for trajIndex in range(len(self.TrajsResults)) :
            for PathletIndex in self.TrajsResults[trajIndex] :
                TimesPathletsUsed[PathletIndex] = TimesPathletsUsed[PathletIndex] + 1

                TrajectoriesThatUsePathlet[PathletIndex].append(trajIndex)

        for i in range(len(TimesPathletsUsed)) :
            TimesPathletsUsed[i] = TimesPathletsUsed[i] * len(self.Pathlets[i])


        #calculate percentage of reconstructable trajectories by deleting methodically from pathlets
        TrajectoriesDeclined = set()
        CalculatedResult = [(100,100)]

        PathletsRemovedCounter = 1
        while TimesPathletsUsed :
            minIndex = TimesPathletsUsed.index(min(TimesPathletsUsed))

            TrajectoriesDeclined.update(TrajectoriesThatUsePathlet[minIndex])

            del TrajectoriesThatUsePathlet[minIndex]
            del TimesPathletsUsed[minIndex]

            if ((len(self.Pathlets) - PathletsRemovedCounter)/len(self.Pathlets)) == 0 or ((len(self.TrajsResults) - len(TrajectoriesDeclined))/len(self.TrajsResults)) == 0 :
                break

            CalculatedResult.append((((len(self.Pathlets) - PathletsRemovedCounter)/len(self.Pathlets))*100, ((len(self.TrajsResults) - len(TrajectoriesDeclined))/len(self.TrajsResults))*100))

            PathletsRemovedCounter = PathletsRemovedCounter + 1


        xaxis = list()
        yaxis = list()

        for (x,y) in CalculatedResult :
            xaxis.append(x)
            yaxis.append(y)

        BestDifference = 0
        BestDifResult = ()
        for index in range(len(xaxis)) :
            if yaxis[index] - xaxis[index] > BestDifference or not BestDifResult:
                BestDifference = yaxis[index] - xaxis[index]
                BestDifResult = (xaxis[index],yaxis[index])


        (x,y) = BestDifResult

        plt.annotate('BestResult: ('+str(round(x,3))+","+str(round(y,3))+")", xy=BestDifResult, xytext=(5, 95),
            arrowprops=dict(facecolor='black', shrink=0.05))

        plt.title('PercentageOfReconstrutedTrajectoriesByPathlets')
        plt.xlabel('Percentage of Dictionary in Use')
        plt.ylabel('Percentage of Reconstructable Trajectories')

        plt.plot(xaxis, yaxis,'--bo')
        plt.axis([0, 100, 0, 100])
        plt.show()

        if flag :
            self.OptimizeAccordingToResultPercentageOfPathletsAndTrajectories(BestDifResult)




    def OptimizeAccordingToResultPercentageOfPathletsAndTrajectories(self,BestDifResult) :
        PreviousRes = 0 #Check if Optimization worth it
        for P in self.Pathlets :
                PreviousRes = PreviousRes + len(P)
        for T in self.TrajsResults :
                PreviousRes = PreviousRes + len(T)
                

        (x,y) = BestDifResult

        TrajectoriesThatUsePathlet = [[] for _ in range(len(self.Pathlets))]

        TimesPathletsUsed = [0]*len(self.Pathlets)
        for trajIndex in range(len(self.TrajsResults)) :
            for PathletIndex in self.TrajsResults[trajIndex] :
                TimesPathletsUsed[PathletIndex] = TimesPathletsUsed[PathletIndex] + 1

                TrajectoriesThatUsePathlet[PathletIndex].append(trajIndex)

        for i in range(len(TimesPathletsUsed)) :
            TimesPathletsUsed[i] = TimesPathletsUsed[i] * len(self.Pathlets[i])


        #Xrhsh gia euresh twn pathlets p tha petaksoume
        PathletsDeclinedTemp = copy.deepcopy(TimesPathletsUsed)
        PathletsDeclinedTemp = np.argsort(PathletsDeclinedTemp)
        #------------------------------------------------

        TrajectoriesDeclined = set()
        PathletsDeclined = list()

        CalculatedResult = [(100,100)]

        PathletsRemovedCounter = 0
        while TimesPathletsUsed :
            if ((len(self.Pathlets) - PathletsRemovedCounter)/len(self.Pathlets))*100 == x and ((len(self.TrajsResults) - len(TrajectoriesDeclined))/len(self.TrajsResults))*100 == y :
                break

            PathletsRemovedCounter = PathletsRemovedCounter + 1

            minIndex = TimesPathletsUsed.index(min(TimesPathletsUsed))

            TrajectoriesDeclined.update(TrajectoriesThatUsePathlet[minIndex])
            PathletsDeclined.append(minIndex)

            del TrajectoriesThatUsePathlet[minIndex]
            del TimesPathletsUsed[minIndex]

            
            CalculatedResult.append((((len(self.Pathlets) - PathletsRemovedCounter)/len(self.Pathlets))*100, ((len(self.TrajsResults) - len(TrajectoriesDeclined))/len(self.TrajsResults))*100))

        PathletsDeclined = PathletsDeclinedTemp[0:PathletsRemovedCounter]

        NormalTrajectories = list()
        for i in TrajectoriesDeclined :
            NormalTrajectories.append(self.ReturnRealTraj(self.TrajsResults[i]))

        
        #----------------------------------------------------

        DecreaseOfPointersToPathlets = [0]*len(self.Pathlets)
        DecreaseCounter = 0
        for i in range(len(DecreaseOfPointersToPathlets)) :
            if i in PathletsDeclined :
                DecreaseCounter = DecreaseCounter + 1
            else :
                DecreaseOfPointersToPathlets[i] = i - DecreaseCounter


        
        TrajectoriesDeclined = list(TrajectoriesDeclined)

        TrajsResultsTemp = copy.deepcopy(self.TrajsResults)
        TrajsResultsTemp = np.array(TrajsResultsTemp)

        TrajsResultsTemp = np.delete(TrajsResultsTemp, TrajectoriesDeclined,0)

        for i in range(len(TrajsResultsTemp)) :
            for j in range(len(TrajsResultsTemp[i])) :
                TrajsResultsTemp[i][j] = DecreaseOfPointersToPathlets[TrajsResultsTemp[i][j]]

        #-----------------------------------------------------

        PathletsTemp = copy.deepcopy(self.Pathlets)
        PathletsTemp = np.array(PathletsTemp)

        PathletsTemp = np.delete(PathletsTemp, PathletsDeclined,0)

        PathletsTemp.tolist()
        TrajsResultsTemp.tolist()

        PathletsTemp = list(PathletsTemp)
        TrajsResultsTemp = list(TrajsResultsTemp)

        CurrentRes = 0
        for P in PathletsTemp :
                CurrentRes = CurrentRes + len(P)
        
        for T in TrajsResultsTemp :
                CurrentRes = CurrentRes + len(T)
        for T in NormalTrajectories :
                CurrentRes = CurrentRes + len(T)

        if CurrentRes < PreviousRes :
            print("Optimization via UsePercentage is worth it. Previous:"+str(PreviousRes)+" _ Current:"+str(CurrentRes))
        else :
            print("Optimization via UsePercentage is NOT worth it. Previous:"+str(PreviousRes)+" _ Current:"+str(CurrentRes))

        implement = ""
        while not(implement == 'yes') and not(implement == 'no') :
            implement = input("Do you want to implement Optimization? yes or no: ")
            print(implement)

        if implement == 'yes' :
            self.TrajsResults = TrajsResultsTemp
            self.Pathlets = PathletsTemp
            self.NormalTrajectories = NormalTrajectories
