import math as maths

import string


BOARD_SIZE = 8

SIDE_NONE = 0
SIDE_WHITE = 1
SIDE_BLACK = -1


EMPTY = 0
PAWN = 1 << 0
ROOK = 1 << 1
KNIGHT = 1 << 2
BISHOP = 1 << 3
QUEEN = 1 << 4
KING = 1 << 5


STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w - - 0 1"


NULL_SQUARE = (-1, -1)


def offset_of(x, y):
    return y * BOARD_SIZE + x


def flag_piece(x, y):
    return 1 << offset_of(x, y)


def has_square(mask, x, y):
    return (mask & flag_piece(x, y)) != 0


def side_of(piece):
    piece /= abs(piece) # if the piece is 1 (white), else it is -1 (black)
    return piece


def is_on_side(piece, side):
    return side_of(piece) == side


def square_name_to_tuple(square_name):
    sX = square_name[0]
    sY = square_name[1]
    x = string.ascii_lowercase.index(sX)
    y = int(sY)
    return (x, y)


def is_on_board(boardX, boardY):
    return (boardX >= 0) and (boardY >= 0) and (boardX < BOARD_SIZE) and (boardY < BOARD_SIZE)


def mask_to_coords(mask):
    n = int(maths.log2(mask))
    x = n % BOARD_SIZE
    y = int((n - x) / BOARD_SIZE)
    return x, y