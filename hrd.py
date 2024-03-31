from __future__ import annotations

import argparse
from heapq import heappush, heappop
from typing import *

# ====================================================================================

char_goal = '1'
char_single = '2'


class Heap:
    def __init__(self):
        self.heap = []

    def append(self, item):
        heappush(self.heap, item)

    def pop(self):
        return heappop(self.heap)

    def __bool__(self):
        return bool(self.heap)

    def extend(self, items):
        for item in items:
            self.append(item)


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

    def __repr__(self):
        return '{} {} {} {} {}'.format(self.is_goal, self.is_single, \
                                       self.coord_x, self.coord_y, self.orientation)

    def move(self, x, y) -> Piece:
        new_x = self.coord_x + x
        new_y = self.coord_y + y
        if new_x < 0 or new_y < 0:
            raise ValueError('x and y must be non-negative')
        return Piece(self.is_goal, self.is_single, new_x, new_y, self.orientation)


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

        # self.grid is a 2-d (size * size) array automatically generated
        # using the information on the pieces when a board is being created.
        # A grid contains the symbol for representing the pieces on the board.
        self.grid = []
        self.goal = None
        self.__construct_grid()
        self.board_string = "\n".join(["".join(line) for line in self.grid])

    def move(self, piece_number: int, x: int, y: int) -> Board:
        new_pieces = self.pieces[:]
        new_pieces[piece_number] = new_pieces[piece_number].move(x, y)
        return Board(new_pieces)

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
                self.goal = piece
            elif piece.is_single:
                self.grid[piece.coord_y][piece.coord_x] = char_single
            else:
                if piece.orientation == 'h':
                    self.grid[piece.coord_y][piece.coord_x] = '<'
                    self.grid[piece.coord_y][piece.coord_x + 1] = '>'
                elif piece.orientation == 'v':
                    self.grid[piece.coord_y][piece.coord_x] = '^'
                    self.grid[piece.coord_y + 1][piece.coord_x] = 'v'
        count = 0
        for i in self.grid:
            for j in i:
                if j == '.':
                    count += 1
        if count != 2:
            raise ValueError('The board is not valid.')

    def display(self):
        """
        Print out the current board.

        """
        for i, line in enumerate(self.grid):
            for ch in line:
                print(ch, end='')
            print()


class State:
    """
    State class wrapping a Board with some extra current state information.
    Note that State and Board are different. Board has the locations of the pieces. 
    State has a Board and some extra information that is relevant to the search: 
    heuristic function, f value, current depth and parent.
    """

    def __init__(self, board, depth, parent=None):
        """
        :param board: The board of the state.
        :type board: Board
        :param depth: The depth of current state in the search tree.
        :type depth: int
        :param parent: The parent of current state.
        :type parent: Optional[State]
        """
        self.board = board
        self.f = depth + self.manhattan_distance()
        self.depth = depth
        self.parent = parent
        self.id = hash(board)  # The id for breaking ties.

    def manhattan_distance(self) -> int:
        """
        Calculate the manhattan distance of the current state.
        """
        return abs(self.board.goal.coord_x - 1) + abs(self.board.goal.coord_y - 3)

    def __hash__(self):
        return self.board.board_string.__hash__()

    def __eq__(self, other):
        return self.board.board_string == other.board.board_string

    def __lt__(self, other):
        return self.f < other.f

    def to_list(self) -> List[Board]:
        result = [self.board]
        curr = self
        while curr.parent:
            curr = curr.parent
            result.append(curr.board)
        return result[::-1]

    def generate_successors(self) -> List[State]:
        result = []
        for i in range(len(self.board.pieces)):
            for x, y in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                try:
                    new_board = self.board.move(i, x, y)
                    result.append(State(new_board, self.depth + 1, self))
                finally:
                    continue
        return result

    def is_goal(self) -> bool:
        return self.board.goal.coord_x == 1 and self.board.goal.coord_y == 3

    # def dfs(self) -> State:
    #     seen = set()
    #     frontier = [self]
    #     while frontier:
    #         state = frontier.pop()
    #         if state not in seen:
    #             seen.add(state)
    #             if state.is_goal():
    #                 return state
    #             frontier.extend(state.generate_successors())

    def search(self, frontier) -> State:
        seen = set()
        frontier.append(self)
        while frontier:
            state = frontier.pop()
            if state not in seen:
                seen.add(state)
                if state.is_goal():
                    return state
                frontier.extend(state.generate_successors())


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

            if ch == '^':  # found vertical piece
                pieces.append(Piece(False, False, x, line_index, 'v'))
            elif ch == '<':  # found horizontal piece
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

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--inputfile",
        type=str,
        required=True,
        help="The input file that contains the puzzle."
    )
    parser.add_argument(
        "--outputfile",
        type=str,
        required=True,
        help="The output file that contains the solution."
    )
    parser.add_argument(
        "--algo",
        type=str,
        required=True,
        choices=['astar', 'dfs'],
        help="The searching algorithm."
    )
    args = parser.parse_args()

    # read the board from the file
    board = read_from_file(args.inputfile)
    # new_board = read_from_file("testhrd_hard1.txt")
    new_state = State(board, 0, None)
    solution = None
    if args.algo == 'astar':
        solution = new_state.search(Heap()).to_list()
    else:
        solution = new_state.search([]).to_list()
    with open(args.outputfile, "w") as text_file:
        text_file.write("\n\n".join([board.board_string for board in solution]))
    # print(new_state.board)
    # for state in new_state.generate_successors():
    #     state.board.display()
    #     print()
    # solution = new_state.search([]).to_list()
    # print(len(solution))
    # for board in solution:
    #     board.display()
    #     print()
