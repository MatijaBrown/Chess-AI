from common import *

import random
import pieces

import copy


DEPTH = 2


def generate_children(possible_moves, board, player, enemy, parent, level, max_depth):
    moves = []
    for frm in possible_moves.keys():
        for target in possible_moves[frm]:
            toX = target[0]
            toY = target[1]
            new_board = copy.copy(board)
            new_board.pieces = board.pieces.copy()
            new_board.move_piece_side(frm[0], frm[1], toX, toY, player.side)
            new_player = copy.copy(player)
            new_enemy = copy.copy(enemy)
            new_player.chess_board = new_board
            new_enemy.chess_board = new_board
            new_board.player_white = new_player if new_player.side == SIDE_WHITE else new_enemy
            new_board.player_black = new_player if new_player.side == SIDE_BLACK else new_enemy
            new_board.chess.current_side = player.side
            moves.append(Move(frm[0], frm[1], toX, toY, new_board, new_player, new_enemy, parent, level, max_depth))
            board.chess.current_side = player.side
    return moves


def better_than(a, b, side):
    if side == SIDE_WHITE:
        return a > b
    elif side == SIDE_BLACK:
        return a < b


class Move():
    
    def __init__(self, fromX, fromY, toX, toY, board, player, enemy, parent, level, max_depth):
        self.fromX = fromX
        self.fromY = fromY
        self.toX = toX
        self.toY = toY
        self.board = board
        self.max_depth = max_depth
        
        self.piece_value = -1

        self.player = player
        self.enemy = enemy

        self.parent = parent

        self.level = level
        self.children = []

        self.produce_children()

    def produce_children(self):
        if (self.level < self.max_depth) and (self.enemy != None):
            possible_moves = pieces.calculate_pieces_list(self.enemy, self.player)
            self.children = generate_children(possible_moves, self.board, self.enemy, self.player, self, self.level + 1, self.max_depth)

    def deepen_to(self, new_depth):
        self.max_depth = new_depth
        self.piece_value = -1

        for child in self.children:
            child.deepen_to(self.max_depth)

        if len(self.children) == 0:
            self.produce_children()

    def value(self):
        if self.piece_value != -1:
            return self.piece_value

        if len(self.children) == 0:
            self.piece_value = self.board.value()
            if self.level != self.max_depth:
                self.piece_value -= -self.player.side * VALUE_KING_W
        else:
            best = self.children[0]
            for move in self.children:
                if better_than(move.value(), best.value(), self.enemy.side):
                    best = move
            self.piece_value = best.value()

        return self.piece_value


EARLY_GAME_END = 6


PRESET_MOVES = {
    # Opening
    "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq":
    [
        Move(4, 6, 4, 4, None, None, None, None, 0, 0),
        Move(3, 6, 3, 4, None, None, None, None, 0, 0)
    ],

    # Sicilian Defence
    "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq":
    [
        Move(2, 1, 2, 3, None, None, None, None, 0, 0)
    ],
    "rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq":
    [
        Move(6, 7, 5, 5, None, None, None, None, 0, 0)
    ],
    "rnbqkbnr/pp1ppppp/8/2p5/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq":
    [
        Move(3, 1, 3, 2, None, None, None, None, 0, 0)
    ],
    "rnbqkbnr/pp2pppp/3p4/2p5/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq":
    [
        Move(3, 6, 3, 4, None, None, None, None, 0, 0)
    ],
    "rnbqkbnr/pp2pppp/3p4/2p5/3PP3/5N2/PPP2PPP/RNBQKB1R b KQkq":
    [
        Move(2, 3, 3, 4, None, None, None, None, 0, 0)
    ],
    "rnbqkbnr/pp2pppp/3p4/8/3pP3/5N2/PPP2PPP/RNBQKB1R w KQkq":
    [
        Move(5, 5, 3, 4, None, None, None, None, 0, 0)
    ],
}


def create_all_moves(accessible_squares, board, player, enemy, move_count):
    if move_count <= EARLY_GAME_END:
        fen_comps = board.generate_fen().split(' ')
        fen = fen_comps[0] + ' ' + fen_comps[1] + ' ' + fen_comps[2]
        if fen in PRESET_MOVES.keys():
            reactions = PRESET_MOVES[fen]
            return reactions[random.randint(0, len(reactions) - 1)]
    return generate_children(accessible_squares, board, player, enemy, None, 0, DEPTH)


def pick_move(possible_moves, board, player, enemy):
    if len(possible_moves) == 0:
        return Move(-1, -1, -1, -1, None, None, None, None, 0)

    best_move_value = possible_moves[0].value()
    for move in possible_moves[1:]:
        if better_than(move.value(), best_move_value, player.side):
            best_move_value = move.value()

    best_move = None
    for move in possible_moves:
        if move.value() == best_move_value:
            move.deepen_to(DEPTH + 1)
            if (best_move == None) or better_than(move.value(), best_move.value(), player.side):
                best_move = move

    return best_move