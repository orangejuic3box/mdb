# CMPUT 455 Assignment 1 starter code
# Implement the specified commands to complete the assignment
# Full assignment specification here: https://webdocs.cs.ualberta.ca/~mmueller/courses/cmput455/assignments/a1.html

import sys
import math

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
            "place" : self.place,
            "griddy" : self.griddy
        }
        self.grid = None
        self.height = None
        self.width = None
        # do i set empty self.grid, self.height, self.width??

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
        # Check if valid integers were given for grid size
        try:
            width = int(args[0])
            height = int(args[1])

            # If valid grid size, create grid
            if 1 <= width <= 20 and 1 <= height <= 20:
                self.grid = [["." for _ in range(width)] for _ in range(height)]
                self.height = height
                self.width = width
                return True

            else:
                print("Error: Grid width and height must be between 1 and 20.")
                return False
        
        # Raise exception if invalid arguments are given for grid size
        except:
            print("Error: Invalid input for grid size.")
            return False
    
    def show(self, args):
        # Display grid if it exists
        try:
            for row in self.grid:
                print("".join(row))
            return True
        
        # Raise exception if no grid exists
        except Exception as e:
            print(e)
            print("Error: No game exists.")
            return False
    
    def play(self, args):
        raise NotImplementedError("This command is not yet implemented.")
        return True
    
    def place(self,args):
        ''' Helper Function for legal purposes'''
        # just places the digit at x y in the grid
        x = int(args[0])
        y = int(args[1])
        digit = args[2]

        self.grid[y][x] = digit
        # print(self.grid)
        print("placed")
        return True
    
    def griddy(self,args):
        # creates a grid of the given size and just numbers each position increasingly, for testing purposes
        self.width = int(args[0])
        self.height = int(args[1])
        self.grid = [[str((i * self.width) + j )for j in range(self.width)] for i in range(self.height)]
        # print(self.grid)
        return True

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
        row_max = math.ceil(self.height/2)
        col_max = math.ceil(self.width/2)
        # getting row and column
        row = self.get_row(y)
        col = self.get_col(x)
        # checking balance
        # print("digit", digit)
        # print("row", row, row.count(digit), row_max)
        # print("col", col, col.count(digit), col_max)
        if row.count(digit) != row_max and col.count(digit) != col_max: #technically count should never be above the max, so checking that its != is the same as checking less than
            # print("passed balance check")
            return True
        # print("failed balance check")
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
            return False
        return True
    
    
    def legal(self, args):
        # Check if this move (in the same format as in play) is legal. 
        # Answer yes or no. 
        # The command status is = 1.
        
        # Triple contraint: no 3 consecutive digits in ROW or COLUMN
        # Balance constraint: the max number of playable digits is half the size of its ROW and COLUMN (rounded up)
        '''This function checks the user inputs and then checks if the game
        constraints hold given the supposed play. Triple constraint is only
        looked at if the width of the grid is greater than 3.'''
        
        try:
            x = int(args[0]) # column
            y = int(args[1]) # row
            # checks for index within bound
            if x not in range(self.width) or y not in range(self.height):
                raise IndexError
            digit = args[2]

            # only check triples if width is greater than 3
            if self.width > 3:
                if self.balance(x, y, digit) and self.triple(x, y, digit):
                    print("yes")
                else:
                    print("no")
            else:
                if self.balance(x, y, digit):
                    print("yes")
                else:
                    print("no")
            return True
        except IndexError:
            print("Error: Index position out of bounds.")
            return False
        except TypeError as e:
            print(e)
            print("Error: Game does not exist.")
            return False
        except Exception as e:
            print(e)
            print("Error: Invalid arguments for legal command.\nMust be in format: x y digit")
            return False
    
    def genmove(self, args):
        raise NotImplementedError("This command is not yet implemented.")
        return True
    
    def winner(self, args):
        raise NotImplementedError("This command is not yet implemented.")
        return True
    
    #======================================================================================
    # End of functions requiring implementation
    #======================================================================================

if __name__ == "__main__":
    interface = CommandInterface()
    interface.main_loop()