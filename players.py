from common import *

import pieces as pss
import ai

import copy
import time


class Player():

    can_castle_queenside = False
    can_castle_kingside = False
    en_passent_targets = []

    def __init__(self, chess, board, side):
        self.chess = chess
        self.chess_board = board
        self.side = side
        self.loss = False
        self.draw = False

    def select_piece(self):
        return QUEEN

    def forward(self):
        return 1 if self.side == SIDE_BLACK else -1

    def pieces(self):
        return self.chess_board.white_pieces if self.side == SIDE_WHITE else self.chess_board.black_pieces

    def board(self):
        return self.chess_board.white_squares if self.side == SIDE_WHITE else self.chess_board.black_squares

    def king(self):
        return self.chess_board.pieces[self.side * KING]

    def reset_to(self, dummy):
        self.can_castle_queenside = dummy.can_castle_queenside
        self.can_castle_kingside = dummy.can_castle_kingside
        self.en_passent_targets = dummy.en_passent_targets

    def lost(self):
        return self.loss

    def drew(self):
        return self.draw


class DummyPlayer(Player):

    def __init__(self, board, player):
        super().__init__(None, board, player.side)
        self.can_castle_queenside = player.can_castle_queenside
        self.can_castle_kingside = player.can_castle_kingside
        self.en_passent_targets = player.en_passent_targets


class HumanPlayer(Player):

    selected = NULL_SQUARE
    accessible_squares = {}
    
    def __init__(self, chess, side):
        super().__init__(chess, chess.board, side)

    def __cant_move(self):
        cant_move = True
        for square in self.accessible_squares.keys():
            if self.accessible_squares[square] != 0:
                cant_move = False
                break
        return cant_move

    def pre_turn(self, _):
        enemy = self.chess.get_player(-self.chess.current_side)
        self.accessible_squares = pss.calculate_pieces(self, enemy)
        self.chess_board.highlighted = self.accessible_squares

        board = copy.copy(self.chess_board)
        board.pieces = self.chess_board.pieces.copy()
        dummy = DummyPlayer(board, self)
        if self.side == SIDE_WHITE:
            board.player_white = dummy
        else:
            board.player_black = dummy
        if self.__cant_move() and (self.king() & pss.calculate_attacked_squares(self.chess.get_player(-self.side), dummy)):
            self.loss = True
        elif self.__cant_move():
            self.draw = True

    def __update_selected(self, gridX, gridY):
        if self.selected == (gridX, gridY):
            self.selected = NULL_SQUARE
        elif (gridX, gridY) in self.accessible_squares.keys():
            self.selected = (gridX, gridY)

    def move(self):
        pass

    def on_click(self, gridX, gridY):
        if (self.selected in self.accessible_squares.keys()) and has_square(self.accessible_squares[self.selected], gridX, gridY):
            self.chess_board.move_piece(self.selected[0], self.selected[1], gridX, gridY)
            return True
        else:
            self.__update_selected(gridX, gridY)
            self.chess_board.selected = self.selected
            return False

    def post_turn(self):
        self.selected = NULL_SQUARE
        self.chess_board.selected = NULL_SQUARE
        pass


class AiPlayer(Player):
    
    possible_moves = []
    selected_move = None

    def __init__(self, chess, side):
        super().__init__(chess, chess.board, side)

    def pre_turn(self, move_count):
        enemy = self.chess.get_player(-self.chess.current_side)
        accessible_squares = pss.calculate_pieces_list(self, enemy)
        self.possible_moves = ai.create_all_moves(accessible_squares, self.chess_board, self, enemy, move_count)
        if isinstance(self.possible_moves, ai.Move):
            self.selected_move = self.possible_moves
        else:
            self.selected_move = ai.pick_move(self.possible_moves, self.chess_board, self, enemy)

    def move(self):
        if self.selected_move.fromX > -1:
            self.chess_board.move_piece(self.selected_move.fromX, self.selected_move.fromY, self.selected_move.toX, self.selected_move.toY)
        else:
            board = copy.copy(self.chess_board)
            board.pieces = self.chess_board.pieces.copy()
            dummy = DummyPlayer(board, self)
            if self.side == SIDE_WHITE:
                board.player_white = dummy
            else:
                board.player_black = dummy
            if self.king() & pss.calculate_attacked_squares(self.chess.get_player(-self.side), dummy):
                self.loss = True
            else:
                self.draw = True
        self.chess.switch_side()

    def on_click(self, gridX, gridY):
        return True

    def post_turn(self):
        pass