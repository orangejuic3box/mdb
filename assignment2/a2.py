# CMPUT 455 Assignment 2 starter code
# Implement the specified commands to complete the assignment
# Full assignment specification here: https://webdocs.cs.ualberta.ca/~mmueller/courses/cmput455/assignments/a2.html

import sys
import random
import time
import cProfile

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
            "timelimit" : self.timelimit,
            "solve" : self.solve
        }
        self.board = [[None]]
        self.player = 1
        self.time_limit = 1
        self.moves = []
        self.transposition_table = {}

        #new hashing?
        self.ztable = None
        self.current_hash = 0    
    #===============================================================================================
    # VVVVVVVVVV START of PREDEFINED FUNCTIONS. DO NOT MODIFY. VVVVVVVVVV
    #===============================================================================================
    #region
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
    #endregion
    #===============================================================================================
    # ɅɅɅɅɅɅɅɅɅɅ END OF PREDEFINED FUNCTIONS. ɅɅɅɅɅɅɅɅɅɅ
    #===============================================================================================

    #===============================================================================================
    # VVVVVVVVVV START OF ASSIGNMENT 2 FUNCTIONS. ADD/REMOVE/MODIFY AS NEEDED. VVVVVVVV
    #===============================================================================================

    def make_ztable(self, row, col):
        # 0, 1, 2 (EMPTY/None) -> range(3)
        # print(row, "rows")
        # print(col, "columns")
        self.ztable = [[[random.getrandbits(64) for _ in range(3)] for _ in range(col)] for _ in range(row)]

    def game(self, args):
        if not self.arg_check(args, "n m"):
            return False
        n, m = [int(x) for x in args]
        if n < 0 or m < 0:
            print("Invalid board size:", n, m, file=sys.stderr)
            return False

        self.make_ztable(m, n)
        self.current_hash = 0

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
        self.current_hash ^= self.ztable[y][x][num]
        # print("urp")
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
    
    def undo(self):
        if not self.moves:
            return
        x, y, num = self.moves.pop()
        self.board[y][x] = None
        self.current_hash ^= self.ztable[y][x][num]
        self.player = 3 - self.player
    
    # new function to be implemented for assignment 2
    def timelimit(self, args):
        self.time_limit = int(args[0])
        return True
    
    # new function to be implemented for assignment 2
    def solve(self, args):
        # og_player = self.player
        self.transposition_table = {}
        self.start_time = time.time()

        win, best_move = self.boolean_negamax(self.player)

        if win == "unknown":
            print(win)
        if win == True:
            print(f"{self.player} {best_move[0]} {best_move[1]} {best_move[2]}")
        if win == False:
            print(3-self.player)
            
        return True
    
    # functions for assignment 2
    def game_over(self):
        if len(self.get_legal_moves()) == 0:
            return True
        return False
    
    def winner_is(self):
        if not self.game_over():
            return None
        return 3 - self.player
            
    def evaluate_board(self, player):
        if self.game_over():
            winner = self.winner_is()
            if winner == player:
                return True#10
            elif winner == 3 - player:
                return False #-10
            else:
                return 0
        return 0
    
    def boolean_negamax(self, player):
        '''
        Return:
            - WINNER (1, 2 or unknown)
            - BEST MOVE [x, y, num]
        '''
        if time.time() - self.start_time > self.time_limit:
            return "unknown", None

        # get dictionary key
        board_key = self.current_hash

        # if key exists in table already return the value from the table
        if board_key in self.transposition_table:
            return self.transposition_table[board_key], None
        
        # grab all legal moves to explore
        legal_moves = self.get_legal_moves()

        # if there no legal moves left, GAME OVER, return the winner
        if not legal_moves:
            return self.evaluate_board(player), None

        best_move = None
        is_won = False
        
        for move in legal_moves:
            # unpack move
            x, y, num = move

            self.play(move) #self.player switches here
            self.moves.append((int(x), int(y), int(num)))

            win, _ = self.boolean_negamax(self.player)

            self.undo() #self.player switches here

            if win == "unknown":
                return "unknown", None
            
            win = not win

            if win == True:
                is_won = True
                best_move = move
                break

        self.transposition_table[board_key] = is_won
        return is_won, best_move

    #===============================================================================================
    # ɅɅɅɅɅɅɅɅɅɅ END OF ASSIGNMENT 2 FUNCTIONS. ɅɅɅɅɅɅɅɅɅɅ
    #===============================================================================================
    
if __name__ == "__main__":
    interface = CommandInterface()
    interface.main_loop()