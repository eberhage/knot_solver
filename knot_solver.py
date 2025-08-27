import sys
import copy
import random

class Knot:
    def __init__(self,gauss):
        self.gauss = gauss
        self.unknot = False
        self.nochange = 0
        self.lastprint = str(gauss)

    def clean_gauss(self):
        #This functions cleans the gauss code after every move
        if not self.gauss:
            self.unknot = True
            if self.lastprint != str(self.gauss):
                print(self.gauss)
                self.lastprint = str(self.gauss)
            return

        # Repeat until no more swaps / renumberings are needed.
        while True:
            made_change = False
            found = [0]
            missing = []

            # iterate by index to avoid iterator invalidation if self.gauss changes
            for idx in range(len(self.gauss)):
                element = self.gauss[idx]
                if abs(element) == found[-1] + 1:
                    found.append(abs(element))
                elif abs(element) > found[-1] + 1:
                    # find positions of this element and the "expected" next number
                    switch = [[], []]
                    for j, elem_j in enumerate(self.gauss):
                        if abs(elem_j) == abs(element):
                            switch[0].append(j)
                        if abs(elem_j) == found[-1] + 1:
                            switch[1].append(j)

                    if switch[1]:
                        # perform the swap/rename and restart the outer while loop
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
                        made_change = True
                        break      # restart scanning from the top

                    else:
                        for missing_num in range(found[-1] + 1, abs(element)):
                            missing.append(missing_num)

                    found.append(abs(element))

            if made_change:
                continue  # re-scan after rename/swap

            # apply missing-number compression (decrease labels above gaps)
            if missing:
                missing.sort(reverse=True)
                for miss in missing:
                    for index, element in enumerate(self.gauss):
                        if abs(element) > miss:
                            self.gauss[index] = element - 1 if element > 0 else element + 1
                # after renumbering, re-scan to catch any newly-exposed renames
                continue

            # prettify: prefer +1 at start (only if list non-empty)
            if self.gauss and self.gauss[0] == -1:
                self.gauss = [-x for x in self.gauss]

            # print only when changed
            if self.lastprint != str(self.gauss):
                print(self.gauss)
                self.lastprint = str(self.gauss)

            break  # stable, exit

    def reidemeister_1(self):
        #remove two nodes (a, -a) that are adjacent and part of the same overlap. Easy!
        #can even handle more of these occurences at once
        n = len(self.gauss)
        if n == 0:
            self.nochange += 1
            return

        candidates = [i for i in range(n) if self.gauss[i] == -self.gauss[(i + 1) % n]]

        if not candidates:
            self.nochange += 1
            return

        self.nochange = 0
        # build delete set from original indices (safe), then delete in reverse order
        original_len = n
        to_delete = set(candidates) | { (i + 1) % original_len for i in candidates }
        indices_to_delete = sorted(to_delete, reverse=True)

        print(f"{len(indices_to_delete)//2} x Reidemeister I found!")
        for idx in indices_to_delete:
            del self.gauss[idx]

        # now do a safe clean
        self.clean_gauss()

    def reidemeister_2(self):
        #remove four nodes (a, b ... [-a, -b] xor [-b, -a])
        n = len(self.gauss)
        if n < 4:
            self.nochange += 1
            return

        pair_map = {}  # maps (a,b) → list of start indices
        for i in range(n):
            a, b = self.gauss[i], self.gauss[(i + 1) % n]
            if a * b > 0:  # both same sign → possible R2
                key = tuple(sorted((abs(a), abs(b))))
                pair_map.setdefault(key, []).append(i)

        candidates = None
        for (a, b), starts in pair_map.items():
            if len(starts) >= 2:
                # check distinct quads
                for i in range(len(starts)):
                    for j in range(i + 1, len(starts)):
                        quad = {starts[i], (starts[i] + 1) % n,
                                starts[j], (starts[j] + 1) % n}
                        if len(quad) == 4:  # valid distinct 4 nodes
                            candidates = sorted(quad, reverse=True)
                            break
                    if candidates:
                        break
            if candidates:
                break

        if candidates:
            self.nochange = 0
            print("Reidemeister II found!")
            for idx in candidates:
                del self.gauss[idx]
            self.clean_gauss()
        else:
            self.nochange += 1

    def reidemeister_3(self):
        #performs triangle operation on six nodes (a, b ... [-a, c] xor [c, -a] ... [-b, -c] xor [-c , -b])
        #a, b stays in place. The rest gets moved around: -a becomes c becomes -b becomes -c becomes -a
        candidates = []
        n = len(self.gauss)
        if n > 7:
            #only do this for at least 8 nodes. R1 and R2 are better for 6, 4 or 2 nodes for obvious reasons
            for index, element in enumerate(self.gauss):
                #find a and b
                if element > 0 and self.gauss[(index+1)%n] > 0:
                    candidates.append([[index,(index+1)%n],[self.gauss.index(-element)],[self.gauss.index(-self.gauss[(index+1)%n])]])
                    if self.gauss[candidates[-1][1][0]-1] == -self.gauss[candidates[-1][2][0]-1]:
                        #both c and -c appear before -a and -b in the code
                        candidates[-1][1].append(candidates[-1][1][0]-1)
                        candidates[-1][2].append(candidates[-1][2][0]-1)
                    elif self.gauss[candidates[-1][1][0]-1] == -self.gauss[(candidates[-1][2][0]+1)%n]:
                        #c appears before -a and -c appears after -b in the code
                        candidates[-1][1].append(candidates[-1][1][0]-1)
                        candidates[-1][2].append((candidates[-1][2][0]+1)%n)
                    if self.gauss[(candidates[-1][1][0]+1)%n] == -self.gauss[candidates[-1][2][0]-1]:
                        #c appears after -a and -c appears before -b in the code
                        candidates[-1][1].append((candidates[-1][1][0]+1)%n)
                        candidates[-1][2].append(candidates[-1][2][0]-1)
                    elif self.gauss[(candidates[-1][1][0]+1)%n] == -self.gauss[(candidates[-1][2][0]+1)%n]:
                        #both c and -c appear after -a and -b in the code
                        candidates[-1][1].append((candidates[-1][1][0]+1)%n)
                        candidates[-1][2].append((candidates[-1][2][0]+1)%n)
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
