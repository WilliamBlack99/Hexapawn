try:
    import pygame
    pygame.mixer.pre_init(buffer=2)
    pygame.init()
    from pygame.locals import *
    import time
    import alph as ai
    from screeninfo import get_monitors
except BaseException as e:
    print('failed to import module: ' + str(e))
    raise BaseException

# To DO:
# support mac
# create background
# save alph's memory
# credit sound effects
# convert files to application

# get a monitor's resolution
try:
    x_res = 0
    y_res = 0
    while x_res == 0 or y_res == 0:   # because get_monitors() sometimes returns an empty list, repeat until you have an x_res and y_res
        for m in get_monitors():
            x_res = m.width
            y_res = m.height
except BaseException as e:
    print('failed to set resolution: ' + str(e))
    raise BaseException

# find the width and height of the game given the resolution
if x_res > y_res:
    height = y_res
    width = y_res
    game_x = x_res // 2 - width // 2
    game_y = 0
else:
    height = x_res
    width = x_res
    game_x = 0
    game_y = y_res // 2 - height // 2



# colors used
board_color_1 = (156, 111, 70)     # Brown
board_color_2 = (215, 186, 154)    # Light Brown
top_color = (46, 35, 30)           # Dark Brown
bottom_color = (236, 229, 198)     # Off White
selection_color = (0, 255, 0)      # Lime

# create game window
screen = pygame.display.set_mode((x_res, y_res), pygame.FULLSCREEN)

# import music and play on repeat
try:
    music = 'music.mp3'
    pygame.mixer.music.load(music)
    pygame.mixer.music.set_volume(0.8)
    pygame.mixer.music.play(-1)
except BaseException as e:
    print('failed to load/play music: ' + str(e))
    print('the game will continue without music')

# setup sound effects
try:
    pawn_move_sound = pygame.mixer.Sound('pawn movement.wav')
    pawn_captured_sound = pygame.mixer.Sound('pawn captured.wav')
    victory_sound = pygame.mixer.Sound('victory.wav')
    defeat_sound = pygame.mixer.Sound('defeat.wav')
except BaseException as e:
    print('failed to load sound effects: ' + str(e))
    raise BaseException

# an object used to save which pawn is selected and move it to a target square
class Selection:
    # class constructor
    def __init__(self):
        self.selection = False          # True if a pawn is being selected
        self.color = selection_color

    # process a key press into an appropriate action (select pawn, deselect pawn, move pawn)
    def select(self, x, y):
        if (x, y) == self.selection:                                    # if selecting a pawn that is already selected, deselect it
            self.selection = False
            return
        for instance in Pawn.instances:                                 # if selecting an active pawn, select it
            if instance.location == (x, y) and instance.is_active():
                self.selection = (x, y)
                return
        for instance in Pawn.instances:                                 # if not selecting an active pawn, move already selected pawn to new location
            if instance.location == self.selection and instance.is_active:
                instance.move((x, y))
                self.selection = False
                return

# pawns are the basic game pieces
class Pawn:
    instances = []    
    captured = []    # a list of all pawns that have been defeated
    turn = 1

    # class constructor
    def __init__(self, location, color):
        self.color = color

        # determine the pawns team and direction of movement from its color
        if color == top_color:
            self.team = 'top'
            self.y_change = 1
        else:
            self.team = 'bottom'
            self.y_change = -1
            
        self.location = location
        self.alive = True
        self.instances.append(self)

    # if the pawn is alive, draw it to the screen
    def draw(self):
        if self.alive:
            pygame.draw.circle(screen, self.color, (game_x + (self.location[0] * width // 3 + width // 6), \
                                                    game_y + (self.location[1] * height // 3 + height // 6)), width // 7)

    # if target location leads to a valid move, move pawn to target location
    # rules of movement:
    # -target square must be on the board
    # -move must be in towards opponents side vertically
    # -target square must be empty if moving vertically
    # -target square must be occupied by an enemy if moving diagonally
    def move(self, location):
        if location[0] < 0 or location[0] > 2 or location[1] < 0 or location[1] > 2: # not valid if out of bounds
            return
        if location[1] - self.location[1] == self.y_change: # not valid if pawn's direction of movement isn't consistent with target location
            if location[0] == self.location[0]:             # not valid if moving vertically and pawn in way
                for instance in self.instances:
                    if instance.location == location: 
                        return
            elif abs(location[0] - self.location[0]) == 1:  # not valid if moving diagonally and target location doesn't contain enemy pawn
                valid = False
                for instance in self.instances:
                    if instance.location == location and instance.team != self.team:
                        valid = True
                        instance.kill()
                if not valid:
                    return
            else:
                return
        else:
            return
        pawn_move_sound.play()
        # move pawn and increment turn counter
        self.location = location
        Pawn.turn += 1

    # if a pawn is defeated, stop drawing it and prevent it from apearing when iterating through all Pawn instances
    def kill(self):
        pawn_captured_sound.play()
        self.alive = False
        Pawn.instances.remove(self)
        Pawn.captured.append(self)

    # determine whether it is the pawn's team's turn to move
    def is_active(self):
        if ((self.turn % 2 == 0 and self.team == 'top') or (self.turn % 2 == 1 and self.team == 'bottom')) and self.alive:
            return True
        else:
            return False

# draw the board to the screen
def DrawBoard():
    for i in range(3):
        for j in range(3):
            if (i + j) % 2 == 0:
                color = board_color_1
            else:
                color = board_color_2
            pygame.draw.rect(screen, color, (game_x + i * width // 3, game_y + j * width // 3, width // 3, height // 3))

# return True if target location contains a pawn and it is not its turn
def SquareOccupied(x, y):
    for instance in Pawn.instances:
        if instance.location == (x, y) and not instance.is_active() and not (x > 2 or x < 0 or y > 2 or y < 0):
            return True
    return False

# determine if the game is over then punish or reward the ai accordingly
# victory conditions:
# -a pawn is on the opposite vertical side of the board from where it started
# -if the player whose turn it is has no possible moves
# -all pawns on a team are defeated
def VictoryCheck():
    stalemate = True
    top_pawns = 0
    bottom_pawns = 0
    for instance in Pawn.instances:

        # if pawn is on opposite vertical side from where it started return True and punish/reward ai
        if instance.location[1] == 0 and instance.team == 'bottom':
            ai.alph.punish()
            victory_sound.play()
            return True
        if instance.location[1] == 2 and instance.team == 'top':
            ai.alph.reward()
            defeat_sound.play()
            return True

        # count pawns on each team
        if instance.team == 'top':
            top_pawns += 1
        elif instance.team == 'bottom':
            bottom_pawns += 1

        # if there are no possible moves for the active player return True and punish/reward ai
        if (SquareOccupied(instance.location[0] - 1, instance.location[1] + instance.y_change) or \
           not SquareOccupied(instance.location[0], instance.location[1] + instance.y_change) or \
           SquareOccupied(instance.location[0] + 1, instance.location[1] + instance.y_change)) and \
           instance.is_active():
            stalemate = False
    if stalemate:
        if Pawn.turn % 2 == 0:
            ai.alph.punish()
            victory_sound.play()
            return True
        else:
            ai.alph.reward()
            defeat_sound.play()
            return True

    # if a team has no pawns, return True and punish/reward ai
    if top_pawns == 0:
        ai.alph.punish()
        victory_sound.play()
        return True
    elif bottom_pawns == 0:
        ai.alph.reward()
        defeat_sound.play()
        return True
    
    return False

# reset the game to be played again
def Restart():
    # revive all captured pawns
    for pawn in Pawn.captured:
        Pawn.instances.append(pawn)
        pawn.alive = True
    Pawn.captured = []

    # move pawns to starting positions
    top_left_pawn.location = (0, 0)
    top_middle_pawn.location = (1, 0)
    top_right_pawn.location = (2, 0)
    bottom_left_pawn.location = (0, 2)
    bottom_middle_pawn.location = (1, 2)
    bottom_right_pawn.location = (2, 2)

    # reset turn counter
    Pawn.turn = 1

# initialize pawns with their locations and colors
top_left_pawn = Pawn((0, 0), top_color)
top_middle_pawn = Pawn((1, 0), top_color)
top_right_pawn = Pawn((2, 0), top_color)
bottom_left_pawn = Pawn((0, 2), bottom_color)
bottom_middle_pawn = Pawn((1, 2), bottom_color)
bottom_right_pawn = Pawn((2, 2), bottom_color)
selection = Selection()

running = True

# game loop
while running:

    # event handling
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

        # if a key in the 3x3 grid on the keyboard consisting of q,w,e,a,s,d,z,x,c is pressed, attempt to select corresponding square on the board
        elif event.type == KEYDOWN: 
            if event.key == K_q:
                selection.select(0, 0)
            if event.key == K_w:
                selection.select(1, 0)
            if event.key == K_e:
                selection.select(2, 0)
            if event.key == K_a:
                selection.select(0, 1)
            if event.key == K_s:
                selection.select(1, 1)
            if event.key == K_d:
                selection.select(2, 1)
            if event.key == K_z:
                selection.select(0, 2)
            if event.key == K_x:
                selection.select(1, 2)
            if event.key == K_c:
                selection.select(2, 2)

            # exit if escape key is pressed
            if event.key == K_ESCAPE:
                running = False

    # draw the board to the screen
    DrawBoard()

    # if a pawn is selected indicate so with a colored square
    if selection.selection:
        pygame.draw.rect(screen, selection_color, (game_x + selection.selection[0] * width // 3, game_y + selection.selection[1] * width // 3, width // 3, height // 3))

    # draw all pawns to the screen
    for instance in Pawn.instances:
        instance.draw()

    # update the screen
    pygame.display.update()

    # if game is over, wait for a second then restart
    if VictoryCheck():
        time.sleep(1)
        Restart()

    # if it is the ai's turn
    if Pawn.turn % 2 == 0:
        time.sleep(1)

        # convert the state of the board so that alph can read it and give the data to him
        board = [['0', '0', '0'], ['0', '0', '0'], ['0', '0', '0']]
        for instance in Pawn.instances:
            if instance.team == 'top' and instance.alive:
                board[instance.location[1]][instance.location[0]] = '1'
            elif instance.team == 'bottom' and instance.alive:
                board[instance.location[1]][instance.location[0]] = '2'
        ai.alph.inform(''.join(board[0]) + ''.join(board[1]) + ''.join(board[2]))

        # get alph's move and execute it
        ai.alph.choose()
        selection.select(ai.alph.get_selection()[0], ai.alph.get_selection()[1])
        selection.select(ai.alph.get_target()[0], ai.alph.get_target()[1])

pygame.quit()
quit()
