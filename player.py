class Player():

    can_castle_kingside = False
    can_castle_queenside = False

    def __init__(self, chess, side):
        self.chess = chess
        self.side = side


class HumanPlayer(Player):
    pass


class AiPlayer(Player):
    pass