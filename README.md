# knot_solver.py
This script takes a knot in gauss notation as input (see https://en.wikipedia.org/wiki/Gauss_notation) and tries to simplify it using Reidemeister moves (https://en.wikipedia.org/wiki/Reidemeister_move). "[]" means, it found the unknot (https://en.wikipedia.org/wiki/Unknot). It can only solve "easy" knots, though.

## Usage
```
python3 knot_solver.py [1,-2,-3,4,5,6,-7,8,-9,-10,11,12,13,7,-8,-13,-12,9,14,-5,2,-1,-6,-14,-15,3,-4,15,10,-11]
```

## Output
```
Reidemeister II found!
[1, -2, -3, 4, 5, 6, -7, 8, -9, -10, 11, 7, -8, 9, 12, -5, 2, -1, -6, -12, -13, 3, -4, 13, 10, -11]
1 of 1 possible Reidemeister III performed!
[1, -2, -3, 4, 5, 6, -7, 8, -9, -10, 11, 7, -8, 9, -6, 12, 2, -1, -12, -5, -13, 3, -4, 13, 10, -11]
1 of 3 possible Reidemeister III performed!
[1, -2, 3, -4, -5, -6, 7, -8, 9, 10, -11, -7, 8, -9, 6, -1, -12, 12, 2, 5, 13, -3, 4, -13, -10, 11]
1 x Reidemeister I found!
[1, -2, 3, -4, -5, -6, 7, -8, 9, 10, -11, -7, 8, -9, 6, -1, 2, 5, 12, -3, 4, -12, -10, 11]
1 of 1 possible Reidemeister III performed!
[1, -2, 3, -4, -5, -6, 7, -8, 9, 10, -11, -7, 8, -9, 6, -1, 2, 12, 4, -3, -12, 5, -10, 11]
1 of 3 possible Reidemeister III performed!
[1, 2, -3, -4, -5, -6, 7, -8, 9, 10, -11, -7, 8, -9, 6, -1, 12, 3, 4, -12, -2, 5, -10, 11]
Reidemeister II found!
[1, 2, -3, -4, 5, -6, 7, 8, -9, -5, 6, -7, 4, -1, 10, -10, -2, 3, -8, 9]
1 x Reidemeister I found!
[1, 2, -3, -4, 5, -6, 7, 8, -9, -5, 6, -7, 4, -1, -2, 3, -8, 9]
Reidemeister II found!
[1, 2, -3, 4, -5, -6, 7, 3, -4, 5, -2, -1, 6, -7]
Reidemeister II found!
[1, -2, 3, 4, -5, -1, 2, -3, -4, 5]
Reidemeister II found!
[1, -2, -3, -1, 2, 3]
Reidemeister II found!
[1, -1]
1 x Reidemeister I found!
[]

Result:
[]
```

## Example for a knot it cannot solve
```
python3 knot_solver.py [-1,2,-3,4,-5,3,-6,-7,-2,1,-8,9,-10,6,-4,5,7,8,-9,10]
```

Output:
```
Result:
[1, -2, 3, -4, 5, -3, 6, 7, 2, -1, 8, -9, 10, -6, 4, -5, -7, -8, 9, -10]
```

Making small adjustments to the knot (still the same knot!):
```
python3 knot_solver.py [-1,-2,3,-4,2,1,-5,6,-7,-3,4,5,-6,7]
```

Output:
```
[1, 2, -3, 4, -2, -1, 5, -6, 7, 3, -4, -5, 6, -7]
Reidemeister II found!
[1, -2, -3, 4, -5, -1, 2, 3, -4, 5]
Reidemeister II found!
[1, 2, -3, -1, -2, 3]
Reidemeister II found!
[1, -1]
1 x Reidemeister I found!
[]

Result:
[]
```
