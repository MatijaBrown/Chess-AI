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


STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"


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


def tuple_to_square_name(tuple):
    tX = tuple[0]
    tY = tuple[1]
    x = chr(97 + tX)
    return x + str(tY)


def is_on_board(boardX, boardY):
    return (boardX >= 0) and (boardY >= 0) and (boardX < BOARD_SIZE) and (boardY < BOARD_SIZE)


def mask_to_coords(mask):
    n = int(maths.log2(mask))
    x = n % BOARD_SIZE
    y = int((n - x) / BOARD_SIZE)
    return x, y


def value_of_piece(piece, x, y):
    p = abs(piece)
    if p == PAWN:
        value_map = VALUES_PAWN_W
    elif p == BISHOP:
        value_map = VALUES_BISHOP_W
    elif p == KNIGHT:
        value_map = VALUES_KNIGHT_W
    elif p == ROOK:
        value_map = VALUES_ROOK_W
    elif p == QUEEN:
        value_map = VALUES_QUEEN_W
    elif p == KING:
        return VALUE_KING_W * side_of(piece)
    else:
        return 0
    
    if side_of(piece) == SIDE_BLACK:
        value_map.reverse()

    return value_map[y][x]


# ALL VALUES FOR WHITE, REVERSE FOR BLACK (Taken from Sunfish)
VALUES_PAWN_W = [
    [   0,   0,   0,   0,   5,   0,   0,   0],
    [  78,  83,  86,  73, 102,  82,  85,  90],
    [   7,  29,  21,  44,  40,  31,  44,   7],
    [ -17,  16,  -2,  15,  14,   0,  15, -13],
    [ -26,   3,  10,   9,   6,   1,   0, -23],
    [ -22,   9,   5, -11, -10,  -2,   3, -19],
    [ -31,   8,  -7, -37, -36, -14,   3, -31],
    [   0,   0,   0,   0,   0,   0,   0,   0]
]


VALUES_ROOK_W = [
    [ 35,  29,  33,   4,  37,  33,  56,  50],
    [ 55,  29,  56,  67,  55,  62,  34,  60],
    [ 19,  35,  28,  33,  45,  27,  25,  15],
    [  0,   5,  16,  13,  18,  -4,  -9,  -6],
    [-28, -35, -16, -21, -13, -29, -46, -30],
    [-42, -28, -42, -25, -25, -35, -26, -46],
    [-53, -38, -31, -26, -29, -43, -44, -53],
    [-30, -24, -18,   5,  -2, -18, -31, -32]
]


VALUES_KNIGHT_W = [
    [-66, -53, -75, -75, -10, -55, -58, -70],
    [ -3,  -6, 100, -36,   4,  62,  -4, -14],
    [ 10,  67,   1,  74,  73,  27,  62,  -2],
    [ 24,  24,  45,  37,  33,  41,  25,  17],
    [ -1,   5,  31,  21,  22,  35,   2,   0],
    [-18,  10,  13,  22,  18,  15,  11, -14],
    [-23, -15,   2,   0,   2,   0, -23, -20],
    [-74, -23, -26, -24, -19, -35, -22, -69]
]


VALUES_BISHOP_W = [
    [-59, -78, -82, -76, -23,-107, -37, -50],
    [-11,  20,  35, -42, -39,  31,   2, -22],
    [ -9,  39, -32,  41,  52, -10,  28, -14],
    [ 25,  17,  20,  34,  26,  25,  15,  10],
    [ 13,  10,  17,  23,  17,  16,   0,   7],
    [ 14,  25,  24,  15,   8,  25,  20,  15],
    [ 19,  20,  11,   6,   7,   6,  20,  16],
    [ -7,   2, -15, -12, -14, -15, -10, -10]
]


VALUES_QUEEN_W = [
    [  6,   1,  -8,-104,  69,  24,  88,  26],
    [ 14,  32,  60, -10,  20,  76,  57,  24],
    [ -2,  43,  32,  60,  72,  63,  43,   2],
    [  1, -16,  22,  17,  25,  20, -13,  -6],
    [-14, -15,  -2,  -5,  -1, -10, -20, -22],
    [-30,  -6, -13, -11, -16, -11, -16, -27],
    [-36, -18,   0, -19, -15, -15, -21, -38],
    [-39, -30, -31, -13, -31, -36, -34, -42]
]


VALUE_KING_W = 10000000