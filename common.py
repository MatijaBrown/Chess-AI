import math
import string
from common import *

BOARD_SIZE = 8

def is_on_board(x, y):
    return ((x >= 0) and (x < BOARD_SIZE)) and ((y >= 0) and (y < BOARD_SIZE))


def offset_of(x: int, y: int) -> int:
    return y * BOARD_SIZE + x


def coords_to_flag(x: int, y: int) -> int:
    return 1 << offset_of(x, y)


def flag_to_coords(flag: int): # Only single flags
    for i in range(int.bit_length()):
        if (flag >> i) == 0:
            y = math.floor(i / BOARD_SIZE)
            x = i % BOARD_SIZE
            return x, y
    return -1, -1


def check_bit(flag: int, x: int, y: int):
    return (flag & coords_to_flag(x, y)) != 0


def square_name_to_tuple(square_name):
    sX = square_name[0]
    sY = square_name[1]
    x = string.ascii_lowercase.index(sX)
    y = int(sY)
    return (x, y)