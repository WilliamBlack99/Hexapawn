try:
    import random
    from datetime import datetime
except BaseException as e:
    print('failed to import module: ' + str(e))
random.seed(datetime.time)

# an AI object can take board data, make decisions, and learn from the results
class AI:
    def __init__(self):

        # self.board is what the ai believes the current board to look like
        # the first 3 digits represent the top row, the next 3 represent the middle row, and the last 3 represent the bottom row
        # ones represent the ai's pawns, twos represent the player's pawns, and zeroes represent empty squares
        # refered to as "board format"
        self.board = '000000000'

        # self.choice is the ai's intended move
        # the first two digits are the x and y coordinates respectively of the pawn the ai wants to move
        # the second two digits are the x and y coordinates respectively of the location the ai wants to move a pawn to
        # refered to as "choice format"
        self.choice = '0000'

        # self.scenarios contains a list of all board positions in board format encountered throughout the game
        self.scenarios = []

        # self.decisions contains a list of all choices in choice format the ai made throughout the game
        # any index in self.scenarios will give the corresponding choice if used in self.decisions and vice versa
        self.decisions = []

        # self.memory is a dictionary where the keys are possible board positions in board format
        # the items are lists
        # each list contains at least one list containing a possible choice in choice format and a "score" corresponding to how likely the ai is to make that choice
        self.memory = {'111200022':[['1001', 1], ['1011', 1], ['2021', 1]], \
 '111020202':[['0001', 1], ['0011', 1], ['2011', 1], ['2021', 1]], \
 '111002220':[['0001', 1], ['1011', 1], ['1021', 1]], \
 '101200002':[['2021', 1]], \
 '101120002':[['0011', 1], ['2011', 1], ['0102', 1]], \
 '101102020':[['0102', 1], ['0112', 1]], \
 '101220020':[['0011', 1], ['2011', 1], ['2021', 1]], \
 '110221002':[['0011', 1], ['1001', 1]], \
 '110202002':[['1001', 1], ['1011', 1], ['1021', 1]], \
 '011122200':[['1021', 1], ['2011', 1]], \
 '011210002':[['1001', 1], ['2021', 1], ['1112', 1]], \
 '011020002':[['2011', 1], ['2021', 1]], \
 '011020200':[['2011', 1], ['2021', 1]], \
 '011012200':[['1021', 1], ['1112', 1]], \
 '110210002':[['1001', 1], ['1112', 1]], \
 '110020002':[['0001', 1], ['0011', 1]], \
 '110020200':[['0001', 1], ['0011', 1]], \
 '110012200':[['0001', 1], ['1021', 1], ['1102', 1], ['1112', 1]], \
 '110221002':[['0011', 1], ['1001', 1]], \
 '011202200':[['1001', 1], ['1011', 1], ['1021', 1]], \
 '011122200':[['1021', 1], ['2011', 1]], \
 '101022020':[['0001', 1], ['0011', 1], ['2011', 1]], \
 '101201020':[['2112', 1], ['2122', 1]], \
 '101021200':[['0001', 1], ['0011', 1], ['2011', 1], ['2122', 1]], \
 '101002200':[['0001', 1]], \
 '001120000':[['2001', 1], ['2021', 1], ['0102', 1]], \
 '001112000':[['0102', 1], ['1112', 1]], \
 '100120000':[['0011', 1], ['0102', 1]], \
 '100112000':[['0102', 1], ['1112', 1]], \
 '100222000':[['0011', 1]], \
 '010221000':[['1001', 1], ['2122', 1]], \
 '010122000':[['1021', 1], ['0102', 1]], \
 '010012000':[['1021', 1], ['1112', 1]], \
 '010210000':[['1001', 1], ['1112', 1]], \
 '001211000':[['1112', 1], ['2122', 1]], \
 '001021000':[['2011', 1], ['2122', 1]], \
 '100211000':[['1112', 1], ['2122', 1]], \
 '100021000':[['0001', 1], ['0011', 1], ['2122', 1]], \
 '001222000':[['2011', 1]]}

    # return the location of the pawn the ai wants to move
    def get_selection(self):
        return (int(self.choice[0]), int(self.choice[1]))

    # return the location of where the ai wants to move a pawn
    def get_target(self):
        return (int(self.choice[2]), int(self.choice[3]))

    # store the current state of the board in board format
    def inform(self, data):
        self.board = data

    # make a decision as to the ai's next move
    def choose(self):

        # a list with possible choices the ai can make. identical choices will appear more than once or not at all depending on how likely the ai is to choose it
        options = [] 
        for option in self.memory[self.board]:
            for i in range(option[1]):
                options.append(option[0])     # fill the options list with choices
                
        if not options:                       # if there are no choices punish the ai for being in a situation with only losing moves then fill options with said moves
            self.punish()                      
            for option in self.memory[self.board]:
                options.append(option[1])

        # choose randomly from options and store the board data and choice data 
        self.choice = random.choice(options)
        self.scenarios.append(self.board)
        self.decisions.append(self.choice)

    # increase the score of all moves made this game
    def reward(self):
        for i in range(len(self.decisions)):
            for option in self.memory[self.scenarios[i]]:
                if option[0] == self.decisions[i]:
                    option[1] += 1
                    print('reward', option[1])
        self.decisions = []
        self.scenarios = []

    # decrease the score of the last move made this game
    def punish(self):
        for option in self.memory[self.scenarios[-1]]:
            if option[0] == self.decisions[-1]:
                option[1] -= 1
                print('punish', option[1])

# initialize the ai
alph = AI()
