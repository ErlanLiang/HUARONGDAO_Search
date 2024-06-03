from copy import deepcopy
from heapq import heappush, heappop
import time
import argparse
import sys

#====================================================================================

char_goal = '1'
char_single = '2'

class Piece:
    """
    This represents a piece on the Hua Rong Dao puzzle.
    """

    def __init__(self, is_goal, is_single, coord_x, coord_y, orientation):
        """
        :param is_goal: True if the piece is the goal piece and False otherwise.
        :type is_goal: bool
        :param is_single: True if this piece is a 1x1 piece and False otherwise.
        :type is_single: bool
        :param coord_x: The x coordinate of the top left corner of the piece.
        :type coord_x: int
        :param coord_y: The y coordinate of the top left corner of the piece.
        :type coord_y: int
        :param orientation: The orientation of the piece (one of 'h' or 'v') 
            if the piece is a 1x2 piece. Otherwise, this is None
        :type orientation: str
        """

        self.is_goal = is_goal
        self.is_single = is_single
        self.coord_x = coord_x
        self.coord_y = coord_y
        self.orientation = orientation
        self.shape = (2, 2) if is_goal else (1, 2) if orientation == 'h' else (2, 1) if orientation == 'v' else (1, 1)

    def __repr__(self):
        return '{} {} {} {} {}'.format(self.is_goal, self.is_single, \
            self.coord_x, self.coord_y, self.orientation)
    
    def __eq__(self, value: object) -> bool:
        return self.is_goal == value.is_goal and self.is_single == value.is_single and \
            self.coord_x == value.coord_x and self.coord_y == value.coord_y and \
            self.orientation == value.orientation
    
    def __hash__(self) -> int:
        return hash((self.is_goal, self.is_single, self.coord_x, self.coord_y, self.orientation))

class Board:
    """
    Board class for setting up the playing board.
    """

    def __init__(self, pieces):
        """
        :param pieces: The list of Pieces
        :type pieces: List[Piece]
        """

        self.width = 4
        self.height = 5

        self.pieces = pieces
        self.empty = [None, None] # The empty space on the board
        # self.grid is a 2-d (size * size) array automatically generated
        # using the information on the pieces when a board is being created.
        # A grid contains the symbol for representing the pieces on the board.
        self.grid = []
        self.__construct_grid()

    def __hash__(self):
        return hash(tuple(tuple(row) for row in self.grid))

    def __eq__(self, other):
        return self.grid == other.grid


    def __construct_grid(self):
        """
        Called in __init__ to set up a 2-d grid based on the piece location information.

        """

        for i in range(self.height):
            line = []
            for j in range(self.width):
                line.append('.')
            self.grid.append(line)

        for piece in self.pieces:
            if piece.is_goal:
                self.grid[piece.coord_y][piece.coord_x] = char_goal
                self.grid[piece.coord_y][piece.coord_x + 1] = char_goal
                self.grid[piece.coord_y + 1][piece.coord_x] = char_goal
                self.grid[piece.coord_y + 1][piece.coord_x + 1] = char_goal
            elif piece.is_single:
                self.grid[piece.coord_y][piece.coord_x] = char_single
            else:
                if piece.orientation == 'h':
                    self.grid[piece.coord_y][piece.coord_x] = '<'
                    self.grid[piece.coord_y][piece.coord_x + 1] = '>'
                elif piece.orientation == 'v':
                    self.grid[piece.coord_y][piece.coord_x] = '^'
                    self.grid[piece.coord_y + 1][piece.coord_x] = 'v'
        
        # update the empty space
        count = 0
        for i in range(self.height):
            for j in range(self.width):
                if self.grid[i][j] == '.':
                    self.empty[count] = (j, i) 
                    count += 1
                    if count == 2:
                        break

    def display(self):
        """
        Print out the current board.

        """
        for i, line in enumerate(self.grid):
            for ch in line:
                print(ch, end='')
            print()
    
    def heuristic(self):
        """
        Calculate the heuristic value of a state. The heuristic function is the Manhattan distance
        between the goal piece and the exit.
        """
        for piece in self.pieces:
            if piece.is_goal:
                return abs(piece.coord_x - 1) + abs(piece.coord_y - 3)
        return 0


class State:
    """
    State class wrapping a Board with some extra current state information.
    Note that State and Board are different. Board has the locations of the pieces. 
    State has a Board and some extra information that is relevant to the search: 
    heuristic function, f value, current depth and parent.
    """

    def __init__(self, board, f, depth, parent=None):
        """
        :param board: The board of the state.
        :type board: Board
        :param f: The f value of current state.
        :type f: int
        :param depth: The depth of current state in the search tree.
        :type depth: int
        :param parent: The parent of current state.
        :type parent: Optional[State]
        """
        self.board = board
        self.f = f
        self.depth = depth
        self.parent = parent
        self.id = hash(board)  # The id for breaking ties.
    
    def __lt__(self, other):
        return self.f < other.f  # Compare based on f value

class DFS:
    """
    Game class for the Hua Rong Dao puzzle.
    """

    def __init__(self, initial_board):
        """
        :param initial_board: The initial board of the game.
        :type initial_board: Board
        """
        self.width = 4
        self.height = 5
        self.current_state = State(initial_board, 1, 0)
        self.visited = set()
        self.visited.add(self.current_state.id)
        self.frontier = [self.current_state]    
    
    def human_play(self):
        """
        Play the game manually.

        """
        while True:
            if self.current_state.board.heuristic() == 0:
                break
            print("===========================================================")
            self.current_state.board.display()
            print("current id: ", self.current_state.id)
            print("visited: ", len(self.visited))
            print("frontier: ", len(self.frontier))
            print("=====================================")
            actions = self.get_actions()
            print("Possible moves: ")
            for i, action in enumerate(actions):
                print(i)
                action.board.display()
                self.frontier.append(action)
            print("Enter your move: ")
            move = input()
            self.current_state = actions[int(move)]
            
            self.frontier.remove(self.current_state)
            print("=====================================")


        print("You win!")
        return
    
    def dfs(self):
        """
        Perform depth-first search.

        """
        while self.frontier:
            
            self.current_state = self.frontier.pop()

            # print("===========================================================")
            # self.current_state.board.display()
            # print("visited: ", len(self.visited))
            # print("frontier: ", len(self.frontier))
            # if len(self.frontier) < 50:
            #     for i in range(len(self.frontier)):
            #         print()
            #         print(i, " Frontier: ")
            #         self.frontier[i].board.display()
            #         print("empty: ", self.frontier[i].board.empty)

            if self.current_state.board.heuristic() == 0:
                print("Depth: ", self.current_state.depth)
                self.print_solution()     
                return
            
            
            # self.visited.add(self.current_state.id)
            actions = self.get_actions()
            for action in actions:
                self.frontier.append(action)
        print("No solution found.")
        return None
        #     self.visited.add(self.current_state.id)
        #     self.get_actions()
        #     # for action in actions:
        #     #     if action.id:
        #     #         self.frontier.append(action)
        #     #         self.visited.add(action.id)
        # return None
    
    def print_solution(self):
        """
        Print out the solutions
        """
        count = 0
        path = []
        while self.current_state:
            path.append(self.current_state)
            self.current_state = self.current_state.parent
        path.reverse()
        for state in path:
            count += 1
            print("Step: ", count)
            state.board.display()
            print()
        return   

    def get_actions(self):
        """
        Get all possible actions that can be taken from the current state.

        :return: A list of possible state.
        :rtype: List[State]
        """
        actions = []
        empty_spaces = self.current_state.board.empty
        directions = {'up': (0, -1), 'down': (0, 1), 'left': (-1, 0), 'right': (1, 0)}
        for ex, ey in empty_spaces:
            # print("ex: ", ex, "ey: ", ey)
            for direction, (dx, dy) in directions.items():
                nx, ny = ex + dx, ey + dy
                if 0 <= nx < self.width and 0 <= ny < self.height and self.current_state.board.grid[ny][nx] != '.':
                    # print("=====================================")
                    # print("nx: ", nx, "ny: ", ny)
                    piece = self.get_piece_at(nx, ny)
                    # print("piece: ", piece.coord_x, ", ", piece.coord_y)
                    # print("direction: ", direction)
                    new_board = self.move_piece(piece, direction)
                    # if new_board:
                    #     new_board.board.display()
                    #     print("empty: ", new_board.board.empty)
                    if new_board and new_board.id not in self.visited:
                        # print("added")
                        self.visited.add(new_board.id)
                        actions.append(new_board)

        return actions
    
    def get_piece_at(self, x, y):
        for piece in self.current_state.board.pieces:
            if piece.is_goal and (x, y) in [(piece.coord_x, piece.coord_y), (piece.coord_x + 1, piece.coord_y),
                                            (piece.coord_x, piece.coord_y + 1), (piece.coord_x + 1, piece.coord_y + 1)]:
                return piece
            elif piece.is_single and (x, y) == (piece.coord_x, piece.coord_y):
                return piece
            elif piece.orientation == 'h' and (x, y) in [(piece.coord_x, piece.coord_y), (piece.coord_x + 1, piece.coord_y)]:
                return piece
            elif piece.orientation == 'v' and (x, y) in [(piece.coord_x, piece.coord_y), (piece.coord_x, piece.coord_y + 1)]:
                return piece
        return None
    
    def move_piece(self, piece, direction):
        new_pieces = deepcopy(self.current_state.board.pieces)
        empty_spaces = deepcopy(self.current_state.board.empty)
        for p in new_pieces:
            if p == piece:
                if direction == 'down' and p.coord_y > 0:
                    new_empty1 = (p.coord_x, p.coord_y + p.shape[0] - 1) # the first empty space after moving
                    new_empty2 = (p.coord_x + p.shape[1] - 1, p.coord_y + p.shape[0] - 1) # the second empty space after moving
                    if (p.coord_x, p.coord_y - 1) in empty_spaces: # check if the first empty space is empty
                        empty_spaces.remove((p.coord_x, p.coord_y - 1)) # remove the first empty space
                        empty_spaces.append(new_empty1) # add the new empty space
                        p.coord_y -= 1
                elif direction == 'up' and p.coord_y + p.shape[0] < self.height:
                    new_empty1 = (p.coord_x, p.coord_y )
                    new_empty2 = (p.coord_x + p.shape[1] - 1, p.coord_y)
                    # print("new_empty1: ", new_empty1)
                    # print("new_empty2: ", new_empty2)
                    if (p.coord_x, p.coord_y + p.shape[0]) in empty_spaces:
                        empty_spaces.remove((p.coord_x, p.coord_y + p.shape[0]))
                        empty_spaces.append(new_empty1)
                        p.coord_y += 1
                elif direction == 'right' and p.coord_x > 0:
                    new_empty1 = (p.coord_x + p.shape[1] - 1, p.coord_y)
                    new_empty2 = (p.coord_x + p.shape[1] - 1, p.coord_y + p.shape[0] - 1)
                    if (p.coord_x - 1, p.coord_y) in empty_spaces:
                        empty_spaces.remove((p.coord_x - 1, p.coord_y))
                        empty_spaces.append(new_empty1)
                        p.coord_x -= 1
                elif direction == 'left' and p.coord_x + p.shape[1] < self.width:
                    new_empty1 = (p.coord_x, p.coord_y)
                    new_empty2 = (p.coord_x, p.coord_y + p.shape[0] - 1)
                    if (p.coord_x + p.shape[1], p.coord_y) in empty_spaces:
                        empty_spaces.remove((p.coord_x + p.shape[1], p.coord_y))
                        empty_spaces.append(new_empty1)
                        p.coord_x += 1
                else:
                    return None

                if is_valid(new_pieces):
                    new_board = Board(new_pieces)
                    for x, y in empty_spaces:
                        if new_board.grid[y][x] != '.':
                            empty_spaces.remove((x, y))
                            empty_spaces.append(new_empty2)
                    new_board.empty = empty_spaces
                    return State(new_board, 1, self.current_state.depth + 1, self.current_state)
        return None

class AStar:
    """
    Game class for the Hua Rong Dao puzzle.
    """

    def __init__(self, initial_board):
        """
        :param initial_board: The initial board of the game.
        :type initial_board: Board
        """
        self.width = 4
        self.height = 5
        self.current_state = State(initial_board, self.heuristic(initial_board), 0)
        self.visited = set()
        self.visited.add(self.current_state.id)
        self.frontier = []    
        heappush(self.frontier, self.current_state)
    
    def heuristic(self, board: Board):
        return self.linear_conflict(board) + board.heuristic()

    def linear_conflict(self, board):
        # Example implementation of linear conflict
        conflicts = 0
        caocao = None
        for piece in board.pieces:
            if piece.is_goal:
                caocao = piece
                break
        
        if caocao:
            goal_x, goal_y = 1, 3
            if caocao.coord_y < goal_y:  
                for row in range(caocao.coord_y + 2, goal_y + 1):
                    for col in range(caocao.coord_x, caocao.coord_x + 2):
                        if board.grid[row][col] != '.':
                            conflicts += 1
            if caocao.coord_x < goal_x:  
                for col in range(caocao.coord_x + 2, goal_x + 1):
                    for row in range(caocao.coord_y, caocao.coord_y + 2):
                        if board.grid[row][col] != '.':
                            conflicts += 1
        return conflicts * 2  
    
    def human_play(self):
        """
        Play the game manually.
        """
        while True:
            if self.heuristic(self.current_state.board) == 0:
                break
            self.current_state = heappop(self.frontier)
            self.visited.add(self.current_state.id)
            print("===========================================================")
            self.current_state.board.display()
            print("current id: ", self.current_state.id)
            print("frontier: ", len(self.frontier)  )
            print("visited: ", len(self.visited))
            print("=====================================")
            actions = self.get_actions()
            for action in actions:
                if action.id not in self.visited:
                    heappush(self.frontier, action)
            print("Possible moves: ")
            for action in self.frontier:
                print("F: ", action.f)
                action.board.display()
            i = int(input("Enter your move: "))
        print("You win!")
        return
    
    def astar(self):
        """
        Perform depth-first search.

        """

        while self.frontier:
            # print()
            # self.current_state.board.display()
            # print("visited: ", len(self.visited))
            # print("frontier: ", len(self.frontier))
            self.current_state = heappop(self.frontier)

            if self.heuristic(self.current_state.board) == 0:
                print("Depth: ", self.current_state.depth)
                self.print_solution()     
                return
            self.visited.add(self.current_state.id)
            actions = self.get_actions()
            for action in actions:
                if action.id not in self.visited:
                    heappush(self.frontier, action)
                    self.visited.add(action.id)
                    
        return None
    
    def print_solution(self):
        """
        Print out the solution.

        """
        count = 0
        path = []
        while self.current_state:
            path.append(self.current_state)
            self.current_state = self.current_state.parent
        path.reverse()
        for state in path:
            count += 1
            print("Step: ", count)
            state.board.display()
            print()
        return

    def get_actions(self):
        """
        Get all possible actions that can be taken from the current state.

        :return: A list of possible state.
        :rtype: List[State]
        """
        actions = []
        empty_spaces = self.current_state.board.empty
        directions = {'up': (0, -1), 'down': (0, 1), 'left': (-1, 0), 'right': (1, 0)}
        for ex, ey in empty_spaces:
            # print("ex: ", ex, "ey: ", ey)
            for direction, (dx, dy) in directions.items():
                nx, ny = ex + dx, ey + dy
                if 0 <= nx < self.width and 0 <= ny < self.height and self.current_state.board.grid[ny][nx] != '.':
                    # print("=====================================")
                    # print("nx: ", nx, "ny: ", ny)
                    piece = self.get_piece_at(nx, ny)
                    # print("piece: ", piece.coord_x, ", ", piece.coord_y)
                    # print("direction: ", direction)
                    new_board = self.move_piece(piece, direction)
                    # if new_board:
                    #     new_board.board.display()
                    #     print("empty: ", new_board.board.empty)
                    if new_board and new_board.id not in self.visited:
                        # print("added")
                        # self.visited.add(new_board.id)
                        actions.append(new_board)

        return actions
    
    def get_piece_at(self, x, y):
        for piece in self.current_state.board.pieces:
            if piece.is_goal and (x, y) in [(piece.coord_x, piece.coord_y), (piece.coord_x + 1, piece.coord_y),
                                            (piece.coord_x, piece.coord_y + 1), (piece.coord_x + 1, piece.coord_y + 1)]:
                return piece
            elif piece.is_single and (x, y) == (piece.coord_x, piece.coord_y):
                return piece
            elif piece.orientation == 'h' and (x, y) in [(piece.coord_x, piece.coord_y), (piece.coord_x + 1, piece.coord_y)]:
                return piece
            elif piece.orientation == 'v' and (x, y) in [(piece.coord_x, piece.coord_y), (piece.coord_x, piece.coord_y + 1)]:
                return piece
        return None
    
    def move_piece(self, piece, direction):
        new_pieces = deepcopy(self.current_state.board.pieces)
        empty_spaces = deepcopy(self.current_state.board.empty)
        for p in new_pieces:
            if p == piece:
                if direction == 'down' and p.coord_y > 0:
                    new_empty1 = (p.coord_x, p.coord_y + p.shape[0] - 1) # the first empty space after moving
                    new_empty2 = (p.coord_x + p.shape[1] - 1, p.coord_y + p.shape[0] - 1) # the second empty space after moving
                    if (p.coord_x, p.coord_y - 1) in empty_spaces: # check if the first empty space is empty
                        empty_spaces.remove((p.coord_x, p.coord_y - 1)) # remove the first empty space
                        empty_spaces.append(new_empty1) # add the new empty space
                        p.coord_y -= 1
                elif direction == 'up' and p.coord_y + p.shape[0] < self.height:
                    new_empty1 = (p.coord_x, p.coord_y )
                    new_empty2 = (p.coord_x + p.shape[1] - 1, p.coord_y)
                    # print("new_empty1: ", new_empty1)
                    # print("new_empty2: ", new_empty2)
                    if (p.coord_x, p.coord_y + p.shape[0]) in empty_spaces:
                        empty_spaces.remove((p.coord_x, p.coord_y + p.shape[0]))
                        empty_spaces.append(new_empty1)
                        p.coord_y += 1
                elif direction == 'right' and p.coord_x > 0:
                    new_empty1 = (p.coord_x + p.shape[1] - 1, p.coord_y)
                    new_empty2 = (p.coord_x + p.shape[1] - 1, p.coord_y + p.shape[0] - 1)
                    if (p.coord_x - 1, p.coord_y) in empty_spaces:
                        empty_spaces.remove((p.coord_x - 1, p.coord_y))
                        empty_spaces.append(new_empty1)
                        p.coord_x -= 1
                elif direction == 'left' and p.coord_x + p.shape[1] < self.width:
                    new_empty1 = (p.coord_x, p.coord_y)
                    new_empty2 = (p.coord_x, p.coord_y + p.shape[0] - 1)
                    if (p.coord_x + p.shape[1], p.coord_y) in empty_spaces:
                        empty_spaces.remove((p.coord_x + p.shape[1], p.coord_y))
                        empty_spaces.append(new_empty1)
                        p.coord_x += 1
                else:
                    return None

                if is_valid(new_pieces):
                    new_board = Board(new_pieces)
                    for x, y in empty_spaces:
                        if new_board.grid[y][x] != '.':
                            empty_spaces.remove((x, y))
                            empty_spaces.append(new_empty2)
                    new_board.empty = empty_spaces
                    return State(new_board, self.current_state.depth + 1 + self.heuristic(new_board), self.current_state.depth + 1, self.current_state)
        return None
  

    # def get_actions(self):
    #     """
    #     Get all possible actions that can be taken from the current state.

    #     :return: A list of possible state.
    #     :rtype: List[State]
    #     """
    #     actions = []
    #     for piece in self.current_state.board.pieces:
    #         for direction in ['up', 'down', 'left', 'right']:
    #             new_board = self.move_piece(piece, direction)
    #             if new_board and new_board.id not in self.visited:
    #                 actions.append(new_board)
    #     return actions
    
    # def move_piece(self, piece, direction):
    #     new_pieces = deepcopy(self.current_state.board.pieces)
    #     for p in new_pieces:
    #         if p == piece:
    #             if direction == 'up' and p.coord_y > 0:
    #                 p.coord_y -= 1
    #             elif direction == 'down' and p.coord_y + p.shape[0] < self.height:
    #                 p.coord_y += 1
    #             elif direction == 'left' and p.coord_x > 0:
    #                 p.coord_x -= 1
    #             elif direction == 'right' and p.coord_x + p.shape[1] < self.width:
    #                 p.coord_x += 1
    #             else:
    #                 return None
    #     if is_valid(new_pieces):
    #         # print("piece: ", piece.coord_x, ", ", piece.coord_y, " | direction: ", direction)
    #         new_board = Board(new_pieces)
    #         # new_board.display()
    #         return State(new_board, self.current_state.depth + 1 + self.heuristic(new_board), self.current_state.depth + 1, self.current_state)
    #     return None
    
def is_valid(pieces: Piece):
    positions = set()
    for piece in pieces:
        if piece.is_goal:
            positions.update([(piece.coord_x, piece.coord_y), (piece.coord_x + 1, piece.coord_y),
                                (piece.coord_x, piece.coord_y + 1), (piece.coord_x + 1, piece.coord_y + 1)])
        elif piece.is_single:
            positions.add((piece.coord_x, piece.coord_y))
        else:
            if piece.orientation == 'h':
                positions.update([(piece.coord_x, piece.coord_y), (piece.coord_x + 1, piece.coord_y)])
            elif piece.orientation == 'v':
                positions.update([(piece.coord_x, piece.coord_y), (piece.coord_x, piece.coord_y + 1)])
    return len(positions) == len(pieces) + 8


def read_from_file(filename):
    """
    Load initial board from a given file.

    :param filename: The name of the given file.
    :type filename: str
    :return: A loaded board
    :rtype: Board
    """

    puzzle_file = open(filename, "r")

    line_index = 0
    pieces = []
    g_found = False

    for line in puzzle_file:

        for x, ch in enumerate(line):

            if ch == '^': # found vertical piece
                pieces.append(Piece(False, False, x, line_index, 'v'))
            elif ch == '<': # found horizontal piece
                pieces.append(Piece(False, False, x, line_index, 'h'))
            elif ch == char_single:
                pieces.append(Piece(False, True, x, line_index, None))
            elif ch == char_goal:
                if g_found == False:
                    pieces.append(Piece(True, False, x, line_index, None))
                    g_found = True
        line_index += 1

    puzzle_file.close()

    board = Board(pieces)
    
    return board



if __name__ == "__main__":
    board = read_from_file("testhrd_med1.txt")
    dfs = DFS(board)

    # dfs.human_play()

    # time_start = time.time()
    # dfs.dfs()
    # time_end = time.time()
    # print("Time: ", time_end - time_start)

    astar = AStar(board)

    # astar.human_play()

    time_start = time.time()
    astar.astar()
    time_end = time.time()
    print("Time: ", time_end - time_start)

    # parser = argparse.ArgumentParser()
    # parser.add_argument(
    #     "--inputfile",
    #     type=str,
    #     required=True,
    #     help="The input file that contains the puzzle."
    # )
    # parser.add_argument(
    #     "--outputfile",
    #     type=str,
    #     required=True,
    #     help="The output file that contains the solution."
    # )
    # parser.add_argument(
    #     "--algo",
    #     type=str,
    #     required=True,
    #     choices=['astar', 'dfs'],
    #     help="The searching algorithm."
    # )
    # args = parser.parse_args()

    # # read the board from the file
    # board = read_from_file(args.inputfile)
