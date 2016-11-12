import sys
import os
import random
import time

class IntervalSetCoverGenerator:

   def generate(self, start, end, numSubSets):
      s1 = numSubSets/2
      s2 = numSubSets - s1
      mincover = (end - start + 1) / numSubSets 
      (U, S1) = self.__generate__(start, end, s1)
      (_, S2) = self.__generate__(start + mincover - 1, end - mincover - 1, s2) 
      return (U, S1+S2)

   def __generate__(self, start, end, numSubSets):
      if start < 0 or end <= 0 or start >= end or numSubSets <= 0: raise Exception("Invalid arguments")
      if end - start < numSubSets: raise Exception("Too many subset requested") 
      mincover = (end - start + 1) / numSubSets 
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

    def __getStart__(self, subInterval):
        return subInterval[0]

    def __getEnd__(self, subInterval):
        return subInterval[1]

    #repeatly select the largest sub interval that covers the leftmost uncovered points
    def greedy(self):
        cover = []
        uncoveredInterval = self.I
        subsets = self.S
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

    def RandomizedLinearProgrammingRelaxiation(self):


if __name__ == '__main__':
   g = IntervalSetCoverGenerator()
   (I, S) = g.generate(0, 1000000, 10000)
   print 'Universe Interval = %s' % (I,)
   print 'Number of Sub-intervals = %d' % len(S)

   begin = time.time()
   solver = IntervalSetCoverSolver(I, S)
   c = solver.greedy()
   end = time.time()
   print 'greedy alogrithm find optimal cover size %d in %.3f secs' % (len(c), end - begin)

