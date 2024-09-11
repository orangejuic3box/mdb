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
        row_max = math.ceil(self.height/2)
        col_max = math.ceil(self.width/2)
        row = self.get_row(y)
        col = self.get_col(x)
        
        # checking balance
        if row.count(digit) != row_max and col.count(digit) != col_max:
            print("passed balance check")
            return True
        print("failed balance check")
        return False
    
    
    def legal(self, args):
        # raise NotImplementedError("This command is not yet implemented.")
        # Check if this move (in the same format as in play) is legal. 
        # Answer yes or no. 
        # The command status is = 1.
        
        # Triple contraint: no 3 consecutive digits in ROW or COLUMN
        # Balance constraint: the max number of playable digits is half the size of its ROW and COLUMN (rounded up)

        try:
            print("converting arguments")
            x = int(args[0]) # column
            y = int(args[1]) # row
            digit = args[2]
            print("converted")
            # Goes to the row and checks both constraints

            '''given x y look at that position as
            x y, x+1, y, x+2 y
            x-1 y, x y, x+1 y
            x-2 y, x-1 y, x y'''

            self.balance(x,y, digit)

            # row = self.grid[y]
            # for i in range(self.width):
            #     # print("i is", i)
            #     # Case: grid width is 3 or smaller
            #     if self.width <= 3:
            #         if self.width == 1:
            #             # print("width is 1")
            #             print(row[i])
            #         if self.width == 2:
            #             # print("width is 2")
            #             print(row[i], row[i+1])
            #         if self.width == 3:
            #             # print("width is 3")
            #             print(row[i], row[i+1], row[i+2])
            #         break
            #     # Case: grid width bigger than 3
            #     if i < self.width-2: # need to test this against width 1, 2, 3
            #         # print(i, width-2)
            #         consec = [row[i], row[i+1], row[i+2]]
            #         # print(row[i], row[i+1], row[i+2])
            #         print(consec)

            #     else:
            #         print("Width is 0")
            #         break
            # Goes to the column and checks both constraints
            return True
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