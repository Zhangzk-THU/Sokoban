import numpy as np
import math
from copy import deepcopy

WALL = -9


class Node(object):  # Represents a node in a search tree
    def __init__(self, state, parent=None, action=None, path_cost=0):
        self.state = state
        self.parent = parent
        # self.action = action  # Node.action is redundant since we have Node.parent
        self.path_cost = path_cost
        self.heuristic_score = 0  # heuristic function of each node, should be updated whenever a node is generated
        self.depth = 0
        if parent:
            self.depth = parent.depth + 1

    def child_node(self, problem, action):
        next_state, pushed = problem.move(self.state, action)
        next_node = Node(next_state, self, action,
                         problem.g(self.path_cost, self.state,
                                   pushed, next_state))
        return next_node

    def path(self):
        """
        Returns list of nodes from this node to the root node
        """
        node, path_back = self, []
        while node:
            path_back.append(node)
            node = node.parent
        return list(reversed(path_back))

    def __repr__(self):
        return "<Node {}(g={})>".format(self.state, self.path_cost)

    def __lt__(self, other):
        return self.path_cost + self.heuristic_score < other.path_cost + other.heuristic_score  # A*:f(n)=g(n)+h(n)

    def __eq__(self, other):
        return self.state == other.state


class Problem(object):
    def __init__(self, init_state=None, goal_state=None):
        self.init_state = Node(init_state)
        self.goal_state = Node(goal_state)

    def actions(self, state):
        """
        Given the current state, return valid actions.
        :param state:
        :return: valid actions
        """
        pass

    def move(self, state, action):
        pass

    def is_goal(self, state):
        pass

    def g(self, cost, from_state, pushed, to_state):
        return cost + pushed

    def solution(self, goal):
        """
        Returns actions from this node to the root node
        """
        if goal.state is None:
            return None
        return [node for node in goal.path()[:]]

    def expand(self, node):  # Returns a list of child nodes
        return [node.child_node(self, action) for action in self.actions(node.state)]


class Maze(Problem):
    def __init__(self,
                 init_state=None,  # e.g. {'egg_pos':[(2, 5), (3, 2), (2, 2)],'mouse_pos': [3, 1]}
                 goal_state=None,
                 map=None,
                 ordered=False):
        """ Define goal state and initialize a problem """
        super().__init__(init_state, goal_state)
        self.map = map
        self.ordered = ordered
        self.dead_squares = self.simple_deadlock()

    def actions(self, state):
        possible_actions = ['UP', 'DOWN', 'LEFT', 'RIGHT']
        pos = state['mouse_pos']
        # detect precomputed dead_squares and freeze deadlocks
        if any(self.dead_squares[pos[0]][pos[1]] for pos in state['egg_pos']):
            return []
        elif self.freeze_deadlock(state):
            return []

        if self.map[pos[0] - 1][pos[1]] == WALL:                # a wall on certain direction
            possible_actions.remove('UP')
        elif (pos[0] - 1, pos[1]) in state['egg_pos'] and (     # an egg on certain direction
                (pos[0] - 2, pos[1]) in state['egg_pos'] or self.map[pos[0] - 2][pos[1]] == -9):
            possible_actions.remove('UP')
        if self.map[pos[0] + 1][pos[1]] == WALL:
            possible_actions.remove('DOWN')
        elif (pos[0] + 1, pos[1]) in state['egg_pos'] and (
                (pos[0] + 2, pos[1]) in state['egg_pos'] or self.map[pos[0] + 2][pos[1]] == -9):
            possible_actions.remove('DOWN')
        if self.map[pos[0]][pos[1] - 1] == WALL:
            possible_actions.remove('LEFT')
        elif (pos[0], pos[1] - 1) in state['egg_pos'] and (
                (pos[0], pos[1] - 2) in state['egg_pos'] or self.map[pos[0]][pos[1] - 2] == -9):
            possible_actions.remove('LEFT')
        if self.map[pos[0]][pos[1] + 1] == WALL:
            possible_actions.remove('RIGHT')
        elif (pos[0], pos[1] + 1) in state['egg_pos'] and (
                (pos[0], pos[1] + 2) in state['egg_pos'] or self.map[pos[0]][pos[1] + 2] == -9):
            possible_actions.remove('RIGHT')

        return possible_actions

    def move(self, state, action):
        new_state = deepcopy(state)
        mouse = state['mouse_pos']
        pushed = False

        if action == 'RIGHT':
            if (mouse[0], mouse[1] + 1) in new_state['egg_pos']:
                pushed = True
                idx = state['egg_pos'].index((mouse[0], mouse[1] + 1))
                new_state['egg_pos'][idx] = (mouse[0], mouse[1] + 2)
            new_state['mouse_pos'] = [mouse[0], mouse[1] + 1]

        if action == 'LEFT':
            if (mouse[0], mouse[1] - 1) in new_state['egg_pos']:
                pushed = True
                idx = state['egg_pos'].index((mouse[0], mouse[1] - 1))
                new_state['egg_pos'][idx] = (mouse[0], mouse[1] - 2)
            new_state['mouse_pos'] = [mouse[0], mouse[1] - 1]

        if action == 'UP':
            if (mouse[0] - 1, mouse[1]) in new_state['egg_pos']:
                pushed = True
                idx = state['egg_pos'].index((mouse[0]-1, mouse[1]))
                new_state['egg_pos'][idx] = (mouse[0]-2, mouse[1])
            new_state['mouse_pos'] = [mouse[0] - 1, mouse[1]]

        if action == 'DOWN':
            if (mouse[0] + 1, mouse[1]) in new_state['egg_pos']:
                pushed = True
                idx = state['egg_pos'].index((mouse[0]+1, mouse[1]))
                new_state['egg_pos'][idx] = (mouse[0]+2, mouse[1])
            new_state['mouse_pos'] = [mouse[0] + 1, mouse[1]]

        if not self.ordered:
            new_state['egg_pos'].sort()

        return new_state, pushed

    def is_goal(self, state):
        return state['egg_pos'] == self.goal_state.state['egg_pos']

    def heuristic_function(self, state, fast=False):
        heuristic = 0
        if self.ordered:     # if ordered, calc pairwise manhat-dis
            heuristic = np.sum(np.abs(np.array(state['egg_pos']) - np.array(self.goal_state.state['egg_pos'])))
        else:               # if not ordered, calc manhat-dis greedily
            for egg in state['egg_pos']:
                heuristic += np.min(np.sum(np.abs(np.array(egg) - np.array(self.goal_state.state['egg_pos'])), axis=1))

        if fast:            # if use fast, penalize each egg not in goal
            for i, pos in enumerate(state['egg_pos']):
                if self.ordered:
                    if pos not in self.goal_state.state['egg_pos']:
                        heuristic += 9999
                else:
                    if pos != self.goal_state.state['egg_pos'][i]:
                        heuristic += 9999

        return heuristic

    def simple_deadlock(self):
        """Mark squares where boxes can reach to any goal."""
        # return bi-dimensional list that stores the positions where boxes can reach at least one goal
        # positions with True are not reachable and are considered dead squares
        unvisited = np.ones(self.map.shape) > 0
        # iterative breath first search to find the unreacheable positions starting at a goal
        # and doing the opposite movement (pulling the box instead of pushing )
        for egg_pos in self.goal_state.state['egg_pos']:
            open_nodes = [egg_pos]
            while open_nodes:
                x, y = open_nodes.pop()
                if not unvisited[x][y]:
                    continue
                unvisited[x][y] = False  # mark as visited
                # continue search if two squares behind the box are empty
                hor_size = self.map.shape[0]
                ver_size = self.map.shape[1]
                if x in range(hor_size) and y + 2 in range(ver_size) and not (self.map[x][y + 2] == -9) and not (
                        self.map[x][y + 1] == -9):
                    open_nodes.append((x, y + 1))
                if x + 2 in range(hor_size) and y in range(ver_size) and not (self.map[x + 2][y] == -9) and not (
                        self.map[x + 1][y] == -9):
                    open_nodes.append([x + 1, y])
                if x in range(hor_size) and y - 2 in range(ver_size) and not (self.map[x][y - 2] == -9) and not (
                        self.map[x][y - 1] == -9):
                    open_nodes.append([x, y - 1])
                if x - 2 in range(hor_size) and y in range(ver_size) and not (self.map[x - 2][y] == -9) and not (
                        self.map[x - 1][y] == -9):
                    open_nodes.append([x - 1, y])
        return unvisited

    def freeze_deadlock(self, state, ignore_goals=True):
        """
        :param state: a dictionary which stores current positions of eggs and the mouse
        :param ignore_goals: a flag to ignore the blocked eggs that are on a goal
        """
        def is_blocked(egg, all_egg_pos, ignore_goals):
            x, y = egg
            vis_eggs = {(x, y)}
            global_any_off_goal = (x, y) not in self.goal_state.state['egg_pos']
            global_blocked = 0

            # x-axis
            if self.map[x - 1][y] == -9 or self.map[x + 1][y] == -9:  # blocked by a wall on any side
                global_blocked |= 0b01
            elif self.dead_squares[x - 1][y] and self.dead_squares[x + 1][y]:  # blocked by a dead square on both sides
                global_blocked |= 0b01

            # y-axis
            if self.map[x][y - 1] == -9 or self.map[x][y + 1] == -9:
                global_blocked |= 0b10
            elif self.dead_squares[x][y - 1] and self.dead_squares[x][y + 1]:
                global_blocked |= 0b10

            # print(x,y,global_blocked,global_any_off_goal)
            if global_blocked == 0b11 and (
                    global_any_off_goal or not ignore_goals):  # blocked locally on both axis and one box off goal
                return True

            # prepare recursive search for every adjacent box
            open_boxes = []
            for dx in (-1, 1):
                if (x + dx, y) in all_egg_pos:
                    open_boxes.append((x + dx, y, (global_blocked & 0b10) >> 1, 0b01, False, global_any_off_goal))
            for dy in (-1, 1):
                if (x, y + dy) in all_egg_pos:
                    open_boxes.append((x, y + dy, (global_blocked & 0b01) << 1, 0b10, True, global_any_off_goal))

            # iterative search on other boxes
            while open_boxes:
                x, y, blocked, blocked_axis, search_x_axis, any_off_goal = open_boxes.pop()
                vis_eggs.add((x, y))
                any_off_goal |= ((x, y) not in self.goal_state.state['egg_pos'])
                if search_x_axis:
                    if ((self.map[x - 1][y] == -9 or self.map[x + 1][y] == -9)
                            or (self.dead_squares[x - 1][y] and self.dead_squares[x + 1][y])
                            or ((x - 1, y) in vis_eggs or (x + 1, y) in vis_eggs)):  # blocked by a box on any side
                        blocked |= 0b01
                        global_blocked |= blocked_axis
                        global_any_off_goal |= any_off_goal
                    else:
                        continue
                else:
                    if ((self.map[x][y - 1] == -9 or self.map[x][y + 1] == -9)
                            or (self.dead_squares[x][y - 1] and self.dead_squares[x][y + 1])
                            or ((x, y - 1) in vis_eggs or (x, y + 1) in vis_eggs)):
                        blocked |= 0b10
                        global_blocked |= blocked_axis
                        global_any_off_goal |= any_off_goal
                    elif self.map[x][y - 1] != -9 and self.map[x][y - 1] != -9:
                        continue

                if blocked == 0b11 and (any_off_goal or not ignore_goals):  # blocked on both axis and one box off goal
                    return True
                if global_blocked == 0b11 and (global_any_off_goal or not ignore_goals):
                    return True

                # if it is not blocked and there are other boxes around, search for them
                if search_x_axis:
                    for dx in (-1, 1):
                        if (x + dx, y) not in vis_eggs and (x + dx, y) in all_egg_pos:
                            open_boxes.append((x + dx, y, (blocked & 0b10) >> 1, blocked_axis, False, any_off_goal))
                else:
                    for dy in (-1, 1):
                        if (x, y + dy) not in vis_eggs and (x, y + dy) in all_egg_pos:
                            open_boxes.append((x, y + dy, (blocked & 0b01) << 1, blocked_axis, True, any_off_goal))
            return False

        for egg_pos in state['egg_pos']:
            if is_blocked(egg_pos, state['egg_pos'], ignore_goals):
                return True
        return False
