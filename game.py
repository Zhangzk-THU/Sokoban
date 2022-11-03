import numpy as np
import pygame, sys
from search import *
from problem import Maze
import time

# load image dependencies
IMG_SIZE = 32
wall = pygame.image.load('images/wall.png')
floor = pygame.image.load('images/floor.png')
egg = pygame.image.load('images/box.png')
egg_docked = pygame.image.load('images/box_docked.png')
worker = pygame.image.load('images/worker.png')
worker_docked = pygame.image.load('images/worker_dock.png')
docker = pygame.image.load('images/dock.png')
background = 255, 226, 191
colors = ['red', 'blue', 'green', 'purple', 'yellow']


# read games from levels.txt
def load_game():
    level = -999
    order = '?'
    ordered = True
    while not (level >= 0 and level <= 10):
        level = int(input('please enter level(0~6):'))
    filename = 'levels.txt'
    while not (order == 'y' or order == 'n'):
        order = input('please enter whether eggs are ordered(y/n):')
    if order == 'y':
        ordered = True
    elif order == 'n':
        ordered = False

    # read file by lines
    with open(filename, 'r') as file:
        level_found = False
        init_state = {'egg_pos': [], 'mouse_pos': []}
        goal_state = {'egg_pos': [], 'mouse_pos': []}
        map = []
        row_count = 0
        for line in file:
            if not level_found:
                if "Level " + str(level) == line.strip():
                    level_found = True
            else:
                if line.strip() != "":
                    row = []
                    col_count = 0
                    for c in line:
                        if c != '\n':
                            if c == '#':
                                row.append(-9)
                            else:
                                if c == '$':
                                    init_state['egg_pos'].append((row_count, col_count))
                                if c == '.':
                                    goal_state['egg_pos'].append((row_count, col_count))
                                if c == '@':
                                    init_state['mouse_pos'] = [row_count, col_count]
                                if c == '*':
                                    goal_state['egg_pos'].append((row_count, col_count))
                                    init_state['mouse_pos'] = [row_count, col_count]
                                row.append(0)
                        elif c == '\n':  # jump to next row when newline
                            map.append(np.array(row))
                            continue
                        else:
                            print("ERROR: Level " + str(level) + " has invalid value " + c)
                            sys.exit(1)
                        col_count += 1
                    row_count += 1
                else:
                    break
        return init_state, goal_state, np.array(map), level, ordered


# display current state & hints
def display_state(screen, node):
    fontobject = pygame.font.Font(None, 18)
    # draw rectangle for captions
    pygame.draw.rect(screen, (0, 0, 0),
                     ((screen.get_width() / 2) - 150,
                      screen.get_height() - 50,
                      300, 45), 0)
    pygame.draw.rect(screen, (255, 255, 255),
                     ((screen.get_width() / 2) - 152,
                      screen.get_height() - 52,
                      304, 49), 1)
    # display captions
    screen.blit(fontobject.render('level:' + str(level_selected), 1, (255, 255, 255)),
                ((screen.get_width() / 2) - 130, (screen.get_height()) - 50))
    screen.blit(fontobject.render('pushes:' + str(node.path_cost), 1, (255, 255, 255)),
                ((screen.get_width() / 2) - 70, (screen.get_height()) - 50))
    screen.blit(fontobject.render('steps:' + str(node.depth), 1, (255, 255, 255)),
                (screen.get_width() / 2, (screen.get_height()) - 50))
    screen.blit(fontobject.render('ordered:' + str(ordered), 1, (255, 255, 255)),
                ((screen.get_width() / 2) + 60, (screen.get_height()) - 50))
    screen.blit(fontobject.render('press \'P\' for faster?(but not optimal) AI search', 1, (255, 0, 0)),
                ((screen.get_width() / 2) - 130, (screen.get_height()) - 40))
    screen.blit(fontobject.render('press \'SPACE\' for slow AI search', 1, (255, 255, 0)),
                ((screen.get_width() / 2) - 90, (screen.get_height()) - 30))
    screen.blit(fontobject.render('press \'D\' for backtrack, \'R\' for restart, \'Q\' for quit', 1, (0, 255, 255)),
                ((screen.get_width() / 2) - 130, (screen.get_height()) - 20))


# display special messages with flashing
def display_words(screen, message):
    font_object = pygame.font.Font(None, 18)
    pygame.draw.rect(screen, (0, 0, 0),
                     ((screen.get_width() / 2) - 100,
                      (screen.get_height() / 2) - 10,
                      200, 20), 0)
    pygame.draw.rect(screen, (255, 255, 255),
                     ((screen.get_width() / 2) - 102,
                      (screen.get_height() / 2) - 12,
                      204, 24), 1)
    screen.blit(font_object.render(message, 1, (255, 255, 255)),
                ((screen.get_width() / 2) - 100, (screen.get_height() / 2) - 10))
    pygame.display.flip()


# draw the whole maze according to current state
def print_game(game, state, screen):
    screen.fill(background)

    for row in range(game.map.shape[0]):
        for col in range(game.map.shape[1]):
            # floor
            if game.map[row][col] == 0:
                if (row, col) in game.goal_state.state['egg_pos']:
                    if (row, col) in state['egg_pos']:
                        screen.blit(egg_docked, (IMG_SIZE * col, IMG_SIZE * row))
                    elif [row, col] == state['mouse_pos']:
                        screen.blit(worker_docked, (IMG_SIZE * col, IMG_SIZE * row))
                    else:
                        screen.blit(docker, (IMG_SIZE * col, IMG_SIZE * row))
                else:
                    if (row, col) in state['egg_pos']:
                        screen.blit(egg, (IMG_SIZE * col, IMG_SIZE * row))
                    elif [row, col] == state['mouse_pos']:
                        screen.blit(worker, (IMG_SIZE * col, IMG_SIZE * row))
                    else:
                        screen.blit(floor, (IMG_SIZE * col, IMG_SIZE * row))
            # wall
            elif game.map[row][col] == -9:
                screen.blit(wall, (IMG_SIZE * col, IMG_SIZE * row))

    if game.ordered:
        for i, (row,col) in enumerate(state['egg_pos']):
            pygame.draw.rect(screen, colors[i], (IMG_SIZE*col+IMG_SIZE/4, IMG_SIZE * row+IMG_SIZE/4, IMG_SIZE/2, IMG_SIZE/2))
        for i, (row, col) in enumerate(game.goal_state.state['egg_pos']):
            pygame.draw.rect(screen, colors[i], (IMG_SIZE*col+IMG_SIZE/4, IMG_SIZE * row+IMG_SIZE/4, IMG_SIZE/2, IMG_SIZE/2))



if __name__ == "__main__":
    # init game
    init_state, goal_state, map, level_selected, ordered = load_game()
    goal_state['egg_pos'].sort()
    print(init_state)
    if level_selected==0 and ordered:
        goal_state['egg_pos'].sort(reverse=True)
    print(goal_state)
    game = Maze(init_state, goal_state, map, ordered)
    row, col = game.map.shape
    player_node_list = [game.init_state]
    result = []
    result_show_step = 0

    # init pygame window
    pygame.init()
    screen = pygame.display.set_mode((IMG_SIZE * col, IMG_SIZE * row + 70))

    # game loop
    while 1:
        # check if player  won
        if game.is_goal(player_node_list[-1].state):
            display_words(screen, 'level completed, press n for next level')
        print_game(game, player_node_list[-1].state, screen)
        display_state(screen, player_node_list[-1])

        # if got a result, show it step by step:
        if result:
            print_game(game, result[result_show_step].state, screen)
            display_state(screen, result[result_show_step])
            pygame.display.update()
            pygame.time.wait(100)
            if result_show_step == len(result) - 1:
                pygame.time.wait(900)
                result = []
                result_show_step = -1
            result_show_step += 1

        # check if player is dead
        if not game.actions(player_node_list[-1].state):
            display_words(screen, 'no valid moves, please go back')

        # update pygame
        pygame.display.update()
        # else get orders from player
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    if 'UP' in game.actions(player_node_list[-1].state):
                        player_node_list.append(player_node_list[-1].child_node(game, 'UP'))
                elif event.key == pygame.K_DOWN:
                    if 'DOWN' in game.actions(player_node_list[-1].state):
                        player_node_list.append(player_node_list[-1].child_node(game, 'DOWN'))
                elif event.key == pygame.K_LEFT:
                    if 'LEFT' in game.actions(player_node_list[-1].state):
                        player_node_list.append(player_node_list[-1].child_node(game, 'LEFT'))
                elif event.key == pygame.K_RIGHT:
                    if 'RIGHT' in game.actions(player_node_list[-1].state):
                        player_node_list.append(player_node_list[-1].child_node(game, 'RIGHT'))
                elif event.key == pygame.K_SPACE:
                    newgame = Maze(player_node_list[-1].state, game.goal_state.state, map, ordered)
                    time1 = time.time()
                    result = A_star(newgame, False)
                    time2 = time.time()
                    print("search time:", time2 - time1)
                    print('pushes=', result[-1].path_cost if result else "no solutions", ', steps=', len(result)-1 if result else "no solutions")
                elif event.key == pygame.K_p:
                    newgame = Maze(player_node_list[-1].state, game.goal_state.state, map, ordered)
                    time1 = time.time()
                    result = A_star(newgame, True)
                    time2 = time.time()
                    print("search time:", time2 - time1)
                    print('cost=', result[-1].path_cost if result else "no solutions", ', steps=',
                          len(result)-1 if result else "no solutions")
                elif event.key == pygame.K_q:
                    sys.exit(0)
                elif event.key == pygame.K_d:
                    if len(player_node_list) > 1:
                        player_node_list.pop(-1)
                elif event.key == pygame.K_r:
                    for idx in range(len(player_node_list)-1):
                        player_node_list.pop(-1)
