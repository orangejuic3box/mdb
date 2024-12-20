# CMPUT 455 Assignment 4 starter code
# Implement the specified commands to complete the assignment
# Full assignment specification here: https://webdocs.cs.ualberta.ca/~mmueller/courses/cmput455/assignments/a4.html

import sys
import random
import signal
import math
import time

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
            "timelimit": self.timelimit,
            "random": self.random
        }
        self.board = [[None]]
        self.player = 1
        self.max_genmove_time = 1
        signal.signal(signal.SIGALRM, handle_alarm)

        self.ztable = None
        self.current_hash = 0
        self.n = 0
        self.m = 0
    
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
            print(f"exception as e for command {command}: {e}")
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
        self.tt = {}
        self.n = n
        self.m = m

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
    def random(self, args):
        # Get all legal moves
        moves = self.get_legal_moves()
        # If empty, resign
        if len(moves) == 0:
            print("resign")
        # else, pick random one and play it
        else:
            rand_move = moves[random.randint(0, len(moves)-1)]
            self.play(rand_move)
            print(" ".join(rand_move))
        return True

    def get_depth(self):
        depth = 0
        for row in self.board:
            depth += sum(1 for x in row if x in {0, 1})
        return depth
            
    def make_ztable(self, row, col):
        # 0, 1, 2 (EMPTY/None) -> range(3)
        # print(row, "rows")
        # print(col, "columns")
        self.ztable = [[[random.getrandbits(64) for _ in range(3)] for _ in range(col)] for _ in range(row)]

    def add_to_tt(self, board_key, total, n):
        '''
        Takes in hashvalue of the board, move, and win_value from playing that move,
        puts it into the transposition table for easy lookup
        '''
        if len(self.tt) < 1000000:
            self.tt[board_key] = [total, n]
        
    def update_tt(self, state, value):
        total, n = self.tt[state]
        if total == float("inf"):
            total = value
        else:
            total += value
        n += 1
        self.tt[state] = [total, n]

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
            return "game not over"
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

    def adaptive_c(self, depth, max_depth, printit=False):
        if printit:
            print(depth, max_depth)
        initial_c = 1.41  # High exploration at root
        final_c = 0.5  # Lower value for deeper nodes
        return initial_c + (final_c - initial_c) * (depth / max_depth)

    def ucb1(self, state, N, C, printit=False):
        total, n = self.tt[state]
        if n == 0 or N ==0: #child has not been seen
            return float("inf")
        v = total/n
        ln = math.log(N)
        sq_rt = math.sqrt(ln/n)
        ucb = v + C * sq_rt
        if printit:
            print(v, total, n)
            print(ln, N)
            print(sq_rt)
            print(ucb)
        return ucb

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

    def rollout(self):
        '''
        Rollout(si):
            loop forever: #potentially change this?
                if si is a terminal state:
                    return value(si)
                ai = random(legal_moves(si))
                si = quick_play(ai) #simulate the move
        '''
        original_player = self.player
        original_board = []
        original_hash = self.current_hash
        for row in self.board:
            original_board.append(list(row))
        i = 0
        while True:
            if i > 10000:
                print("so many rollouts")
                return "too many rollouts"
            moves = self.get_legal_moves()
            if not moves: #no more moves to play, terminal
                break
            #RANDOM POLICY
            # move = random.choice(moves)
            #MOVE PRIORITY POLICY
            # moves.sort(key=lambda move: self.evaluate_move_priority(move), reverse=True)
            move = max(moves, key=self.evaluate_move_priority)

            self.quick_play(move)
            i += 1
        #check who the winner is
        winner = self.winner_is()
        if winner == original_player:
            value = 1
        else:
            value =  0
        #reset everything
        self.board = original_board
        self.player = original_player
        self.current_hash = original_hash
        return value

    def maximize_ucb(self, child_states, N, printit=False):
        ucb_values = {}
        for child in child_states:
            c = self.adaptive_c(self.get_depth(), self.n*self.m)
            ucb_values[child] = self.ucb1(child, N, c)
        max_child = max(ucb_values, key=ucb_values.get) #mags: change this to choose random child if same ucb values
        max_value = max(ucb_values)
        return max_child, max_value

    def is_leaf_node(self, state):
        '''
        n = 0 OR no child nodes in the tree
        '''
        _, n = self.tt[state]
        if n == 0:
            return True
        moves = self.get_legal_moves()
        child_states, _ = self.get_children(moves) #_ = move_child, we dont need it here
        for child in child_states:
            if child in self.tt:
                return False
        return True
    
    def propogate(self, path_to_leaf, value, printit=False):
        '''
        Backpropogate value(si) by adding it to the t-val and add 1 to each n to the leafnode it came from and up until the start state
        '''
        if printit:
            print("BACKPROPGATION")
        while path_to_leaf != []:
            self.update_tt(self.current_hash, value)
            move = path_to_leaf.pop()
            self.undo(move)
            if printit:
                print("undoing move...", move)
        if printit:
            print(self.current_hash, "should be the root")
        #should be at the root now
        self.update_tt(self.current_hash, value)

    def find_best_move(self, move_child:dict, child_states:list, printit=False):
        if printit:
            print("find bestie--------------")
        # Initialize variables for the best child and its value
        best_child = None
        best_value = -float('inf')  # Start with a very small value
        # Iterate over child_states and check their values in tt
        for child in child_states:
            if child in self.tt:  # Check if the child is present in tt
                total, n = self.tt[child]
                if n == 0:
                    continue
                value = total/n
                if printit:
                    print(f"{child}: [{total}, {n}]")
                if value > best_value: #this will pick the last child with the best val
                    best_child = child
                    best_value = value
        if best_child == None:
            raise Exception("child state is empty or no child could be found in tt")
        best_move = move_child[best_child]
        if printit:
            print("best move best child best value", best_move, best_child, best_value)
        return best_move

    def get_children(self, moves):
        child_states = []
        move_child = {}
        for move in moves:
            self.quick_play(move)
            child_states.append(self.current_hash)
            move_child[self.current_hash] = move
            self.undo(move)
        return child_states, move_child

    def selection(self, current, printit=False):
        moves = self.get_legal_moves()
        child_states, move_child = self.get_children(moves)
        in_the_tree = set(child_states).intersection(self.tt.keys())
        """ print("currenthash", self.current_hash)
        print(len(child_states), "children")
        print(len(self.tt), "nodes in the tree") """

        #pick maximizing ucb1 child
        N = self.tt[current][1]
        best_child, highest_ucb_score = self.maximize_ucb(in_the_tree, N)
        best_move = move_child[best_child]
        if printit:
            print("child with highest ucb score is ", best_child, "with move", best_move, "and score", highest_ucb_score)
        return best_child, best_move

    def expand(self, moves):
        for move in moves:
            self.quick_play(move)
            self.tt[self.current_hash] = [float("inf"), 0] #add new nodes
            self.undo(move)
        return random.choice(moves)

    def mcts(self, printit=False):
        '''
        1. Tree traversal: UCB(si) = avg(vi) + C*sqrt[ln(N)/ni], C=2
            - choose child that maximizes this formula
        2. Node Expansion
        3. Rollout (random simulation)
        4. Backpropogation
        '''
        if printit:
            print("root state:",self.current_hash)
        if self.current_hash not in self.tt:
            #put root into tree
            self.tt[self.current_hash] = [float("inf"), 0]
        moves = self.get_legal_moves()
        child_states, move_child = self.get_children(moves)
        #always expand root
        #(1) SELECTION
        # is current state a leaf node?
        path_to_leaf = []
        while not self.is_leaf_node(self.current_hash):
            #there is a path further down
            best_child, best_move = self.selection(self.current_hash)
            self.quick_play(best_move)
            path_to_leaf.append(best_move)
            if printit:
                print(f"curr: {self.current_hash}")
                self.show("")
                print(f"move: {best_move}")
            assert self.current_hash == best_child, "did not go to the right kid"
        if printit:
            print("leafnode found!", self.is_leaf_node(self.current_hash), self.current_hash)
        total, n = self.tt[self.current_hash]
        if n == 0:
            #(2) NODE EXPANSION
            moves = self.get_legal_moves()
            if moves: #there are nodes to expand!!
                move = self.expand(moves)
                self.quick_play(move)
                path_to_leaf.append(move)
        if printit:
            print("THE PATH TRAVELLED")
            print(path_to_leaf)
        #(3)SIMULATION
        value = self.rollout() #resets the board to what it was from the rollout
        if printit:
            print("random rollout was", value)
        #(4)BACKPROPOGATION
        self.propogate(path_to_leaf, value)
        #keep doing this until time runs out?

        best_move = self.find_best_move(move_child, child_states)
        if printit:
            print("ALMOST OVER")
            # self.show("")
            # print(self.tt)
            # print("mc", move_child)
            # print()
            # print("cs", child_states)
            print("the best move so far is", best_move)
        return best_move

    def genmove(self, args):
        start_time = time.time()
        time_limit = self.max_genmove_time
        # Set the time limit alarm
        signal.alarm(self.max_genmove_time)  
        #get all legal moves
        moves = self.get_legal_moves()
        if len(moves) == 0:
            print("resign")
            return True
        # #make a copy of board
        # player_copy = self.player
        # board_copy = []
        # for row in self.board:
        #     board_copy.append(list(row))
        try:          
            # Attempt to find a winning move by solving the board
            while time.time() - start_time < (2/3)*time_limit:
                move = self.mcts()
            # Disable the time limit alarm 
            signal.alarm(0)
        except TimeoutError:
            # print("rah timeout, getting random move")
            move = moves[random.randint(0, len(moves)-1)]
            signal.alarm(0)
        except Exception as e:
            signal.alarm(0)
        # print("done mcts", time.time()-start_time)
        # print(self.current_hash)
        # print(self.board == board_copy, self.player == player_copy, "was it the same??")
        # self.board = board_copy #board from before, makes sure not to use the board for search
        # self.player = player_copy
        self.play(move)
        print(" ".join(move))

        return True
    
    #===============================================================================================
    # ɅɅɅɅɅɅɅɅɅɅ End of Assignment 4 functions. ɅɅɅɅɅɅɅɅɅɅ
    #===============================================================================================
    
if __name__ == "__main__":
    interface = CommandInterface()
    interface.main_loop()