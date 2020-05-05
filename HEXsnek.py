"""
    Adam Ziółkowski
    Snake game with board made of hexagons, made to be enjoyed in terminal

    Controls:
    left arrow - left
    right arrow - right
    q - left up
    e - right up
    a - left down
    d - right down

"""
import numpy as np
import random
import curses
import time
from curses import wrapper

# implementation requires n to be odd
n = 11


def initialize_hexes():
    # declaration of array of Hex classes
    hexes = np.empty((2 * n - 1, n), dtype=Hex)
    """
        array initialization in form that depicts hexagonal mesh
        [[ Hex, None, Hex, ... ],
         [ None, Hex, None, ...],
         [ ...   ...  ...  ... ]] 
        
    """
    for i in range(2 * n - 1):
        for j in range(n):
            if i % 2 == 0 and j % 2 == 0:
                hexes[i][j] = Hex(2 * i + 3, 2 * j + 2)
            elif i % 2 != 0 and j % 2 != 0:
                hexes[i][j] = Hex(2 * i + 3, 2 * j + 2)
            else:
                hexes[i][j] = None
    # Sneak starts from 0,0 hexagon
    hexes[0][0].is_snake = True
    hexes[0][0].is_snakehead = True
    snek = Snek(0, 0)
    # first fruit
    grow_fruit(hexes)

    return snek, hexes


# Function for printing out gameboard
def print_board(stdscr, hexes):
    # Simple hexagons representation
    for i in range(1, n * 2, 4):
        stdscr.addstr(i, 2, "/ \\ " * n)
        stdscr.addstr(i + 1, 1, "|")
        stdscr.addstr(i + 1, 2, "   |" * n)
        stdscr.addstr(i + 2, 2, "\\ / " * n)
        stdscr.addstr(i + 3, 0, "   |" * n)
    # curses library allows printing at any spot in terminal so I print out agents after board
    for hexe in hexes:
        for hex_i in hexe:
            if hex_i is None:
                continue
            if hex_i.is_fruit:
                stdscr.addstr(hex_i.y, hex_i.x, "$", curses.color_pair(1))
            if hex_i.is_snake:
                stdscr.addstr(hex_i.y, hex_i.x, "#", curses.color_pair(2))
            if hex_i.is_snakehead:
                stdscr.addstr(hex_i.y, hex_i.x, "@", curses.color_pair(2))
    # controls
    stdscr.addstr(1, 5 * n, "CONTROLS:")
    stdscr.addstr(2, 5 * n, "left arrow - left")
    stdscr.addstr(3, 5 * n, "right arrow - right")
    stdscr.addstr(4, 5 * n, "q - left up")
    stdscr.addstr(5, 5 * n, "e - right up")
    stdscr.addstr(6, 5 * n, "a - left down")
    stdscr.addstr(7, 5 * n, "d - right down")
    stdscr.addstr(8, 5 * n, "ESC - terminate game")


# Random fruit generation
def grow_fruit(hexes):
    done = False
    while not done:
        # Hexagons are placed only on all odd or all even coordinates of array
        x = random.randrange(0, 2 * n - 1, 1)
        if x % 2 == 0:
            y = random.randrange(0, n, 2)
        else:
            y = random.randrange(1, n, 2)
        # Fruit can't appear where snake or previous fruit is
        if hexes[x][y].is_snake or hexes[x][y].is_fruit:
            continue
        hexes[x][y].is_fruit = True
        done = True


# Collision detection
def collisions(hexes, x, y, score, up=False, down=False, left=False, right=False):
    collision = False
    fruit_eaten = False
    if up and y < 0:
        collision = True
    if down and y > n - 1:
        collision = True
    if left and x < 0:
        collision = True
    if right and x > 2 * n - 2:
        collision = True
    if not collision and hexes[x][y].is_snake:
        collision = True
    if not collision and hexes[x][y].is_fruit:
        score += 10
        grow_fruit(hexes)
        hexes[x][y].is_fruit = False
        fruit_eaten = True
    return collision, fruit_eaten, score


# This class carries information about whats in each hexagon, and where it is on the board
class Hex:
    # coordinates of hexagon editable center on board
    x = None
    y = None

    is_snake = False
    is_snakehead = False
    is_fruit = False

    def __init__(self, x, y, sneak=None, fruit=None):
        self.x = x
        self.y = y
        if sneak:
            self.is_snake = sneak
        if fruit:
            self.is_fruit = fruit


# Snake agent class holding all coordinates of hexagons where it is and methode for moving
class Snek:
    x = []
    y = []

    def __init__(self, x, y):
        self.x.append(x)
        self.y.append(y)

    def move(self, diff_x, diff_y, if_eaten):
        self.x.append(self.x[-1] + diff_x)
        self.y.append(self.y[-1] + diff_y)
        if not if_eaten:
            self.x.pop(0)
            self.y.pop(0)


# main function with main game loop
def main(stdscr):
    # Clear screen
    stdscr.clear()
    # Turn of delay on getch()
    stdscr.nodelay(1)
    # Turn of cursor visibility
    curses.curs_set(0)
    # Game initialization
    snek, hexes = initialize_hexes()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)
    print_board(stdscr, hexes)
    stdscr.refresh()
    # last pressed key for constant movement
    last_pressed = curses.KEY_RIGHT
    allowed_key = [97, 100, 101, 27,  113, curses.KEY_LEFT, curses.KEY_RIGHT]

    game_over = False
    score = 0

    # game loop
    while True:

        pressed = stdscr.getch()
        if pressed == -1:
            pressed = last_pressed
        elif pressed in allowed_key:
            last_pressed = pressed

        hexes[snek.x[0]][snek.y[0]].is_snake = False
        hexes[snek.x[-1]][snek.y[-1]].is_snakehead = False

        if pressed == curses.KEY_LEFT:  # left arrow
            collision, fruit_eaten, score = collisions(hexes, snek.x[-1] - 2, snek.y[-1], score, left=True)
            if collision:
                game_over = True
                break
            else:
                snek.move(-2, 0, fruit_eaten)
        if pressed == curses.KEY_RIGHT:  # left arrow
            collision, fruit_eaten, score = collisions(hexes, snek.x[-1] + 2, snek.y[-1], score, right=True)
            if collision:
                game_over = True
                break
            else:
                snek.move(2, 0, fruit_eaten)
        if pressed == 113:  # q
            collision, fruit_eaten, score = collisions(hexes, snek.x[-1] - 1, snek.y[-1] - 1, score, up=True, left=True)
            if collision:
                game_over = True
                break
            else:
                snek.move(-1, -1, fruit_eaten)
        if pressed == 101:  # e
            collision, fruit_eaten, score = collisions(hexes, snek.x[-1] + 1, snek.y[-1] - 1, score, up=True, right=True)
            if collision:
                game_over = True
                break
            else:
                snek.move(+1, -1, fruit_eaten)
        if pressed == 97:  # a
            collision, fruit_eaten, score = collisions(hexes, snek.x[-1] - 1, snek.y[-1] + 1, score, down=True, left=True)
            if collision:
                game_over = True
                break
            else:
                snek.move(-1, 1, fruit_eaten)
        if pressed == 100:  # d
            collision, fruit_eaten, score = collisions(hexes, snek.x[-1] + 1, snek.y[-1] + 1, score, down=True, right=True)
            if collision:
                game_over = True
                break
            else:
                snek.move(1, 1, fruit_eaten)

        hexes[snek.x[-1]][snek.y[-1]].is_snake = True
        hexes[snek.x[-1]][snek.y[-1]].is_snakehead = True

        if pressed == 27:  # ESC
            break

        stdscr.addstr(0, 19, "SCORE: {}".format(score), curses.A_BOLD)
        print_board(stdscr, hexes)
        stdscr.refresh()
        time.sleep(0.65)
    # Now getkey() will wait for user interaction before shutting down
    stdscr.nodelay(0)
    if game_over:
        stdscr.addstr(n + 1, 2 * n - 3, "GAME OVER", curses.A_BOLD | curses.A_BLINK)
        stdscr.refresh()
        stdscr.getkey()
    else:
        stdscr.addstr(n + 1, 2 * n - 8, "Game terminated", curses.A_BOLD)
        stdscr.refresh()
        stdscr.getkey()


# Curses wrapper that handles terminal preparation and cleans after main function is done
wrapper(main)
