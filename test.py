from problem import Maze
from search import *
import numpy as np
import time

if __name__ == "__main__":
    # a toy example to prove that the penalizing each egg not in goal does not ensure best solution
    test_map = np.array([[-9, -9, -9, -9, -9, -9, -9, -9, -9, -9],
                    [-9, -9, 0, 0, 0, 0, 0, -9, -9, -9],
                    [-9, -9, 0, -9, -9, -9, 0, 0, 0, -9],
                    [-9, 0, 0, 0, 0, 0, 0, 0, 0, -9],
                    [-9, 0, 0, 0, -9, 0, 0, 0, 0, -9],
                    [-9, -9, 0, 0, -9, 0, 0, 0, 0, -9],
                    [-9, -9, -9, -9, -9, -9, -9, -9, -9, -9]])
    newgame = Maze({'egg_pos': [(3, 6), (3, 7), (3, 4)], 'mouse_pos': [3, 1]},
                   {'egg_pos': [(4, 2), (4, 3), (5, 2)], 'mouse_pos': []}, test_map, False)
    time1 = time.time()
    result_false = A_star(newgame, fast=True)
    time2 = time.time()
    print("search time(FAST):", time2 - time1)
    print('pushes=', result_false[-1].path_cost if result_false else "no solution", ', steps=', len(result_false) if result_false else "no solution")
    result = A_star(newgame, fast=False)
    time3 = time.time()
    print("search time(SLOW):", time3 - time2)
    # print('cost=', result)
    print('pushed=', result[-1].path_cost if result else "no solution", ', steps=', len(result) if result else "no solution")

    if result[-1].path_cost != result_false[-1].path_cost:
        print("error!!!")
