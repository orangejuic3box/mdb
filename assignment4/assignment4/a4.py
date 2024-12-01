# CMPUT 455 Assignment 4 starter code
# Implement the specified commands to complete the assignment
# Full assignment specification here: https://webdocs.cs.ualberta.ca/~mmueller/courses/cmput455/assignments/a4.html

import sys
import random
import signal

# Custom time out exception
class TimeoutException(Exception):
    pass

# Function that is called when we reach the time limit
def handle_alarm(signum, frame):
    raise TimeoutException

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
            "timelimit": self.timelimit
        }
        self.board = [[None]]
        self.player = 1
        self.max_genmove_time = 1
        signal.signal(signal.SIGALRM, handle_alarm)

    #====================================================================================================================
    # VVVVVVVVVV Start of predefined functions. You may modify, but make sure not to break the functionality. VVVVVVVVVV
    #====================================================================================================================    
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

    def is_legal(self, x, y, num):
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
    
    def valid_move(self, x, y, num):
        if  x >= 0 and x < len(self.board[0]) and\
                y >= 0 and y < len(self.board) and\
                (num == 0 or num == 1):
            legal, _ = self.is_legal(x, y, num)
            return legal

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
        legal, reason = self.is_legal(x, y, num)
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
                    legal, _ = self.is_legal(x, y, num)
                    if legal:
                        moves.append([str(x), str(y), str(num)])
        return moves

    def winner(self, args):
        if len(self.get_legal_moves()) == 0:
            if self.player == 1:
                print(2)
            else:
                print(1)
        else:
            print("unfinished")
        return True

    def timelimit(self, args):
        self.max_genmove_time = int(args[0])
        return True

    #===============================================================================================
    # ɅɅɅɅɅɅɅɅɅɅ End of predefined functions. ɅɅɅɅɅɅɅɅɅɅ
    #===============================================================================================

    #===============================================================================================
    # VVVVVVVVVV Start of Assignment 4 functions. Add/modify as needed. VVVVVVVV
    #===============================================================================================
    def boolean_negamax(self, depth):
        if depth == 0:
            return False  # Cannot guarantee a win at this depth limit

        board_hash = self.hash_board()
        if board_hash in self.transposition_table:
            return self.transposition_table[board_hash]

        if len(self.get_legal_moves()) == 0:
            # No moves left, current player loses
            self.transposition_table[board_hash] = False #set board hash to false
            return False

        moves = self.get_legal_moves()
        moves.sort(key=lambda move: self.evaluate_move_priority(move), reverse=True)

        for move in moves:
            self.make_move(move)
            result = not self.boolean_negamax(depth - 1)
            self.undo_move(move)
            if result:
                self.transposition_table[board_hash] = True
                return True

        self.transposition_table[board_hash] = False
        return False

    def make_move(self, move):
        x, y, num = int(move[0]), int(move[1]), int(move[2])
        self.board[y][x] = num

    def undo_move(self, move):
        x, y, num = int(move[0]), int(move[1]), int(move[2])
        self.board[y][x] = None

    def hash_board(self):
        return str(self.board)

    def evaluate_move_priority(self, move):
        x, y, num = int(move[0]), int(move[1]), int(move[2])
        score = 0

        # Center Control (Encourage staying close to the center)
        center_x, center_y = len(self.board[0]) // 2, len(self.board) // 2
        if x == center_x and y == center_y:
            score += 10
        elif abs(x - center_x) <= 1 and abs(y - center_y) <= 1:
            score += 5  # Reward for being close to the center

        # Prefer balanced moves
        zeros = sum(row.count(0) for row in self.board)
        ones = sum(row.count(1) for row in self.board)
        imbalance = abs(zeros - ones)
        score -= imbalance ** 1.5  # Exponentially scale penalty for imbalance

        return score

    def genmove(self, args):
        try:
            # Set the time limit alarm
            signal.alarm(self.max_genmove_time)
            
            # Modify the following to give better moves than random play 
            moves = self.get_legal_moves()
            if len(moves) == 0:
                print("resign")
                return True
            best_move = None
            depth = 1
            print("         GENMOVE FOR PLAYER")
            while True:
                print("depth:", depth)
                curr_best_move = None

                self.transposition_table = {}

                moves.sort(key=lambda move: self.evaluate_move_priority(move), reverse=True)

                for move in moves:
                    self.make_move(move)
                    if not self.boolean_negamax(depth - 1):
                        curr_best_move = move
                        self.undo_move(move)    
                        break
                    self.undo_move(move)

                if curr_best_move:
                    best_move = curr_best_move
                    break

                depth += 1

                # Stop if time running out?

            if best_move:
                self.play(best_move)
                print(" ".join(best_move))
            else:
                # No winning move found, random move
                rand_move = moves[random.randint(0, len(moves) - 1)]
                self.play(rand_move)
                print(" ".join(rand_move))



            # Disable the time limit alarm 
            signal.alarm(0)

        except TimeoutException:
            # This block of code runs when the time limit is reached
            print("resign")

        return True
    
    #===============================================================================================
    # ɅɅɅɅɅɅɅɅɅɅ End of Assignment 4 functions. ɅɅɅɅɅɅɅɅɅɅ
    #===============================================================================================
    
if __name__ == "__main__":
    interface = CommandInterface()
    interface.main_loop()