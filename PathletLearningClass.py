from pulp import *
import gc
import numpy as np
import matplotlib.pyplot as plt

class PathletLearningClass :
    def __init__(self, trajectories) :
        self.NormalTrajectories = list()
        
        self.Pathlets = list()
        self.TrajsResults = list()

        self.lamda = 0.001

        Results = dict()

        self.BestResultCounter = len(trajectories) * len(trajectories[0])
        self.BestResult = ()

        while self.lamda < 100000 :
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

            Results[self.lamda] = [PathletCounter,TrajsResultsCounter]

            if PathletCounter + TrajsResultsCounter < self.BestResultCounter :
                self.BestResult = (self.Pathlets,self.TrajsResults)

            gc.collect()
            self.lamda = self.lamda*10

        if self.BestResult is not () :
            (self.Pathlets,self.TrajsResults) = self.BestResult
        else :
            print("Pathlet Learning is not worth it cause not many common subpaths")
            self.NormalTrajectories = trajectories

        print(Results)
        print(self.Pathlets,self.TrajsResults)

    def MainFunction(self, trajectories) :
        self.Pathlets, IndexesForConstraints= self.FindAllPossiblePathlets(trajectories)

        gc.collect()

        PathletResults,self.TrajsResults = self.SolvePathletLearningLinearly(trajectories, IndexesForConstraints)
        #print(IndexesForConstraints)

        gc.collect()
        
        self.MinimizePathletLearningResults(PathletResults)
        

    def FindAllPossiblePathlets(self, trajectories) :
        print("STARTFINDPOSSIBLEPATHLETS")
        AllPossiblePathlets = []
        TrajsIndexesNeededForPathletLearning = []

        seen = dict()

        for traj in trajectories :
            trajIndexTemp = []
            for i in range(len(traj)) :
                trajIndexTemp.append([])

            for i in range(len(traj) + 1): 

                for j in range(i + 1, len(traj) + 1): 

                    sub = tuple(traj[i:j])
                    #print(sub)
                    if (sub not in seen) :
                        for k in range(i,j) :
                            trajIndexTemp[k].append(len(AllPossiblePathlets))

                        seen[sub] = len(AllPossiblePathlets)
                        AllPossiblePathlets.append(sub)
                    else :
                        #print("FINDINDEX")
                        index = seen[sub]
                        #print("FOUNDINDEX")
                        for k in range(i,j) :
                            trajIndexTemp[k].append(index)

            #print(trajIndexTemp)
            TrajsIndexesNeededForPathletLearning.append(trajIndexTemp)
            #print("FINISHED A TRAJECTORY")
     
        print("FoundAllPossiblePathlets")
        return AllPossiblePathlets, TrajsIndexesNeededForPathletLearning


    def ExistsIndexesInPathlets(self,traj,e) :
        indexes = []
        for i in range(len(self.Pathlets)) :
            flag = False
            for j in self.Pathlets[i] :
                if j not in traj :
                    flag = True
                    break

            if flag :
                continue
            if e in self.Pathlets[i] :
                indexes.append(i)
        return indexes

    def SolvePathletLearningLinearly(self,trajectories,IndexesForConstraints) :
        problem = LpProblem("PathletLearning", LpMinimize)

        Xp = LpVariable.dicts("Xp", list(range(len(self.Pathlets))), cat="Binary")

        Xtp = []
        #-------------------
        #Constraints
        print("Adding Constraints\n1st Set Of Constraints")
        for i in range(len(trajectories)) :
            Xtp.append(LpVariable.dicts("Xtp"+str(i), list(range(len(self.Pathlets))), cat="Binary"))
            
            for j in range(len(Xtp[i])) :
                problem += Xtp[i][j] <= Xp[j]

            print(i)

        print("2nd Set Of Constraints")


        #print(IndexesForConstraints)
        for i in range(len(trajectories)) :

            for j in range(len(trajectories[i])) :
                #indexes = []
                #indexes = self.ExistsIndexesInPathlets(trajectories[i],j)
                #print(len(indexes))

                temp = lpSum(Xtp[i][k] for k in IndexesForConstraints[i][j])

                problem += temp == 1

            print(i)
        #-------------------
        #objective function
        print("Adding Objective Function")
        temp = lpSum(Xp[i]  for i in range(len(Xp)))
        
        temp += lpSum(self.lamda*Xtp[i][j] for j in range(len(Xtp[i])) for i in range(len(Xtp)))

        problem += temp
        #print(problem)
        print("SolvingStarts!")

        problem.solve() #!!!

        PathletResults = []
        for i in range(len(self.Pathlets)) :
            PathletResults.append(Xp[i].varValue)
        #print(PathletResults)

        TrajsResults = []
        for i in range(len(trajectories)) :
            trajResult = []
            for j in range(len(self.Pathlets)) :
                trajResult.append(Xtp[i][j].varValue)
            TrajsResults.append(trajResult)
        #print(TrajsResults)
        
        return PathletResults,TrajsResults

    def MinimizePathletLearningResults(self,PathletResults) :
        #----------------------------------------------
        #Parakatw meiwnw to megethos twn dedomenwn mas
        indexes = []
        for i in range(len(PathletResults)) :
            if PathletResults[i] == 0 :
                indexes.append(i)

        #print("\nIndexes to Remove: ",indexes)

        self.Pathlets = np.array(self.Pathlets)
        PathletResults = np.array(PathletResults)
        self.TrajsResults = np.array(self.TrajsResults)

        self.Pathlets = list(np.delete(self.Pathlets, indexes))
        PathletResults = np.delete(PathletResults, indexes)
        self.TrajsResults = np.delete(self.TrajsResults, indexes, 1)


        NewTrajsResults = []
        for traj in self.TrajsResults :
            NewTraj = np.where(traj == 1)[0]

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

        NormalTrajectories = list()
        for i in TrajectoriesDeclined :
            NormalTrajectories.append(self.ReturnRealTraj(self.TrajsResults[i]))

        
        #----------------------------------------------------

        DecreaseOfPointersToPathlets = [0]*len(self.Pathlets)
        DecreaseCounter = 0
        for i in range(len(DecreaseOfPointersToPathlets)) :
            if i in TrajectoriesDeclined :
                DecreaseCounter = DecreaseCounter + 1
            else :
                DecreaseOfPointersToPathlets[i] = i - DecreaseCounter

        
        TrajectoriesDeclined = list(TrajectoriesDeclined)

        TrajsResults = np.array(self.TrajsResults)

        TrajsResults = np.delete(TrajsResults, TrajectoriesDeclined,0)

        for i in range(len(TrajsResults)) :
            for j in range(len(TrajsResults[i])) :
                TrajsResults[i][j] = DecreaseOfPointersToPathlets[TrajsResults[i][j]]


        #-----------------------------------------------------

        Pathlets = np.array(self.Pathlets)

        Pathlets = np.delete(Pathlets, PathletsDeclined,0)

        Pathlets.tolist()
        TrajsResults.tolist()

        Pathlets = list(Pathlets)
        TrajsResults = list(TrajsResults)

        CurrentRes = 0
        for P in Pathlets :
                CurrentRes = CurrentRes + len(P)
        
        for T in TrajsResults :
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
            self.TrajsResults = TrajsResults
            self.Pathlets = Pathlets
            self.NormalTrajectories = NormalTrajectories
        
        