import random
import math

class YuleDistr(object):

    def __init__(self):
        pass

    @staticmethod
    def normalizeFreqs(freqs):
        res = []
        for i in range(0, len(freqs)):
            if i == 0:
                res.append(freqs[i])
            else:
                res.append(res[i-1]+freqs[i])
        return res

    @staticmethod
    def randomGen(freqs):
        temp = normalizeFreqs(freqs)
        if temp[len(temp)-1] >= 1:
            return -1
        else:
            num = random.random()
            for i in range(0, len(temp)+1):
                if i == 0 and num < temp[i]:
                    return i
                elif i == len(temp) and num >= temp[i-1]:
                    return i
                elif num >= temp[i-1] and num < temp[i]:
                    return i

    @staticmethod
    def borodProb(num, rank):
        if rank < 1 or num < 1:
            return -1
        else:
            return (1/num)*(math.log(num+1)-math.log(rank))


#test 1 +++
s = [0.1, 0.01]
#print(normalizeFreqs(s))


#test 2
"""for i in range(0, 100):
    k = randomGen(s)
    if i%10 < 9:
        print(str(k), end=" ")
    else:
        print(str(k))"""

#test 3

for i in range(1, 21):
    print(borodProb(20,i))
    

