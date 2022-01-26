#TODO:
# Seperate into different files
	#../../../window.py
	#snake.py
"""This is a project I am made to get python practice
in! It's the game Snake built from scratch -- not with
a game or screen API"""

import random
import sys
import tty
import termios
import select
import time
import threading
sys.path.append("../../../py_lib")
import clear
import inputs

# Unicode of char's that represent the border of the board
top_left = u'\u2554'
top_right = u'\u2557'
bottom_left = u'\u255a'
bottom_right = u'\u255D'
horizontal = u'\u2550'
vertical =  u'\u2016'

class Snake:
        """Welcome to Snake! This game will only work
        correctly if you only click the arrow keys,
        otherwise it can't handle the input and will
        glitch! Conveniently, that is also how you exit
        the game. Type three non-arrow keys to quit."""

#| In case I want to tweak the game to change the char's used
#| for each 'thing'
        SIZE = 11  #| Accounts for sides of map as well as inside
        PLAYER = '$'
        HEAD = "O"  #| "Head" of snake
        EMPTY = ' '
        PELLET = '*'

        xPos = [SIZE/2]  #| Start player in the middles
        yPos = [SIZE/2]  #| Start player in the middles
        score = 0  #| Used to determine size of snake; snake_size = score+1
        xPel = random.randrange(1, SIZE-1)
        yPel = random.randrange(1, SIZE-1)
        cur_dir = 1  #| Direction snake is currently going
        _debug_data = ""

        def __init__(self, size):
                """'size' is the length of the board, and
                entails the sides."""

                random.seed()
                self.SIZE = size  #|  Size of grid, including the borders
                self.xPos = [self.SIZE//2 - 1]  #| Start player in the middle of the board
                self.yPos = [self.SIZE//2 - 1]  #| Start player in the middle of the board
                self.xPel = random.randrange(1, self.SIZE-1)
                self.yPel = random.randrange(1, self.SIZE-1)
                while True:
                        if self.yPel == self.yPos[0]:
                                self.yPel = random.randrange(1,self.SIZE-1)
                                continue
                        if self.xPel == self.xPos[0]:
                                self.xPel = random.randrange(1,self.SIZE-1)
                                continue
                        break

        def draw(self):
                """Draws the board and the player's
                position/length on it."""

                for i in range(0, self.SIZE):
                        row = ""
                        for j in range(0, self.SIZE):
                                if i == 0:  #| Top row
                                        if j == 0:
                                                row += top_left
                                        elif j == self.SIZE-1:
                                                row += top_right
                                        else:
                                                row += horizontal
                                        continue
                                elif i == self.SIZE-1:  #| Bottom row
                                        if j == 0:
                                                row += bottom_left
                                        elif j == self.SIZE-1:
                                                row += bottom_right
                                        else:
                                                row += horizontal
                                        continue
                                else:  #| The GAME
                                        for z in range(0, self.score+1):  #| The snake
                                                if i == self.yPos[z] and j == self.xPos[z]:
                                                        if z == 0:
                                                                row += self.HEAD
                                                        else:
                                                                row += self.PLAYER
                                                        break
                                        else:
                                                if j == 0 or j == self.SIZE-1:  #| Edge bits
                                                        row += vertical
                                                        #print(i, "edge bit")
                                                        continue
                                                elif self.xPel == j and self.yPel == i:  #| Pellet
                                                        row += self.PELLET
                                                        continue
                                                row += self.EMPTY
                        print(i, "\t", row)
                                #print(self._debug_data)
                        self._debug_data = ""

        def getInput(self):
                """Uses custom inputs.py lib to
                passively take arrow input."""
                #| Determine direction in which to move
                inp = inputs.passiveInput()
                if not inp == None:
                        self.cur_dir = inp


        def move(self):
                """Gets input from the player to move
                their snake. Also checks for collisions."""

                for i in reversed(range(0, self.score+1)):  #| Manage all snake segments
                        if i == 0:  #| is Head
                                if self.cur_dir == 1 and self.yPos[i] > 1:  #| Up
                                        self.yPos[i] -= 1
                                elif self.cur_dir == 2 and self.xPos[i] < self.SIZE-2:  #| Right
                                        self.xPos[i] += 1
                                elif self.cur_dir == 3 and self.yPos[i] < self.SIZE-2:  #| Down
                                        self.yPos[i] += 1
                                elif self.cur_dir == 4 and self.xPos[i] > 1:  #| Left
                                        self.xPos[i] -= 1
                                else: self.lose()  #| Hit wall

                                for j in range(1, self.score+1):  #| Check for self-collision
                                        if self.xPos[i] == self.xPos[j] and self.yPos[i] == self.yPos[j]:
                                                self.lose()
                        else:  #| is Body (a.k.a. not-Head)
                                if self.yPos[i-1] < self.yPos[i]:
                                        self.yPos[i] -= 1
                                if self.yPos[i-1] > self.yPos[i]:
                                        self.yPos[i] += 1
                                if self.xPos[i-1] < self.xPos[i]:
                                        self.xPos[i] -= 1
                                if self.xPos[i-1] > self.xPos[i]:
                                        self.xPos[i] += 1

                        if self.yPos[i] == self.yPel and self.xPos[i] == self.xPel:  #| Run into pellet
                                self.gain_point()

        def gain_point(self):
                """Gain a point, grow the snake, and move the pellet.
                Direction is the direction in which the snake
                is currently moving."""

                self.score += 1  #| Increment score
                new_x = self.xPos[len(self.xPos)-1]  #| New x pos for node
                new_y = self.yPos[len(self.yPos)-1]  #| New y pos for node

                #| Move pellet
                # Wish python would have do-while loops...
                xPellet = random.randrange(1, self.SIZE-1)  #| New x pos for pellet
                yPellet = random.randrange(1, self.SIZE-1)  #| New y pos for pellet
                while True:  #| Make sure pellet moves and isn't "in" the snake
                        while xPellet == self.xPel or yPellet == self.yPel:
                                xPellet = random.randrange(1, self.SIZE-1)
                                yPellet = random.randrange(1, self.SIZE-1)
                        for i in range(0, self.score):  #| Not score+1, cause end node hasn't been appended yet
                                if xPellet == self.xPos[i] and yPellet == self.yPos[i]:
                                        xPellet = self.xPel
                                        yPellet = self.yPel
                                        break
                        else: break
                self.xPel = xPellet
                self.yPel = yPellet

		#| Determine the position of new node
                if self.score != 0:
                        if self.xPos[self.score-2] == self.xPos[self.score-1]:
                                if self.yPos[self.score-2] < self.yPos[self.score-1]:  #| Tack node on the bottom
                                        new_y -= 1
                                if self.yPos[self.score-2] > self.yPos[self.score-1]:  #| On top
                                        new_y += 1
                        else:
                                if self.xPos[self.score-2] > self.xPos[self.score-1]:  #| On left
                                        new_x -= 1
                                else:  #| On right
                                        new_x += 1

#| Make new snake node
                self.xPos.append(new_x)
                self.yPos.append(new_y)
                self._debug_data += f"[{new_x}, {new_y}]"

        def lose(self):
                """End game via loss."""
                sys.exit("YOU LOST")

        def start(self):
                """Start game."""
                clear.clear()
                print("SCORE: ", self.score)
                self.draw()
                t0 = time.clock()
                while True:
                        tNow = time.clock()
                        #GET INPUT
                        self.getInput()
                        if tNow - t0 >= 0.1:  #| If .1 seconds have elapsed...
                                #DO STUFF
                                self.move()
                                clear.clear()
                                print("SCORE: ", self.score)
                                self.draw()
                                t0 = tNow


test = Snake(30)
test.start()

