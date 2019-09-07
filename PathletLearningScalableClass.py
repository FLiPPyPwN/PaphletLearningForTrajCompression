from pulp import *
import gc
import numpy as np
import matplotlib.pyplot as plt
import copy
from itertools import permutations

class PathletLearningScalableClass :
    def __init__(self, trajectories = [], l = -1) :
        if not trajectories :
            self.TrajsResults = []
            self.Pathlets = []
            return
            
        RealTrajListCounter = 0
        for T in trajectories :
                RealTrajListCounter = RealTrajListCounter + len(T)


        #if optimized with percentage of use
        self.NormalTrajectories = list()

        self.Pathlets = list()
        self.Xp = list()
        self.TrajsResults = list()

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

        print(Results)
        print(self.Pathlets,self.TrajsResults)

        
    def MainFunction(self, trajectories) :
        self.Pathlets,TpIndexesNeededForPathletLearning,SubIndexesNeededForPathletLearning= self.FindAllPossiblePathlets(trajectories)
        self.Xp = [0]*len(self.Pathlets)

        gc.collect()

        self.TrajsResults = list()
        for i in range(len(trajectories)) :
            self.TrajsResults.append(self.SolvePathletLearningScalableLinearly(i,TpIndexesNeededForPathletLearning,SubIndexesNeededForPathletLearning))

        self.MinimizePathletLearningResults(self.Xp,trajectories)
        


    def FindAllPossiblePathlets(self, trajectories) :
        AllPossiblePathlets = []
        TpIndexesNeededForPathletLearning = []
        SubIndexesNeededForPathletLearning = []

        seen = dict()

        trajCounter = 0
        for traj in trajectories :
            trajIndexTemp = []
            for i in range(len(traj)) :
                trajIndexTemp.append([])

            for i in range(len(traj) + 1): 

                for j in range(i + 1, len(traj) + 1): 

                    sub = tuple(traj[i:j])
                    if (sub not in seen) :
                        for k in range(i,j) :
                            trajIndexTemp[k].append(len(AllPossiblePathlets))

                        TpIndexesNeededForPathletLearning.append(1)
                        seen[sub] = len(AllPossiblePathlets)
                        AllPossiblePathlets.append(sub)
                    else :
                        index = seen[sub]
                        TpIndexesNeededForPathletLearning[index] = TpIndexesNeededForPathletLearning[index] + 1

                        for k in range(i,j) :
                            trajIndexTemp[k].append(index)

            trajCounter = trajCounter + 1
            SubIndexesNeededForPathletLearning.append(trajIndexTemp)

        return AllPossiblePathlets, TpIndexesNeededForPathletLearning,SubIndexesNeededForPathletLearning
                

    def SolvePathletLearningScalableLinearly(self,trajIndex,TpIndexesNeededForPathletLearning,SubIndexesNeededForPathletLearning) :
        problem = LpProblem("PathletLearning", LpMinimize)

        #-------------------
        #Constraints
        Xtp = LpVariable.dicts("Xtp"+str(trajIndex), list(range(len(self.Pathlets))), cat="Binary")

        PathletsUsing = set()
        for indexes in SubIndexesNeededForPathletLearning[trajIndex] :
            PathletsUsing.update(indexes)

            temp = lpSum(Xtp[index]  for index in indexes)
            
            problem += temp == 1

        temp = lpSum((self.lamda + 1/TpIndexesNeededForPathletLearning[i])*Xtp[i]  for i in PathletsUsing)

        problem += temp

        problem.solve() #!!!

        trajResults = []
        
        for i in range(len(self.Pathlets)) :
            if i not in PathletsUsing :
                trajResults.append(0)
            else :
                trajResults.append(Xtp[i].varValue)
            
            if trajResults[i] == 1 :
                self.Xp[i] = 1

        return trajResults

    def MinimizePathletLearningResults(self,PathletResults,trajectories) :
        #----------------------------------------------
        #Parakatw meiwnw to megethos twn dedomenwn mas
        indexes = []
        for i in range(len(PathletResults)) :
            if PathletResults[i] == 0 :
                indexes.append(i)


        self.Pathlets = np.array(self.Pathlets)
        PathletResults = np.array(PathletResults)
        self.TrajsResults = np.array(self.TrajsResults)

        self.Pathlets = list(np.delete(self.Pathlets, indexes))
        PathletResults = np.delete(PathletResults, indexes)
        self.TrajsResults = np.delete(self.TrajsResults, indexes, 1)
        


        NewTrajsResults = []
        for i in range(len(self.TrajsResults)) :
            NewTraj = np.where(self.TrajsResults[i] == 1)[0]

            #Swsth topothethsh twn index sta Pathlets
            if not(self.ReturnRealTraj(NewTraj) == trajectories[i]) :
                for PossibleOrder in list(permutations(NewTraj, len(NewTraj))) :
                    if self.ReturnRealTraj(PossibleOrder) == trajectories[i] :
                        NewTraj = PossibleOrder
                        break

                NewTrajsResults.append(list(NewTraj))
            else :
                NewTrajsResults.append(NewTraj.tolist())


        self.TrajsResults = NewTrajsResults

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

    #Cant work if used UsagePercentageOptimization
    def ReturnSpecificTrajectoryByIndex(self, index) :
        if index > len(self.TrajsResults) - 1 or index < 0:
            print("There are",len(self.TrajsResults),"trajectories but you asked for the",index)
        else :
            return self.ReturnRealTraj(self.TrajsResults[index])

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

        self.FindAndAskForPercentageOptimization(PathletsDeclined,TrajectoriesDeclined)

        

    def FindAndAskForPercentageOptimization(self,PathletsDeclined,TrajectoriesDeclined) :
        PreviousRes = 0 #Check if Optimization worth it
        for P in self.Pathlets :
                PreviousRes = PreviousRes + len(P)
        for T in self.TrajsResults :
                PreviousRes = PreviousRes + len(T)

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
        PathletsTemp = list(PathletsTemp)
        TrajsResultsTemp.tolist()
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
        