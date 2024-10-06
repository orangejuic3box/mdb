# CMPUT 455 Assignment 2 starter code
# Implement the specified commands to complete the assignment
# Full assignment specification here: https://webdocs.cs.ualberta.ca/~mmueller/courses/cmput455/assignments/a2.html

import sys
import random

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
        self.timelimit = 1
    
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
    # VVVVVVVVVV START OF ASSIGNMENT 2 FUNCTIONS. ADD/REMOVE/MODIFY AS NEEDED. VVVVVVVV
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
    
    # new function to be implemented for assignment 2
    def timelimit(self, args):
        if not args or len(args) != 1:
            print("timelimit requires one argument")
            return False
        try:
            seconds = int(args[0])
            if 1 <= seconds <= 100:
                self.time_limit = seconds
                return True
            else:
                print("timelimit must be between 1 and 100")
                return False
        except ValueError:
            print("timelimit requires an integer argument")
            return False
    
    # new function to be implemented for assignment 2
    def solve(self, args):
        import time

        start_time = time.time()
        time_limit = self.time_limit

        best_move = None
        winner = 'unknown'

        depth = 1
        root_player = self.player

        while True:
            # Check if time limit exceeded
            elapsed_time = time.time() - start_time
            if elapsed_time >= time_limit:
                break

            # Initialize alpha and beta
            alpha = -float('inf')
            beta = float('inf')

            # Call alphabeta at current depth
            value, move = self.alphabeta(depth, alpha, beta, root_player, start_time, time_limit)

            if value is None:
                # Time limit exceeded during search
                break

            if value == 1:
                winner = str(root_player)
                best_move = move
                break
            elif value == -1:
                winner = str(3 - root_player)
                best_move = None
                break
            elif value == 0:
                # Continue to next depth
                pass

            # Increase depth for iterative deepening
            depth += 1

        if winner == 'unknown':
            print("unknown")
        else:
            if best_move:
                print(winner, ' '.join(str(m) for m in best_move))
            else:
                print(winner)

        return True

def alphabeta(self, depth, alpha, beta, maximizing_player, start_time, time_limit):
    import time

    # Check for time limit
    if time.time() - start_time >= time_limit:
        return None, None  # Indicate that time limit was exceeded

    # Check for terminal node
    if self.is_game_over():
        # Return evaluation of terminal node
        winner = self.get_winner()
        if winner == maximizing_player:
            return 1, None  # Maximizing player wins
        elif winner == 3 - maximizing_player:
            return -1, None  # Opponent wins
        else:
            return 0, None  # Draw or unknown

    if depth == 0:
        # Return heuristic evaluation
        return 0, None  # For now, we can return 0

    # Get legal moves
    moves = self.get_legal_moves()

    # If no legal moves, game is over
    if not moves:
        winner = self.get_winner()
        if winner == maximizing_player:
            return 1, None
        elif winner == 3 - maximizing_player:
            return -1, None
        else:
            return 0, None

    best_move = None

    if self.player == maximizing_player:
        # Maximizing player
        value = -float('inf')
        for move in moves:
            # Check time limit
            if time.time() - start_time >= time_limit:
                return None, None
            # Make move
            self.make_move(move)
            v, _ = self.alphabeta(depth - 1, alpha, beta, maximizing_player, start_time, time_limit)
            # Undo move
            self.undo_move(move)
            if v is None:
                return None, None  # Time limit exceeded
            if v > value:
                value = v
                if depth == 1:
                    best_move = move
            alpha = max(alpha, value)
            if alpha >= beta:
                break  # Beta cut-off
        return value, best_move
    else:
        # Minimizing player
        value = float('inf')
        for move in moves:
            if time.time() - start_time >= time_limit:
                return None, None
            self.make_move(move)
            v, _ = self.alphabeta(depth - 1, alpha, beta, maximizing_player, start_time, time_limit)
            self.undo_move(move)
            if v is None:
                return None, None
            if v < value:
                value = v
                if depth == 1:
                    best_move = move
            beta = min(beta, value)
            if alpha >= beta:
                break  # Alpha cut-off
        return value, best_move

def make_move(self, move):
    x, y, num = int(move[0]), int(move[1]), int(move[2])
    self.board[y][x] = num
    # Update player
    if self.player == 1:
        self.player = 2
    else:
        self.player = 1

def undo_move(self, move):
    x, y, num = int(move[0]), int(move[1]), int(move[2])
    self.board[y][x] = None
    # Update player back
    if self.player == 1:
        self.player = 2
    else:
        self.player = 1

def is_game_over(self):
    return len(self.get_legal_moves()) == 0

def get_winner(self):
    if self.is_game_over():
        # The player who is not to move wins
        return 3 - self.player
    else:
        return None
    
    #===============================================================================================
    # ɅɅɅɅɅɅɅɅɅɅ END OF ASSIGNMENT 2 FUNCTIONS. ɅɅɅɅɅɅɅɅɅɅ
    #===============================================================================================
    
if __name__ == "__main__":
    interface = CommandInterface()
    interface.main_loop()