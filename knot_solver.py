import sys
import copy
import random

class Knot:
    def __init__(self,gauss):
        self.gauss = gauss
        self.nodes = len(gauss)
        self.unknot = False
        self.nochange = 0
        self.lastprint = str(gauss)

    def clean_gauss(self):
        #This functions cleans the gauss code after every move
        found = [0]
        missing = []
        if not self.gauss:
            #check if knot is done
            self.unknot = True
            if self.lastprint != str(self.gauss):
                print(self.gauss)
                self.lastprint = str(self.gauss)
            return None
        for element in self.gauss:
            #check if elements are in numerical order (mainly for R2 and aesthetics)
            if abs(element) == found[-1] + 1:
                found.append(abs(element))
            elif abs(element) > found[-1] + 1:
                switch = [[],[]]
                for index, element_2 in enumerate(self.gauss):
                    if abs(element_2) == abs(element):
                        switch[0].append(index)
                    if abs(element_2) == found[-1] + 1:
                        switch[1].append(index)
                if switch[1]:
                    #Switch numbers that appear "too early" in the sequence with their later occuring counterparts.
                    #This doesn't mutate the knot in any way but "renames" the overlaps.
                    next_gauss = self.gauss[:]
                    if self.gauss[switch[0][0]] * self.gauss[switch[1][0]] > 0:
                        next_gauss[switch[0][0]] = self.gauss[switch[1][0]]
                        next_gauss[switch[0][1]] = self.gauss[switch[1][1]]
                        next_gauss[switch[1][0]] = self.gauss[switch[0][0]]
                        next_gauss[switch[1][1]] = self.gauss[switch[0][1]]
                    else:
                        next_gauss[switch[0][0]] = self.gauss[switch[1][1]]
                        next_gauss[switch[0][1]] = self.gauss[switch[1][0]]
                        next_gauss[switch[1][0]] = self.gauss[switch[0][1]]
                        next_gauss[switch[1][1]] = self.gauss[switch[0][0]]
                    self.gauss = next_gauss
                    #call function again in case more have to be switched
                    self.clean_gauss()
                else:
                    for i in range(found[-1] + 1,abs(element)):
                        missing.append(i)
                found.append(abs(element))
        missing.sort(reverse=True)
        for miss in missing:
            #fill gaps by (absolutely) decreasing all numbers that are bigger than the missing ones
            for index, element in enumerate(self.gauss):
                if abs(element) > miss:
                    if element > 0:
                        self.gauss[index] -= 1
                    if element < 0:
                        self.gauss[index] += 1
        if self.gauss[0] == -1:
            #make code prettier by always having +1 at the start
            new_gauss = [-x for x in self.gauss]
            self.gauss = new_gauss
        if self.lastprint != str(self.gauss):
            print(self.gauss)
            self.lastprint = str(self.gauss)

    def reidemeister_1(self):
        #remove two nodes (a, -a) that are adjacent and part of the same overlap. Easy!
        #can even handle more of these occurences at once
        candidates = []
        for index, element in enumerate(self.gauss):
            if element == -self.gauss[(index+1)%self.nodes]:
                candidates.append(index)
                candidates.append((index+1)%self.nodes)
        candidates = sorted(list(dict.fromkeys(candidates)), reverse=True)
        if candidates:
            self.nochange = 0
            print(str(len(candidates)//2) + ' x Reidemeister I found!')
            for i in candidates:
                del self.gauss[i]
                self.nodes -= 1
        else:
            self.nochange += 1
        self.clean_gauss()

    def reidemeister_2(self):
        #remove four nodes (a, b ... [-a, -b] xor [-b, -a])
        candidates = []
        for index, element in enumerate(self.gauss):
            possible_pair = []
            if element * self.gauss[(index+1)%self.nodes] > 0:
                possible_pair = [abs(element), abs(self.gauss[(index+1)%self.nodes])]
                possible_pair.sort()
            for index_partner, element_partner in enumerate(self.gauss):
                if possible_pair == sorted([abs(element_partner), abs(self.gauss[(index_partner+1)%self.nodes])]):
                    quad = set([index, (index+1)%self.nodes, index_partner, (index_partner+1)%self.nodes])
                    if len(quad) == 4:
                        candidates = sorted(list(dict.fromkeys(quad)), reverse=True)
        if candidates:
            self.nochange = 0
            print('Reidemeister II found!')
            for i in candidates:
                del self.gauss[i]
                self.nodes -= 1
        else:
            self.nochange += 1
        self.clean_gauss()

    def reidemeister_3(self):
        #performs triangle operation on six nodes (a, b ... [-a, c] xor [c, -a] ... [-b, -c] xor [-c , -b])
        #a, b stays in place. The rest gets moved around: -a becomes c becomes -b becomes -c becomes -a
        candidates = []
        if self.nodes > 7:
            #only do this for at least 8 nodes. R1 and R2 are better for 6, 4 or 2 nodes for obvious reasons
            for index, element in enumerate(self.gauss):
                #find a and b
                if element > 0 and self.gauss[(index+1)%self.nodes] > 0:
                    candidates.append([[index,(index+1)%self.nodes],[self.gauss.index(-element)],[self.gauss.index(-self.gauss[(index+1)%self.nodes])]])
                    if self.gauss[candidates[-1][1][0]-1] == -self.gauss[candidates[-1][2][0]-1]:
                        #both c and -c appear before -a and -b in the code
                        candidates[-1][1].append(candidates[-1][1][0]-1)
                        candidates[-1][2].append(candidates[-1][2][0]-1)
                    elif self.gauss[candidates[-1][1][0]-1] == -self.gauss[(candidates[-1][2][0]+1)%self.nodes]:
                        #c appears before -a and -c appears after -b in the code
                        candidates[-1][1].append(candidates[-1][1][0]-1)
                        candidates[-1][2].append((candidates[-1][2][0]+1)%self.nodes)
                    if self.gauss[(candidates[-1][1][0]+1)%self.nodes] == -self.gauss[candidates[-1][2][0]-1]:
                        #c appears after -a and -c appears before -b in the code
                        candidates[-1][1].append((candidates[-1][1][0]+1)%self.nodes)
                        candidates[-1][2].append(candidates[-1][2][0]-1)
                    elif self.gauss[(candidates[-1][1][0]+1)%self.nodes] == -self.gauss[(candidates[-1][2][0]+1)%self.nodes]:
                        #both c and -c appear after -a and -b in the code
                        candidates[-1][1].append((candidates[-1][1][0]+1)%self.nodes)
                        candidates[-1][2].append((candidates[-1][2][0]+1)%self.nodes)
                    if len(candidates[-1][1]) == 1:
                        #no c found
                        del candidates[-1]
                    elif len(candidates[-1][1]) == 3:
                        #two different c,-c pairs found, make copy of candidate and have both versions in the candidates
                        candidates.append(copy.deepcopy(candidates[-1]))
                        del candidates[-2][1][2]
                        del candidates[-2][2][2]
                        del candidates[-1][1][1]
                        del candidates[-1][2][1]
        if candidates:
            self.nochange = 0
            #Random choice as i cant be bothered to implement some kind of intelligence here
            chosen = random.choice(candidates)
            print('1 of ' + str(len(candidates)) + ' possible Reidemeister III performed!')
            next_gauss = self.gauss[:]
            #c moves to where -a was
            next_gauss[chosen[1][0]] = self.gauss[chosen[1][1]]
            #-b moves to where c was
            next_gauss[chosen[1][1]] = self.gauss[chosen[2][0]]
            #-c moves to where -b was
            next_gauss[chosen[2][0]] = self.gauss[chosen[2][1]]
            #-a moves to where -c was
            next_gauss[chosen[2][1]] = self.gauss[chosen[1][0]]
            self.gauss = next_gauss
        else:
            self.nochange += 1
        self.clean_gauss()

knot = Knot(list(map(int, sys.argv[1].strip('[]').split(','))))
if sum(knot.gauss) != 0:
    raise ValueError('Sum of knot is not 0. Please enter the knot in basic gauss notation. (https://en.wikipedia.org/wiki/Gauss_notation)')
while not knot.unknot and knot.nochange < 2:
    while not knot.unknot and knot.nochange < 2:
        #Exhaust R1 and R2 as they are much easier to perform and have no randomness
        knot.reidemeister_1()
        knot.reidemeister_2()
    knot.reidemeister_3()

print('')
print('Result:')
print(knot.gauss)
