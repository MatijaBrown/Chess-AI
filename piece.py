from PIL import ImageTk

SIDE_WHITE = 0
SIDE_BLACK = -1

NAME_PAWN = "pawn"
NAME_ROOK = "rook"
NAME_KNIGHT = "knight"
NAME_BISHOP = "bishop"
NAME_QUEEN = "queen"
NAME_KING = "king"

PREFIX_WHITE = "white_"
PREFIX_BLACK = "black_"

WHITE_PAWN = PREFIX_WHITE + NAME_PAWN
WHITE_ROOK = PREFIX_WHITE + NAME_ROOK
WHITE_KNIGHT = PREFIX_WHITE + NAME_KNIGHT
WHITE_BISHOP = PREFIX_WHITE + NAME_BISHOP
WHITE_QUEEN = PREFIX_WHITE + NAME_QUEEN
WHITE_KING = PREFIX_WHITE + NAME_KING

BLACK_PAWN = PREFIX_BLACK + NAME_PAWN
BLACK_ROOK = PREFIX_BLACK + NAME_ROOK
BLACK_KNIGHT = PREFIX_BLACK + NAME_KNIGHT
BLACK_BISHOP = PREFIX_BLACK + NAME_BISHOP
BLACK_QUEEN = PREFIX_BLACK + NAME_QUEEN
BLACK_KING = PREFIX_BLACK + NAME_KING

class Piece():
    
    def __init__(self, side, x, y, name, board):
        self.side = side
        self.boardX = x
        self.boardY = y
        self.name = name + '[' + str(x) + ';' + str(y) + ']'
        self.board = board
        self.canvas = self.board.canvas

        self.texture = ImageTk.PhotoImage(file="./res/" + name + ".png", width=60, height=60)

    def __to_window_choords(self, boardX, boardY):
        winX = boardX * self.board.chess.square_size
        winY = boardY * self.board.chess.square_size
        return winX, winY

    def draw(self):
        x, y = self.__to_window_choords(self.boardX, self.boardY)
        self.canvas.create_image(0, 0, image=self.texture, tags=(self.name, "piece"), anchor='c')
        x0 = x + int(self.board.chess.square_size / 2)
        y0 = y + int(self.board.chess.square_size / 2)
        self.canvas.coords(self.name, x0, y0)


class Pawn(Piece):
    
    def __init__(self, side, x, y, board):
        super().__init__(side, x, y, ("white" if (side == SIDE_WHITE) else "black") + "_pawn", board)


class Rook(Piece):
    
    def __init__(self, side, x, y, board):
        super().__init__(side, x, y, ("white" if (side == SIDE_WHITE) else "black") + "_rook", board)


class Knight(Piece):
    
    def __init__(self, side, x, y, board):
        super().__init__(side, x, y, ("white" if (side == SIDE_WHITE) else "black") + "_knight", board)


class Bishop(Piece):
    
    def __init__(self, side, x, y, board):
        super().__init__(side, x, y, ("white" if (side == SIDE_WHITE) else "black") + "_bishop", board)


class Queen(Piece):
    
    def __init__(self, side, x, y, board):
        super().__init__(side, x, y, ("white" if (side == SIDE_WHITE) else "black") + "_queen", board)


class King(Piece):
    
    def __init__(self, side, x, y, board):
        super().__init__(side, x, y, ("white" if (side == SIDE_WHITE) else "black") + "_king", board)