import sys
import os
import random
import time
from pulp import *

class IntervalSetCoverGenerator:

   def generate(self, start, end, numSubSets):
      s1 = numSubSets/2
      s2 = numSubSets - s1
      mincover = int((end - start + 1) / numSubSets) 
      (U, S1) = self.__generate__(start, end, s1)
      (_, S2) = self.__generate__(start + mincover - 1, end - mincover - 1, s2) 
      return (U, S1+S2)

   def __generate__(self, start, end, numSubSets):
      if start < 0 or end <= 0 or start >= end or numSubSets <= 0: raise Exception("Invalid arguments")
      if end - start < numSubSets: raise Exception("Too many subset requested") 
      mincover = int((end - start + 1) / numSubSets) 
      subset = []
      setStart = start
      while True:
         minEnd = setStart + mincover
         maxEnd = setStart + mincover + mincover
         if maxEnd > end: maxEnd = end
         setEnd = random.randint(minEnd, maxEnd)
         subset.append((setStart,setEnd))
         setStart += mincover
         if maxEnd == end: 
            subset.append((setStart, maxEnd))
            break
      universe = (start, end)
      return (universe, subset)

class IntervalSetCoverSolver:

    def __init__(self, universeInterval, subIntervals):
        self.I = universeInterval
        self.S = sorted(subIntervals, key=self.__getStart__) #sort sub-interval by end point 
        self.prob = None

    def __getStart__(self, subInterval):
        return subInterval[0]

    def __getEnd__(self, subInterval):
        return subInterval[1]

    #repeatly select the largest sub interval that covers the leftmost uncovered point
    def greedy(self):
        cover = []
        uncoveredInterval = self.I
        subsets = self.S[:]
        while uncoveredInterval[0] <= uncoveredInterval[1]: #there is still uncovered elements 
            leftmost = uncoveredInterval[0]
            largestS = None
            numSetCovered = 0 #number of subset covered the leftmost
            for s in subsets:
                if s[0] > leftmost: break # self.S is sorted
                if s[1] >= leftmost:
                    numSetCovered += 1
                    if largestS == None or s[1] > largestS[1]:
                        largestS = s
            if largestS == None:
                raise Exception("No subset cover point %s" % leftmost)

            cover.append(largestS)
            uncoveredInterval = (largestS[1] + 1, uncoveredInterval[1])
            subsets = subsets[numSetCovered:]

        return cover

    def solveSetCoverLpRelaxiation(self):
        begin = time.time()
        self.LpVars = []
        i = 0
        for s in self.S:
            xi = LpVariable('x%d' % i, lowBound=0, upBound=1, cat='Continuous') #LP relaxation to continuous variable
            self.LpVars.append(xi)
            i += 1
        self.prob = LpProblem('SetCoverLpProblem', LpMinimize)
        self.prob += sum(self.LpVars) #objective function = sum of all LP Vars

        #set up LP constraints
        subsets = self.S[:]
        allVars = self.LpVars[:]
        for element in range(self.I[0], self.I[1]+1):
            i = 0
            constraint = []
            toRemoveSubsets = []
            toRemoveLpVars = []
            for s in subsets:
                if s[0] > element: break
                if s[1] >= element:
                    constraint.append(allVars[i]) #this Lp var represents subset cover "element"
                else:
                    toRemoveSubsets.append(s)
                    toRemoveLpVars.append(allVars[i])
                i += 1
            self.prob += sum(constraint) >= 1 #element need to be covered by at least one subset
            
            #remove un-needed subset & corresponding lp vars
            for s in toRemoveSubsets:
                subsets.remove(s)
            for v in toRemoveLpVars:
                allVars.remove(v)

        end = time.time()
        print("set up LP takes %.3f secs" % (end-begin,))
        status = self.prob.solve()
        print("solved %s solution LP relaxation in %.3f secs" % (LpStatus[status], time.time() - end))

    def findCoverFromRandomPick(self):
        if self.prob == None:
            raise Exception("Set Cover LP relaxation hasn't been set up and solved yet!")
        
        #pick the subset
        coveredInterval = None
        cover = []
        subsets = self.S[:]
        allVars = self.LpVars[:]
        while True:
            if coveredInterval == self.I: break #all elements covered
            if len(subsets) == 0: raise Exception("not all elemented covered by at least one subsets")

            i = 0
            toRemoveSubsets = []
            toRemoveLpVars = []
            for lpVar in allVars:
                p = value(lpVar) #treat it as probability
                rn = random.random()
                if p > rn: 
                    s = subsets[i]
                    if coveredInterval == None: coveredInterval = s
                    else:
                        left = coveredInterval[0]
                        right = coveredInterval[1]
                        if s[0] < left: left = s[0]
                        if s[1] > right: right = s[1]
                        coveredInterval = (left, right)
                    cover.append(s)
                    toRemoveSubsets.append(s)
                    toRemoveLpVars.append(lpVar)
                i += 1

            #remove selected subset & corresponding lp var
            for s in toRemoveSubsets:
                subsets.remove(s)
            for v in toRemoveLpVars:
                allVars.remove(v)
        return cover

    def checkCover(self, I, C):
       covered = None
       for c in C:
         if covered == None: covered = c
         left = c[0]
         right = c[1]
         if left < covered[0]: covered = (left, covered[1])
         if right > covered[1]: covered = (covered[0], right)
       if I != covered: raise Exception("Input cover does not cover all elements in the universe, I = %s, covered = %s" % (I, covered))

if __name__ == '__main__':
   print ('----------------------------------------------------')
   g = IntervalSetCoverGenerator()
   (I, S) = g.generate(0, 10000, 1000)
   print ('Universe Interval = %s' % (I,))
   print ('Number of Sub-intervals = %d' % len(S))
   print ('----------------------------------------------------')

   begin = time.time()
   solver = IntervalSetCoverSolver(I, S)
   opt = solver.greedy()
   end = time.time()
   solver.checkCover(I, opt)  
   print ('greedy alogrithm find optimal cover size %d in %.3f secs' % (len(opt), end - begin))
   print ('----------------------------------------------------')

   begin = time.time()
   solver = IntervalSetCoverSolver(I, S)
   solver.solveSetCoverLpRelaxiation()
   end = time.time()

   numTrails = 1
   tolSize = 0
   print("running random pick from LP relaxation for %d times" % numTrails)
   for i in range(0, numTrails):
       c = solver.findCoverFromRandomPick()
       tolSize += len(c)
   avgSize = int(tolSize/numTrails)
   avgTime = (time.time() - end)/numTrails
   solver.checkCover(I, c)  

   print ('LP relaxation random pick find average sub-optimal cover size %d in %.3f secs, total %.3f secs' % (avgSize, avgTime, end - begin + avgTime))
   print ('LP relaxation random pick calculated approximation ratio = %.3f' % (float(avgSize)/len(opt), ))

