from pulp import *
import gc
import numpy as np

class PathletLearningScalableClass :
    def __init__(self, trajectories) :

        self.Pathlets,TpIndexesNeededForPathletLearning,SubIndexesNeededForPathletLearning= self.FindAllPossiblePathlets(trajectories)
        self.Xp = [0]*len(self.Pathlets)

        gc.collect()

        self.TrajsResults = list()
        for i in range(len(trajectories)) :
            print(i)
            self.TrajsResults.append(self.SolvePathletLearningScalableLinearly(i,TpIndexesNeededForPathletLearning,SubIndexesNeededForPathletLearning))

        self.MinimizePathletLearningResults(self.Xp)
        


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
                    #print(sub)
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
            temp = 0
            for index in indexes :
                PathletsUsing.add(index)
                temp += Xtp[index]
            
            problem += temp == 1

        temp = 0
        l = 0.001
        for i in PathletsUsing :
            AbsoluteTp = TpIndexesNeededForPathletLearning[i]
            temp += (l + 1/AbsoluteTp)*Xtp[i]

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
        print(self.TrajsResults)

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
        if index > len(self.TrajsResults) - 1 or index < 0:
            print("There are",len(self.TrajsResults),"trajectories but you asked for the",index)
        else :
            return self.ReturnRealTraj(self.TrajsResults[index])