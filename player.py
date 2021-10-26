from common import *

class Player():

    can_castle_kingside = False
    can_castle_queenside = False

    def __init__(self, chess, side):
        self.chess = chess
        self.side = side


class HumanPlayer(Player):
    
    def on_turn_started(self):
        self.chess.board.calculate_possible_responses(self.side)

    def on_click(self, boardX, boardY):
        result = self.chess.board.select_square_if_on_same_side(boardX, boardY, self.side)
        if not result and self.chess.board.has_selected():
            if self.chess.board.move_selected_piece(boardX, boardY):
                self.chess.set_side(-self.side)

    def post_turn(self): pass


class AiPlayer(Player):
    
    def on_turn_started(self):
        pass

    def on_click(self, boardX, boardY): pass

    def post_turn(self): pass