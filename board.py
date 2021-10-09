from os import remove
from pieces import *
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

        self.selected = NONE_SELECTED

        self.pieces = {
            WHITE_PAWN: 0, WHITE_ROOK: 0, WHITE_KNIGHT: 0, WHITE_BISHOP: 0, WHITE_QUEEN: 0, WHITE_KING: 0,
            BLACK_PAWN: 0, BLACK_ROOK: 0, BLACK_KNIGHT: 0, BLACK_BISHOP: 0, BLACK_QUEEN: 0, BLACK_KING: 0
        }
        self.white_squares = 0
        self.black_squares = 0
        self.taken_squares = 0

    def __load_fen(self, string):
        x = 0
        y = 0
        index = 0
        while string[index] != ' ':
            c = string[index]
            position = y * BOARD_SIZE + x
            piece = PREFIX_BLACK
            if c.isupper():
                piece = PREFIX_WHITE
            if c.lower() == 'r':
                piece += NAME_ROOK
            elif c.lower() == 'n':
                piece += NAME_KNIGHT
            elif c.lower() == 'b':
                piece += NAME_BISHOP
            elif c.lower() == 'q':
                piece += NAME_QUEEN
            elif c.lower() == 'k':
                piece += NAME_KING
            elif c.lower() == 'p':
                piece += NAME_PAWN
            elif c == '/':
                y += 1
                x = -1
            elif c.isnumeric():
                x += int(c) - 1
            x += 1
            index += 1
            if piece in self.pieces.keys():
                self.pieces[piece] |= 1 << position

        index += 1
        if string[index] == 'w':
            self.chess.set_side(SIDE_WHITE)
        elif string[index] == 'b':
            self.chess.set_side(SIDE_BLACK)

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

    def __recalculate_piece_flags(self):
        self.white_squares = 0
        self.black_squares = 0
        for key in self.pieces.keys():
            if key.startswith(PREFIX_WHITE):
                self.white_squares |= self.pieces[key]
            else:
                self.black_squares |= self.pieces[key]
        self.taken_squares = self.white_squares | self.black_squares

    def __get_piece(self, x, y):
        position = y * BOARD_SIZE + x
        if (self.taken_squares & (1 << position)) == 0:
            return EMPTY
        for key in self.pieces.keys():
            if (self.pieces[key] & (1 << position)) != 0:
                return key
        return EMPTY

    def reset(self):
        self.selected = NONE_SELECTED
        self.__load_fen(STARTING_FEN)
        self.__recalculate_piece_flags()

    def select_square(self, x, y):
        if self.selected == (x, y):
            self.selected = NONE_SELECTED
        else:
            self.selected = (x, y)

    def select_square_if_piece_is_on_side(self, x, y, side):
        side_squares = self.white_squares if side == SIDE_WHITE else self.black_squares
        position = y * BOARD_SIZE + x
        if (side_squares & (1 << position)) != 0:
            self.select_square(x, y)
            return True
        else:
            return False

    def has_selected(self):
        return self.selected != NONE_SELECTED

    def __remove_piece(self, x, y):
        position = y * BOARD_SIZE + x
        piece = self.__get_piece(x, y)
        if piece is EMPTY:
            return
        self.pieces[piece] &= ~(1 << position)
        self.__recalculate_piece_flags()

    def __set_piece(self, x, y, piece):
        if piece is EMPTY:
            return
        position = y * BOARD_SIZE + x
        self.__remove_piece(x, y)
        self.pieces[piece] |= 1 << position
        self.__recalculate_piece_flags()

    def move_selected_piece(self, newX, newY):
        if self.selected == NONE_SELECTED:
            return
        piece = self.__get_piece(self.selected[0], self.selected[1])
        self.__remove_piece(self.selected[0], self.selected[1])
        self.selected = NONE_SELECTED
        removed_piece = self.__get_piece(newX, newY)
        self.__set_piece(newX, newY, piece)
        return removed_piece

    def draw_squares(self):
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
                if (col, 7 - row) == self.selected:
                    self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill=SELECTED_COLOUR, tags="square")
                else:
                    self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill=colour, tags="square")
                colour = WHITE_COLOUR if colour == BLACK_COLOUR else BLACK_COLOUR

    def draw_pieces(self):
        self.canvas.delete(TAG_PIECE)
        for y in range(BOARD_SIZE):
            for x in range(BOARD_SIZE):
                piece = self.__get_piece(x, y)
                draw_piece(piece, x, y, self.chess.square_size, self.canvas)