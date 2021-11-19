from common import *

import random
import copy


DEPTH = 3


class Move():
    
    def __init__(self, fromX, fromY, toX, toY, board, side):
        self.fromX = fromX
        self.fromY = fromY
        self.toX = toX
        self.toY = toY
        self.board = board
        self.side = side


def create_all_moves(accessible_squares, board, side):
    moves = []
    for frm in accessible_squares.keys():
        for target in accessible_squares[frm]:
            toX = target[0]
            toY = target[1]
            new_board = copy.copy(board)
            new_board.pieces = board.pieces.copy()
            new_board.move_piece_side(frm[0], frm[1], toX, toY, side)
            moves.append(Move(frm[0], frm[1], toX, toY, new_board, side))
            board.chess.current_side = side
    return moves


def pick_move(possible_moves):
    if len(possible_moves) == 0:
        return Move(-1, -1, -1, -1, None, None)
    move = random.randint(0, len(possible_moves) - 1)
    return possible_moves[move]