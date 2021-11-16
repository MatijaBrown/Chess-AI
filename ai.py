from common import *

import random

class Move():
    
    def __init__(self, fromX, fromY, toX, toY):
        self.fromX = fromX
        self.fromY = fromY
        self.toX = toX
        self.toY = toY


def create_all_moves(accessible_squares):
    moves = []
    for frm in accessible_squares.keys():
        maskTo = accessible_squares[frm]
        if maskTo != 0:
            toX, toY = mask_to_coords(maskTo)
            moves.append(Move(frm[0], frm[1], toX, toY))
    return moves


def pick_move(possible_moves):
    if len(possible_moves) == 0:
        return Move(-1, -1, -1, -1)
    move = random.randint(0, len(possible_moves) - 1)
    return possible_moves[move]