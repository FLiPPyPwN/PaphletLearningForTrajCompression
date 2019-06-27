from pulp import *
class PathletLearningClass :
    def __init__(self, trajectories) :
        self.Pathlets = self.FindAllPossiblePathlets(trajectories)
        #print(self.Pathlets)

        PathletResults,self.TrajsResults = self.SolvePathletLearningLinearly(trajectories)
        self.MinimizePathletLearningResults(PathletResults)

        #print("\nAAA\n",self.Pathlets,self.TrajsResults)
        

    def FindAllPossiblePathlets(self, trajectories) :
        AllPossiblePathlets = []
        for traj in trajectories :
            for PathletLength in range(1,len(traj) + 1) :
                for i in range(0,len(traj)) :

                    temp = []
                    temp.append(traj[i])
                    for j in range(i + 1, i + PathletLength) :
                        if (j < len(traj)) :
                            temp.append(traj[j])
                    
                    if (len(temp) == PathletLength and temp not in AllPossiblePathlets) :
                        AllPossiblePathlets.append(temp)

        return AllPossiblePathlets


    def ExistsIndexesInPathlets(self, AllPossiblePathlets,traj,e) :
        indexes = []
        for i in range(len(AllPossiblePathlets)) :
            flag = False
            for j in AllPossiblePathlets[i] :
                if j not in traj :
                    flag = True
                    break

            if flag :
                continue
            if e in AllPossiblePathlets[i] :
                indexes.append(i)

        return indexes

    def SolvePathletLearningLinearly(self,trajectories) :
        problem = LpProblem("PathletLearning", LpMinimize)

        Xp = LpVariable.dicts("Xp", list(range(len(self.Pathlets))), cat="Binary")

        Xtp = []
        #-------------------
        #Constraints
        for i in range(len(trajectories)) :
            Xtp.append(LpVariable.dicts("Xtp"+str(i), list(range(len(self.Pathlets))), cat="Binary"))
            
            for j in range(len(Xtp[i])) :
                problem += Xtp[i][j] <= Xp[j]

        for i in range(len(trajectories)) :

            for j in trajectories[i] :
                indexes = []
                indexes = self.ExistsIndexesInPathlets(self.Pathlets,trajectories[i],j)

                temp = 0
                for k in indexes :
                    temp += Xtp[i][k]

                problem += temp == 1
        #-------------------
        #objective function
        temp = 0
        for i in range(len(Xp)) :
            temp += Xp[i]

        l = 1; #lamda
        for i in range(len(Xtp)) :
            for j in range(len(Xtp[i])) :
                temp += l*Xtp[i][j]

        problem += temp
        #print(problem)
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

    def ReturnRealTraj(self, PathletDic,TrajResult) :
        RealTraj = []
        TotalTimes = 0
        for i in range(len(TrajResult)) :
            (Value,times) = TrajResult[i]
            if Value == 1 :
                for j in range(times) :
                    RealTraj = self.ReturnPartRealTraj(RealTraj,PathletDic[TotalTimes + j])

            TotalTimes = TotalTimes + times

        return RealTraj

    def ReturnAllTrajsInAList(self) :
        RealTrajs = []
        for i in range(len(self.TrajsResults)) :
            RealTrajs.append(self.ReturnRealTraj(self.Pathlets,self.TrajsResults[i]))

        return RealTrajs