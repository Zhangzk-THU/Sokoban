from utils import *
from copy import deepcopy


def A_star(problem, fast=False):
    print("--------A* search---------")
    nodes = 0
    open = PriorityQueue(problem.init_state)
    closed = set()
    result = -1
    while not open.empty():
        node = open.pop()
        all_pos = deepcopy(node.state['egg_pos'])
        all_pos += (node.state['mouse_pos'])
        closed.add(tuple(all_pos))
        for child in problem.expand(node):
            nodes += 1
            child.heuristic_score = problem.heuristic_function(child.state,fast)
            all_pos = deepcopy(child.state['egg_pos'])
            all_pos+=(child.state['mouse_pos'])
            if not open.find(child) and tuple(all_pos) not in closed:
                if problem.is_goal(child.state):
                    if fast:
                        print('fast(but not optimal) solution')
                    else:
                        print('slow(but optimal) solution')
                    print('1)temporal complexity:', nodes, 'nodes generated')
                    print('2)spatial complexity:', len(open._queue), 'simultaneous nodes')
                    return problem.solution(child)
                else:
                    open.push(child)
            elif open.find(child):
                open.compare_and_replace(open.find(child), child)
    return result

