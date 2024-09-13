# CMPUT 455 Assignment 1 starter code
# Implement the specified commands to complete the assignment
# Full assignment specification here: https://webdocs.cs.ualberta.ca/~mmueller/courses/cmput455/assignments/a1.html

import sys
import math
import random

class CommandInterface:
    # The following is already defined and does not need modification
    # However, you may change or add to this code as you see fit, e.g. adding class variables to init

    def __init__(self):
        # Define the string to function command mapping
        self.command_dict = {
            "help" : self.help,
            "game" : self.game,
            "show" : self.show,
            "play" : self.play,
            "legal" : self.legal,
            "genmove" : self.genmove,
            "winner" : self.winner,
            "place" : self.place
            # "griddy" : self.griddy
        }
        self.grid = None
        self.height = None
        self.width = None
        self.player_one = True
        self.end_of_game = False

    # Convert a raw string to a command and a list of arguments
    def process_command(self, str):
        str = str.lower().strip()
        command = str.split(" ")[0]
        args = [x for x in str.split(" ")[1:] if len(x) > 0]
        if command not in self.command_dict:
            print("? Uknown command.\nType 'help' to list known commands.", file=sys.stderr)
            print("= -1\n")
            return False
        try:
            return self.command_dict[command](args)
        except Exception as e:
            print("Command '" + str + "' failed with exception:", file=sys.stderr)
            print(e, file=sys.stderr)
            print("= -1\n")
            return False
        
    # Will continuously receive and execute commands
    # Commands should return True on success, and False on failure
    # Commands will automatically print '= 1' at the end of execution on success
    def main_loop(self):
        while True:
            str = input()
            if str.split(" ")[0] == "exit":
                print("= 1\n")
                return True
            if self.process_command(str):
                print("= 1\n")
                

    # List available commands
    def help(self, args):
        for command in self.command_dict:
            if command != "help":
                print(command)
        print("exit")
        return True

    #======================================================================================
    # End of predefined functionality. You will need to implement the following functions.
    # Arguments are given as a list of strings
    # We will only test error handling of the play command
    #======================================================================================

    def game(self, args):
        '''This function initiates a new game on an empty rectangular grid, given by
        the user, with width n and height m (in the range from 1 and 20). Formatting
        of the input must be in the format: n m.'''
        width = int(args[0])
        height = int(args[1])

        # Create grid with user specified width and height
        self.grid = [["." for _ in range(width)] for _ in range(height)]
        self.height = height
        self.width = width
        return True
    
    def show(self, args):
        '''This function shows the current state of the grid.'''
        # Display grid
        for row in self.grid:
            print("".join(row))
        return True
    
    def play(self, args):
        '''This function allows players to place a digit (0 or 1) at a given
        coordinate (x, y). The coordinate x increases from left to right, starting
        at 0, and y increases from top to bottom, starting at 0. Formatting of
        a play must be in the format: x y digit.'''
        # Check if move is legal to place digit on grid
        try:
            if self.legal(args) and self.player_one:
                self.place(args)
                self.player_one = False
                return True
            elif self.legal(args) and not self.player_one:
                self.place(args)
                self.player_one = True
                return True

        # Raise exception if illegal move
        except Exception as e:
            # print(e)
            print("= illegal move : {} invalid input\n".format(' '.join(args)))
            return False
    
    def place(self,args):
        ''' Helper Function for legal purposes'''
        # just places the digit at x y in the grid
        x = int(args[0])
        y = int(args[1])
        digit = args[2]

        self.grid[y][x] = digit
        # print(self.grid)
        # print("placed")
        return True
    
    # def griddy(self,args):
    #     # creates a grid of the given size and just numbers each position increasingly, for testing purposes
    #     self.width = int(args[0])
    #     self.height = int(args[1])
    #     self.grid = [[str((i * self.width) + j )for j in range(self.width)] for i in range(self.height)]
    #     # print(self.grid)
    #     return True

    def get_row(self,y):
        # returns a List object of the row
        row = self.grid[y]
        return row
    
    def get_col(self,x):
        # returns a List object of the column
        col = []
        for j in range(self.height):
            col.append(self.grid[j][x])
        return col

    def balance(self, x, y, digit):
        # Balance constraint: the max number of playable digits is half the size of its ROW and COLUMN (rounded up)
        '''This function finds the max number of playable digits, gets the row
        and column of the given play position and checks the count of the given
        play (digit) in its row or column for the balance constraint. 
        Returns True or False.'''
        # getting max values for row and column
        row_max = math.ceil(self.width/2)
        col_max = math.ceil(self.height/2)
        # getting row and column
        row = self.get_row(y)
        col = self.get_col(x)
        # checking balance
        # print("digit", digit)
        # print("row", row, row.count(digit), row_max)
        # print("col", col, col.count(digit), col_max)
        if row.count(digit) < row_max and col.count(digit) < col_max: #technically count should never be above the max, so checking that its != is the same as checking less than
            # print("passed balance check")
            return True
        # print("failed balance check")
        else:
            print("= illegal move: {} {} {} too many {}\n".format(x, y, digit, digit))
            return False

    def triple(self, x, y, digit):
        # Triple contraint: no 3 consecutive digits in ROW or COLUMN
        '''This function gathers the possible collection of the consecutive
        positions around the given play position into a string. Inserts the 
        supposed play (digit) into that string and then checks if the triple
        constraint is being violated. If given position is close to the border,
        handles the IndexError for out of bound positions and continues on. 
        Returns True or False.'''

        # print("triple chair")
        row = ''
        col = ''
        for i in range(-2, 3):
            # print("i is", i)
            # inserts supposed play (digit) into the row and column to be checked
            if i == 0:
                row += digit
                col += digit
            # gets the value from the current grid in position
            else:
                try:
                    if x+i >=0:
                        row += self.grid[y][x+i]
                except IndexError:
                    # print("row failed")
                    pass
                try:
                    if y+i >=0:
                        col += self.grid[y+i][x]
                except IndexError:
                    # print("col failed")
                    pass
        # print("col", col)
        # print("row", row)

        check = digit*3
        # print(check)
        # print(check in row, "row")
        # print(check in col, "col")
        if check in row or check in col:
            # print("invalid play for 3's")
            print("= illegal move: {} {} {} three in a row\n".format(x, y, digit))
            return False
        return True
    
    
    def legal(self, args):
        # Check if this move (in the same format as in play) is legal. 
        # Answer yes or no. 
        # The command status is = 1.
        
        # Triple constraint: no 3 consecutive digits in ROW or COLUMN
        # Balance constraint: the max number of playable digits is half the size of its ROW and COLUMN (rounded up)
        '''This function checks the user inputs and then checks if the game
        constraints hold given the supposed play. Triple constraint is only
        looked at if the width of the grid is greater than 3.'''
        
        try:
            # check if # of args is correct
            if len(args) != 3:
                print("= illegal move: {} wrong number of arguments\n".format(' '.join(args)))
                return False
            
            x = int(args[0]) # column
            y = int(args[1]) # row
            # checks for index within bound
            if x not in range(self.width) or y not in range(self.height):
                print("= illegal move: {} wrong coordinate\n".format(' '.join(args)))
                return False
            digit = args[2]

            # check if digit is valid (0 or 1)
            if digit not in ["0", "1"]:
                print("= illegal move: {} wrong number\n".format(' '.join(args)))
                return False
            
            # check if cell occupied
            if self.grid[y][x] != ".":
                print("= illegal move: {} occupied\n".format(' '.join(args)))
                return False

            # only check triples if width is greater than 3
            if self.width > 3:
                if self.balance(x, y, digit) and self.triple(x, y, digit):
                    # print("yes")
                    pass
                else:
                    # print("no")
                    return False
            else:
                if self.balance(x, y, digit):
                    # print("yes")
                    pass
                else:
                    # print("no")
                    return False
            return True
        except TypeError as e:
            print(e)
            print("Error: Game does not exist.\n")
            return False
        except Exception as e:
            print(e)
            print("Error: Invalid arguments for legal command.\nMust be in format: x y digit\n")
            return False
    
    def genmove(self, args):
        try:
            moves = []

            # Find all legal moves by checking all empty cells
            for y in range(self.height):
                for x in range(self.width):
                    if self.grid[y][x] == ".":
                        for digit in ["0", "1"]:
                            # Check if move is legal to place digit on grid
                            if self.legal([x, y, digit]):
                                moves.append([x, y, digit])
            
            # If no legal moves, resign
            if len(moves) == 0:
                print("resign\n")
                self.end_of_game = True
                return False
            
            # Otherwise, select and play a random legal move
            move = random.choice(moves)
            x = str(move[0])
            y = str(move[1])
            digit = move[2]
            self.play([x, y, digit])
            print("{} {} {}".format(x, y, digit))
            return True
        
        except Exception as e:
            print("Error: Game does not exist.\n")
            return False
    
    def winner(self, args):
        '''This function checks if the game is over. If it is, determine which player
        is the winner.'''
        if self.player_one and self.end_of_game:
            print("1")
            return True
        elif not self.player_one and self.end_of_game:
            print("2")
            return True
        else:
            print("unfinished")
            return True
    
    #======================================================================================
    # End of functions requiring implementation
    #======================================================================================

if __name__ == "__main__":
    interface = CommandInterface()
    interface.main_loop()