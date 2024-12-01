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

        self.ztable = None
        self.current_hash = 0
    
    #====================================================================================================================
    # VVVVVVVVVV Start of predefined functions. You may modify, but make sure not to break the functionality. VVVVVVVVVV
    #====================================================================================================================
    #region all the non game functions:
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
        
        #mags:
        self.make_ztable(m,n)
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

    def is_legal(self, x, y, num):
        '''
        Returns:
            - legal (bool) either True or False is the move legal?
            - reason (str) if legal = False, gives the reason why
        same as is_legal_reason in a2 just has the print statements
        '''
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
        #checks bounds but doesn't do return anything
        # if outside bounds, this is fine bc in self.play()
        # illegal moves are checked anyways before this is called
        if  x >= 0 and x < len(self.board[0]) and\
                y >= 0 and y < len(self.board) and\
                (num == 0 or num == 1):
            legal, _ = self.is_legal(x, y, num) #boolean, str reason if false
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
        #mags:
        self.current_hash ^= self.ztable[y][x][num]
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
    def make_ztable(self, row, col):
        # 0, 1, 2 (EMPTY/None) -> range(3)
        # print(row, "rows")
        # print(col, "columns")
        self.ztable = [[[random.getrandbits(64) for _ in range(3)] for _ in range(col)] for _ in range(row)]

    def add_to_tt(self, board_key, move, win):
        '''
        Takes in hashvalue of the board, move, and win_value from playing that move,
        puts it into the transposition table for easy lookup
        '''
        if len(self.tt) < 1000000:
            self.tt[board_key] = (move, win)

    def quick_play(self, move):
        '''
        Plays one move on the board, switches the player
        Always make sure to undo
        '''
        self.board[int(move[1])][int(move[0])] = int(move[2])
        self.current_hash ^= self.ztable[int(move[1])][int(move[0])][int(move[2])]
        self.player = 3 - self.player

    def undo(self, move):
        '''
        Changes the board value to None, (erasing the move)
        Switches the player
        '''
        self.board[int(move[1])][int(move[0])] = None
        self.current_hash ^= self.ztable[int(move[1])][int(move[0])][int(move[2])]
        self.player = 3 - self.player
   
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
                return True
            elif winner == 3 - player:
                return False
            else:
                return "winner was not p1 or p2"
        return "game was not over"

    def boolean_negamax(self, player):
        '''
        Return:
            - is_won (bool) can you win from your spot
            - best_move (List[str, str, str]) [x,y,num]
        '''
        #deal with time limit???
        # if time.time() - self.start_time > self.time_limit:
        #     return "unknown", None

        # get dictionary key
        board_key = self.current_hash
        #if seen this board position, return move, value
        if board_key in self.tt:
            return self.tt[board_key] #what is this returning??
        #else, get all legal moves
        legal_moves = self.get_legal_moves()
        #if no legal moves left, 
        # add move and value to transposition table
        # declare no moves and the winner
        #RETURN no moves and the winner
        if not legal_moves:
            return self.evaluate_board(player), None

            """ #if current player is p1, winner = p2
            if self.player == 1:
                self.add_to_tt(board_key, None, 2)
                return None, 2
            else:
                self.add_to_tt(board_key, None, 1)
                return None, 1 """
        best_move = None
        is_won = False
        #else for each move, do a quick play to find best move
        #STOP quick play after finding a winning move
        #undo the move you just played
        #add move and winner to transposition table
        #return the move and current player as the winner
        for move in legal_moves:
            self.quick_play(move) #play the move on the board and switch players
            win, _ = self.boolean_negamax(self.player) #keep playing until end of game or timeout
            self.undo(move)
            #timelimit???
            # if win == "unknown":
            #     return "unknown", None
        
            win = not win
            if win == True:
                is_won = True
                best_move = move
                break
        self.tt[board_key] = is_won
        return is_won, best_move

    def genmove(self, args):
        #get all legal moves
        moves = self.get_legal_moves()
        if len(moves) == 0:
            print("resign")
            return True
        #make a copy of board
        player_copy = self.player
        board_copy = []
        for row in self.board:
            board_copy.append(list(row))
        try:
            # Set the time limit alarm
            signal.alarm(self.max_genmove_time)            
            # Attempt to find a winning move by solving the board
            #make new empty transposition table, hash, ztable
            self.tt = {}
            win, move = self.boolean_negamax()
            # Disable the time limit alarm 
            signal.alarm(0)

        except TimeoutError:
            move = moves[random.randint(0, len(moves)-1)]
        self.board = board_copy #board from before, makes sure not to use the board for search
        self.player = player_copy
        self.play(move)
        print(" ".join(move))

        return True
    
    #===============================================================================================
    # ɅɅɅɅɅɅɅɅɅɅ End of Assignment 4 functions. ɅɅɅɅɅɅɅɅɅɅ
    #===============================================================================================
    
if __name__ == "__main__":
    interface = CommandInterface()
    interface.main_loop()