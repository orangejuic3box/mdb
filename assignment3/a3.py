# CMPUT 455 Assignment 3 starter code
# Implement the specified commands to complete the assignment
# Full assignment specification here: https://webdocs.cs.ualberta.ca/~mmueller/courses/cmput455/assignments/a3.html

import sys
import random
import os

class CommandInterface:

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
            "loadpatterns" : self.loadpatterns,
            "policy_moves" : self.policy_moves
        }
        self.board = [[None]]
        self.player = 1
        self.patterns = {}
    
    #===============================================================================================
    # VVVVVVVVVV START of PREDEFINED FUNCTIONS. DO NOT MODIFY. VVVVVVVVVV
    #===============================================================================================

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
    # Every command will print '= 1' or '= -1' at the end of execution to indicate success or failure respectively
    def main_loop(self):
        while True:
            str = input()
            if str.split(" ")[0] == "exit":
                print("= 1\n")
                return True
            if self.process_command(str):
                print("= 1\n")

    # Will make sure there are enough arguments, and that they are valid numbers
    # Not necessary for commands without arguments
    def arg_check(self, args, template):
        converted_args = []
        if len(args) < len(template.split(" ")):
            print("Not enough arguments.\nExpected arguments:", template, file=sys.stderr)
            print("Recieved arguments: ", end="", file=sys.stderr)
            for a in args:
                print(a, end=" ", file=sys.stderr)
            print(file=sys.stderr)
            return False
        for i, arg in enumerate(args):
            try:
                converted_args.append(int(arg))
            except ValueError:
                print("Argument '" + arg + "' cannot be interpreted as a number.\nExpected arguments:", template, file=sys.stderr)
                return False
        args = converted_args
        return True

    # List available commands
    def help(self, args):
        for command in self.command_dict:
            if command != "help":
                print(command)
        print("exit")
        return True

    #===============================================================================================
    # ɅɅɅɅɅɅɅɅɅɅ END OF PREDEFINED FUNCTIONS. ɅɅɅɅɅɅɅɅɅɅ
    #===============================================================================================

    #===============================================================================================
    # VVVVVVVVVV START OF ASSIGNMENT 3 FUNCTIONS. ADD/REMOVE/MODIFY AS NEEDED. VVVVVVVV
    #===============================================================================================

    def game(self, args):
        if not self.arg_check(args, "n m"):
            return False
        n, m = [int(x) for x in args]
        if n < 0 or m < 0:
            print("Invalid board size:", n, m, file=sys.stderr)
            return False
        
        self.board = []
        for i in range(m):
            self.board.append([None]*n)
        self.player = 1
        return True
    
    def show(self, args):
        for row in self.board:
            for x in row:
                if x is None:
                    print(".", end="")
                else:
                    print(x, end="")
            print()                    
        return True

    def is_legal_reason(self, x, y, num):
        if self.board[y][x] is not None:
            return False, "occupied"
        
        consecutive = 0
        count = 0
        self.board[y][x] = num
        for row in range(len(self.board)):
            if self.board[row][x] == num:
                count += 1
                consecutive += 1
                if consecutive >= 3:
                    self.board[y][x] = None
                    return False, "three in a row"
            else:
                consecutive = 0
        too_many = count > len(self.board) // 2 + len(self.board) % 2
        
        consecutive = 0
        count = 0
        for col in range(len(self.board[0])):
            if self.board[y][col] == num:
                count += 1
                consecutive += 1
                if consecutive >= 3:
                    self.board[y][x] = None
                    return False, "three in a row"
            else:
                consecutive = 0
        if too_many or count > len(self.board[0]) // 2 + len(self.board[0]) % 2:
            self.board[y][x] = None
            return False, "too many " + str(num)

        self.board[y][x] = None
        return True, ""
    
    def is_legal(self, x, y, num):
        if self.board[y][x] is not None:
            return False
        
        consecutive = 0
        count = 0
        self.board[y][x] = num
        for row in range(len(self.board)):
            if self.board[row][x] == num:
                count += 1
                consecutive += 1
                if consecutive >= 3:
                    self.board[y][x] = None
                    return False
            else:
                consecutive = 0
        if count > len(self.board) // 2 + len(self.board) % 2:
            self.board[y][x] = None
            return False
        
        consecutive = 0
        count = 0
        for col in range(len(self.board[0])):
            if self.board[y][col] == num:
                count += 1
                consecutive += 1
                if consecutive >= 3:
                    self.board[y][x] = None
                    return False
            else:
                consecutive = 0
        if count > len(self.board[0]) // 2 + len(self.board[0]) % 2:
            self.board[y][x] = None
            return False

        self.board[y][x] = None
        return True
    
    def valid_move(self, x, y, num):
        return  x >= 0 and x < len(self.board[0]) and\
                y >= 0 and y < len(self.board) and\
                (num == 0 or num == 1) and\
                self.is_legal(x, y, num)

    def play(self, args):
        err = ""
        if len(args) != 3:
            print("= illegal move: " + " ".join(args) + " wrong number of arguments\n")
            return False
        try:
            x = int(args[0])
            y = int(args[1])
        except ValueError:
            print("= illegal move: " + " ".join(args) + " wrong coordinate\n")
            return False
        if  x < 0 or x >= len(self.board[0]) or y < 0 or y >= len(self.board):
            print("= illegal move: " + " ".join(args) + " wrong coordinate\n")
            return False
        if args[2] != '0' and args[2] != '1':
            print("= illegal move: " + " ".join(args) + " wrong number\n")
            return False
        num = int(args[2])
        legal, reason = self.is_legal_reason(x, y, num)
        if not legal:
            print("= illegal move: " + " ".join(args) + " " + reason + "\n")
            return False
        self.board[y][x] = num
        if self.player == 1:
            self.player = 2
        else:
            self.player = 1
        return True
    
    def legal(self, args):
        if not self.arg_check(args, "x y number"):
            return False
        x, y, num = [int(x) for x in args]
        if self.valid_move(x, y, num):
            print("yes")
        else:
            print("no")
        return True
    
    def get_legal_moves(self):
        moves = []
        for y in range(len(self.board)):
            for x in range(len(self.board[0])):
                for num in range(2):
                    if self.is_legal(x, y, num):
                        moves.append([str(x), str(y), str(num)])
        return moves

    def genmove(self, args):
        moves = self.get_legal_moves()
        if len(moves) == 0:
            print("resign")
        else:
            rand_move = moves[random.randint(0, len(moves)-1)]
            self.play(rand_move)
            print(" ".join(rand_move))
        return True
    
    def winner(self, args):
        if len(self.get_legal_moves()) == 0:
            if self.player == 1:
                print(2)
            else:
                print(1)
        else:
            print("unfinished")
        return True
    
    # new function to be implemented for assignment 3
    def loadpatterns(self, args):
        '''
        First, delete all existing patterns in your program. 
        Then, load all the new patterns from the file given by filename, 
        and use all these patterns for your policy from now on. 
        When your program first starts up, there should be no patterns loaded.
        '''
        try:
            assert len(args) == 1
            filename = args[0]
            with open(filename, "r") as f:
                # only clear patterns if filename was valid
                self.patterns = {}
                for line in f:
                    line = line.strip()
                    if line.startswith("#") or not line:
                        continue  # Ignore comments and empty lines
                    parts = line.split()
                    if len(parts) == 3:
                        pattern, move, weight = parts
                        if pattern in self.patterns:
                            self.patterns[pattern][move] = int(weight) # adding this move and weight to the pattern
                        else:
                            self.patterns[pattern] = { move : int(weight) } # nested dictionary!!!!
                    #error checking
                    #else:
                        #print(f"Skipping malformed line: {line}")
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found.")
        except AssertionError:
            print("Error: expected 1 argument, got", len(args), "instead")
        except Exception as e:
            print(e)
        # print(self.patterns)
        return True
    
    def get_pattern(self,x, y):
        '''
        This function gets the surrounded 5 length pattern such that
        the middle of the pattern is the x,y coordinate.
        Altered code from A1 from the triplet function.
        '''
        row = ''
        col = ''
        # print(x, y)
        for i in range(-2, 3):
            try:
                if x+i < 0:
                    raise IndexError
                pos = self.board[y][x+i]
                if pos == None:
                    row += "."
                else:
                    row += str(pos)
            except IndexError:
                row += "X"
            try:
                if y+i < 0:
                    raise IndexError
                pos = self.board[y+i][x]
                if pos == None:
                    col += "."
                else:
                    col += str(pos)
            except IndexError:
                col += "X"
        # print("ROW PATTERN:", row)
        # print("COL PATTERN:", col)
        return row, col

    # new function to be implemented for assignment 3
    def policy_moves(self, args):
        '''
        This command should print a sorted list of all legal moves and their probabilities, 
        rounded to at most three digits after the decimal point, 
        for the current simulation policy in the format
        move1 prob1 move2 prob2 ... ... moven probn
        x y digit prob x y digit prob
        '''
        moves = self.get_legal_moves()
        weights = {} #dictionary because moves have to be sorted, key is str version of the listed move, value is weight
        total = 0
        for move in moves:
            #generates the row and column pattern for the given (x,y) coordinate
            row_pat, col_pat = self.get_pattern(int(move[0]), int(move[1]))
            #reverse each pattern so we can see in all directions
            row_reversed = row_pat[::-1]
            col_reversed = col_pat[::-1] 
            #list of listed row patterns and listed column patterns for for loop formatting (tongue twister)
            possible_patterns = [[row_pat, row_reversed], [col_pat, col_reversed]]
            weight = 0
            for rowcol in possible_patterns:
                flag = True #for default weight
                for p in rowcol:
                    if p in self.patterns:
                        flag = False #no longer degault weight
                        weight += self.patterns[p][move[2]]
                        break #break if its the first one
                if flag: #default weight if neither pattern was in the row or col
                    weight += 10
            total += weight
            weights[str(move)] = weight
        #sorts moves based on x then y then digit
        sorted_moves = sorted(moves, key=lambda x: (int(x[0]), int(x[1]), int(x[2])))
        str_prtout = ""
        for i in range(len(moves)):
            #grabs move weight and divides by total
            #then adds move and probability to the string for printout
            move = sorted_moves[i]
            x, y, digit = move
            prob = weights[str(move)]/total
            prob = str(round(prob, 3))
            str_prtout += x + " " + y + " " + digit + " " + prob + " "
        print(str_prtout.rstrip())
        return True
    
    #===============================================================================================
    # ɅɅɅɅɅɅɅɅɅɅ END OF ASSIGNMENT 3 FUNCTIONS. ɅɅɅɅɅɅɅɅɅɅ
    #===============================================================================================
    
if __name__ == "__main__":
    interface = CommandInterface()
    interface.main_loop()