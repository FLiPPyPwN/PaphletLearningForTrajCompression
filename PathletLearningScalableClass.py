from pulp import *
class PathletLearningScalableClass :
    def __init__(self, trajectories) :
        self.NumOfTrajs = len(trajectories)

        self.Pathlets,TpIndexesNeededForPathletLearning,SubIndexesNeededForPathletLearning= self.FindAllPossiblePathlets(trajectories)
        print(self.Pathlets,"\n\n",SubIndexesNeededForPathletLearning)
        self.Xp = [0]*len(self.Pathlets)
        self.TrajsResults = list()
        for i in range(len(trajectories)) :
            self.TrajsResults.append(self.SolvePathletLearningScalableLinearly(i,TpIndexesNeededForPathletLearning,SubIndexesNeededForPathletLearning))

        self.MinimizePathletLearningResults(self.Xp)


    def FindAllPossiblePathlets(self, trajectories) :
        print("STARTFINDPOSSIBLEPATHLETS")
        AllPossiblePathlets = []
        TpIndexesNeededForPathletLearning = []
        SubIndexesNeededForPathletLearning = []

        seenSet = set()
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
                    if (sub not in seenSet) :
                        for k in range(i,j) :
                            trajIndexTemp[k].append(len(AllPossiblePathlets))

                        TpIndexesNeededForPathletLearning.append([trajCounter])
                        seen[sub] = len(AllPossiblePathlets)
                        AllPossiblePathlets.append(sub)
                        seenSet.add(sub)
                    else :
                        index = seen[sub]
                        TpIndexesNeededForPathletLearning[index].append(trajCounter)

                        for k in range(i,j) :
                            trajIndexTemp[k].append(index)

            trajCounter = trajCounter + 1
            SubIndexesNeededForPathletLearning.append(trajIndexTemp)

        print("FoundAllPossiblePathlets")
        return AllPossiblePathlets, TpIndexesNeededForPathletLearning,SubIndexesNeededForPathletLearning
                

    def SolvePathletLearningScalableLinearly(self,trajIndex,TpIndexesNeededForPathletLearning,SubIndexesNeededForPathletLearning) :
        problem = LpProblem("PathletLearning", LpMinimize)

        #-------------------
        #Constraints
        print("Adding Set Of Constraints")
        Xtp = LpVariable.dicts("Xtp"+str(trajIndex), list(range(len(self.Pathlets))), cat="Binary")

        PathletsUsing = set()
        for indexes in SubIndexesNeededForPathletLearning[trajIndex] :
            temp = 0
            for index in indexes :
                PathletsUsing.add(index)
                temp += Xtp[index]
            
            problem += temp == 1

        print("Adding Objective Function")
        temp = 0
        l = 1
        for i in PathletsUsing :
            AbsoluteTp = len(TpIndexesNeededForPathletLearning[i])
            temp += (l + 1/AbsoluteTp)*Xtp[i]

        problem += temp

        print("DONE WITH CONSTRAINTS && OBJECTIVE FUNCTION")
        #print(problem)
        

        print("SolvingStarts!")
        problem.solve() #!!!

        trajResults = []
        
        for i in range(len(self.Pathlets)) :
            if i not in PathletsUsing :
                trajResults.append(0)
            else :
                trajResults.append(Xtp[i].varValue)
            
            if trajResults[i] == 1 :
                self.Xp[i] = 1

        #print(trajResults)
        return trajResults

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
            counter = 1
            currentValue = traj[0]
            for i in traj[1:] :
                if currentValue == i :
                    counter = counter + 1
                else :
                    NewTraj.append((int(currentValue),counter))
                    counter = 1
                    currentValue = i
            NewTraj.append((int(currentValue),counter))
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
        TotalTimes = 0
        for i in range(len(TrajResult)) :
            (Value,times) = TrajResult[i]
            if Value == 1 :
                for j in range(times) :
                    RealTraj = self.ReturnPartRealTraj(RealTraj,self.Pathlets[TotalTimes + j])

            TotalTimes = TotalTimes + times

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