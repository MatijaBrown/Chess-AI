from tkinter.constants import NONE
from pieces import SIDE_WHITE, SIDE_BLACK, Bishop, King, Knight, Pawn, Queen, Rook
import math

BOARD_SIZE = 8

WHITE_COLOUR = "#DDB88C"
BLACK_COLOUR = "#A66D4F"
SELECTED_COLOUR = "orange"

STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

NONE_SELECTED = (-1, -1)

def coords_to_flag(x: int, y: int) -> int:
    offset = y * BOARD_SIZE + x
    return 1 << offset

def flag_to_coords(flag: int): # Only single flags
    for i in range(int.bit_length()):
        if (flag >> i) == 0:
            y = math.floor(i / BOARD_SIZE)
            x = i % BOARD_SIZE
            return x, y
    return -1, -1

class Board():
    
    def __init__(self, chess):
        self.chess = chess
        self.canvas = self.chess.canvas

        self.pieces = [None for _ in range(BOARD_SIZE * BOARD_SIZE)]

        self.selected = NONE_SELECTED

    def __load_fen(self, string):
        x = 0
        y = 0
        index = 0
        while string[index] != ' ':
            c = string[index]
            position = y * BOARD_SIZE + x
            side = SIDE_WHITE
            if c.islower():
                side = SIDE_BLACK
            if c.lower() == 'r':
                    self.pieces[position] = Rook(side, self)
            elif c.lower() == 'n':
                    self.pieces[position] = Knight(side, self)
            elif c.lower() == 'b':
                    self.pieces[position] = Bishop(side, self)
            elif c.lower() == 'q':
                    self.pieces[position] = Queen(side, self)
            elif c.lower() == 'k':
                    self.pieces[position] = King(side, self)
            elif c.lower() == 'p':
                    self.pieces[position] = Pawn(side, self)
            elif c == '/':
                y += 1
                x = -1
            elif c.isnumeric():
                x += int(c) - 1
            x += 1
            index += 1

        index += 1
        if string[index] == 'w':
            self.chess.current_turn = SIDE_WHITE
        elif string[index] == 'b':
            self.chess.current_turn = SIDE_BLACK

        castling = string[index:(index + 4)]
        if 'K' in castling:
            self.chess.player_white.can_castle_kingside = True
        if 'Q' in castling:
            self.chess.player_white.can_castle_queenside = True
        if 'k' in castling:
            self.chess.player_black.can_castle_kingside = True
        if 'q' in castling:
            self.chess.player_black.can_castle_queenside = True

        # TODO: En passent and time

    def reset(self):
        self.selected = NONE_SELECTED
        self.__load_fen(STARTING_FEN)

    def select_piece(self, x, y):
        if (self.pieces[y * BOARD_SIZE + x] is None):
            return None
        self.selected = (x, y)
        return self.pieces[y * BOARD_SIZE + x]

    def move_selected_piece(self, newX, newY):
        if self.selected == NONE_SELECTED:
            return
        oX = self.selected[0]
        oY = self.selected[1]
        self.pieces[newY * BOARD_SIZE + newX] = self.pieces[oY * BOARD_SIZE + oX]
        self.pieces[oY * BOARD_SIZE + oX] = None
        self.selected = NONE_SELECTED

    def draw(self):
        self.canvas.delete("square")
        colour = WHITE_COLOUR
        square_size = self.chess.square_size
        for row in range(BOARD_SIZE):
            colour = WHITE_COLOUR if colour == BLACK_COLOUR else BLACK_COLOUR
            for col in range(BOARD_SIZE):
                x1 = col * square_size
                y1 = (7 - row) * square_size
                x2 = x1 + square_size
                y2 = y1 + square_size
                if (col == self.selected[0]) and (row == (7 - self.selected[1])):
                    self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill=SELECTED_COLOUR, tags="square")
                else:
                    self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill=colour, tags="square")
                colour = WHITE_COLOUR if colour == BLACK_COLOUR else BLACK_COLOUR

    def draw_pieces(self):
        self.canvas.delete("piece")
        for y in range(BOARD_SIZE):
            for x in range(BOARD_SIZE):
                index = y * BOARD_SIZE + x
                if self.pieces[index] is not None:
                    self.pieces[index].draw(x, y)