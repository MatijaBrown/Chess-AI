import string
import math as maths


BOARD_SIZE = 8

NO_SIDE = 0
WHITE = 1
BLACK = -WHITE

NULL_PIECE = 0
PAWN = 1
ROOK = 2
KNIGHT = 3
BISHOP = 4
QUEEN = 5
KING = 6

PIECES = [PAWN, ROOK, KNIGHT, BISHOP, QUEEN, KING]

PIECE_NAMES = {
    WHITE * PAWN: "white_pawn",
    WHITE * ROOK: "white_rook",
    WHITE * KNIGHT: "white_knight",
    WHITE * BISHOP: "white_bishop",
    WHITE * QUEEN: "white_queen",
    WHITE * KING: "white_king",
    
    BLACK * PAWN: "black_pawn",
    BLACK * ROOK: "black_rook",
    BLACK * KNIGHT: "black_knight",
    BLACK * BISHOP: "black_bishop",
    BLACK * QUEEN: "black_queen",
    BLACK * KING: "black_king"
}

DEFAULT_STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

VALUE_PAWN = 1
VALUE_KNIGHT = 3
VALUE_BISHOP = 3
VALUE_ROOK = 5
VALUE_QUEEN = 9
VALUE_KING = 1_000_000


PIECE_VALUES = {
    PAWN: VALUE_PAWN,
    KNIGHT: VALUE_KNIGHT,
    BISHOP: VALUE_BISHOP,
    ROOK: VALUE_ROOK,
    QUEEN: VALUE_QUEEN,
    KING: VALUE_KING
}


def side_of(piece: int) -> int:
    if piece > 0:
        return WHITE
    elif piece < 0:
        return BLACK
    else:
        return 0


def offset_of(x: int, y: int) -> int:
    return y * BOARD_SIZE + x


def flag(offset: int) -> int:
    return 1 << offset


def flag_from_square_name(square_name: str) -> int:
    sX = square_name[0]
    sY = square_name[1]
    x = string.ascii_lowercase.index(sX)
    y = int(sY)
    return 1 << offset_of(x, y)


def check_coords(x: int, y: int):
    return ((x >= 0) and (x < BOARD_SIZE)) and ((y >= 0) and (y < BOARD_SIZE))


def is_on_board(offset: int):
    return (offset >= 0) and (offset < 64)


def location_from_flag(flag: int):
    return int(maths.log2(flag))


def flip(x: int):
    k1 = 0x00FF00FF00FF00FF
    k2 = 0x0000FFFF0000FFFF
    x = ((x >>  8) & k1) | ((x & k1) <<  8)
    x = ((x >> 16) & k2) | ((x & k2) << 16)
    x = (x >> 32)        | ( x       << 32)
    return x


def reverse(x: int):
    k1 = 0x5555555555555555
    k2 = 0x3333333333333333
    k4 = 0x0f0f0f0f0f0f0f0f
    x = ((x >> 1) & k1) +  2 * (x & k1)
    x = ((x >> 2) & k2) +  4 * (x & k2)
    x = ((x >> 4) & k4) + 16 * (x & k4)
    return x


def rotate180(x: int):
    return reverse(flip(x))


def rotate90Cw(x: int):
    return flip(flipDiagA1H8(x))


def rotate90Ccw(x: int):
    return flipDiagA1H8(flip(x))


def flipDiagA1H8(x: int):
    k1 = 0x5500550055005500
    k2 = 0x3333000033330000
    k4 = 0x0f0f0f0f00000000
    t = k4 & (x ^ (x << 28))
    x ^=      t ^ (t >> 28)
    t = k2 & (x ^ (x << 14))
    x ^=      t ^ (t >> 14)
    t = k1 & (x ^ (x << 7))
    x ^=      t ^ (t >> 7)
    return x


def rotateRight(x: int, s: int):
    return (x >> s) | (x << (64 - s))


def rotate45Ccw(x: int):
    k1 = 0xAAAAAAAAAAAAAAAA
    k2 = 0xCCCCCCCCCCCCCCCC
    k4 = 0xF0F0F0F0F0F0F0F0
    x ^= k1 & (x ^ rotateRight(x,  8))
    x ^= k2 & (x ^ rotateRight(x, 16))
    x ^= k4 & (x ^ rotateRight(x, 32))
    return x


def rotate45Cw(x: int):
    k1 = 0x5555555555555555
    k2 = 0x3333333333333333
    k4 = 0x0f0f0f0f0f0f0f0f
    x ^= k1 & (x ^ rotateRight(x,  8))
    x ^= k2 & (x ^ rotateRight(x, 16))
    x ^= k4 & (x ^ rotateRight(x, 32))
    return x