import sys
import os
import random

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




if __name__ == '__main__':
   g = IntervalSetCoverGenerator()
   (I, S) = g.generate(0, 100000, 1000)
   print 'I = %s, S = %s' % (I, S)
