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
        # Performs the triangle move on six nodes:
        # anchor positives a,b stay in place; we rotate (-a -> c -> -b -> -c -> -a)
        n = len(self.gauss)
        if n <= 7:
            self.nochange += 1
            return

        candidates = []
        seen_quads = set()

        for i in range(n):
            a = self.gauss[i]
            b = self.gauss[(i + 1) % n]
            # find anchors: two adjacent positives
            if a <= 0 or b <= 0:
                continue

            ia = self.gauss.index(-a)       # index of -a
            ib = self.gauss.index(-b)       # index of -b

            # neighbors around -a and -b (circular)
            la, ra = (ia - 1) % n, (ia + 1) % n
            lb, rb = (ib - 1) % n, (ib + 1) % n

            # Four possible layouts:
            # [-a, c] & [-b, -c] ; [-a, c] & [-c, -b] ; [c, -a] & [-b, -c] ; [c, -a] & [-c, -b]
            for c_idx, mc_idx in ((ra, rb), (ra, lb), (la, rb), (la, lb)):
                c_val  = self.gauss[c_idx]
                mc_val = self.gauss[mc_idx]

                # must be opposite, and c must be distinct from a,b
                if c_val == -mc_val and abs(c_val) not in (abs(a), abs(b)):
                    quad = (ia, c_idx, ib, mc_idx)
                    if len(set(quad)) == 4:
                        key = tuple(sorted(quad))
                        if key not in seen_quads:
                            seen_quads.add(key)
                            candidates.append(quad)

        if candidates:
            self.nochange = 0
            ia, ic, ib, imc = random.choice(candidates)
            print(f"1 of {len(candidates)} possible Reidemeister III performed!")

            # 4-cycle: (-a) <- c <- (-b) <- (-c) <- (-a)
            tmp = self.gauss[ia]
            self.gauss[ia]  = self.gauss[ic]
            self.gauss[ic]  = self.gauss[ib]
            self.gauss[ib]  = self.gauss[imc]
            self.gauss[imc] = tmp
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
