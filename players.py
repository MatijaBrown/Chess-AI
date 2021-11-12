from common import *

import pieces as pss

import copy


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
        self.loss = False

    def __cant_move(self):
        cant_move = True
        for square in self.accessible_squares.keys():
            if self.accessible_squares[square] != 0:
                cant_move = False
                break
        return cant_move

    def pre_turn(self):
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
        if self.__cant_move() and pss.calculate_attacked_squares(self.chess.get_player(-self.side), dummy):
            self.loss = True
        elif self.__cant_move():
            self.draw = True

    def __update_selected(self, gridX, gridY):
        if self.selected == (gridX, gridY):
            self.selected = NULL_SQUARE
        elif (gridX, gridY) in self.accessible_squares.keys():
            self.selected = (gridX, gridY)

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
        self.chess_board.selected = self.selected


class AiPlayer(Player):
    
    def __init__(self, chess, side):
        super().__init__(chess, chess.board, side)

    def pre_turn(self):
        pass

    def on_click(gridX, gridY) -> bool:
        return True

    def post_turn(self):
        pass