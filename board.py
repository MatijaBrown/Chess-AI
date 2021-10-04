from piece import *

BOARD_SIZE = 8

WHITE_COLOUR = "#DDB88C"
BLACK_COLOUR = "#A66D4F"
SELECTED_COLOUR = "orange"

STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

class Board():
    
    def __init__(self, chess):
        self.chess = chess
        self.canvas = self.chess.canvas
        self.white_pieces = []
        self.black_pieces = []

        self.selected = (-1, -1)

    def __load_from_fen(self):
        pass

    def reset(self):
        self.white_pieces = [
            Pawn(   side=SIDE_WHITE, x=0, y=6, board=self),
            Pawn(   side=SIDE_WHITE, x=1, y=6, board=self),
            Pawn(   side=SIDE_WHITE, x=2, y=6, board=self),
            Pawn(   side=SIDE_WHITE, x=3, y=6, board=self),
            Pawn(   side=SIDE_WHITE, x=4, y=6, board=self),
            Pawn(   side=SIDE_WHITE, x=5, y=6, board=self),
            Pawn(   side=SIDE_WHITE, x=6, y=6, board=self),
            Pawn(   side=SIDE_WHITE, x=7, y=6, board=self),
            Rook(   side=SIDE_WHITE, x=0, y=7, board=self),
            Rook(   side=SIDE_WHITE, x=7, y=7, board=self),
            Knight( side=SIDE_WHITE, x=1, y=7, board=self),
            Knight( side=SIDE_WHITE, x=6, y=7, board=self),
            Bishop( side=SIDE_WHITE, x=2, y=7, board=self),
            Bishop( side=SIDE_WHITE, x=5, y=7, board=self),
            Queen(  side=SIDE_WHITE, x=3, y=7, board=self),
            King(   side=SIDE_WHITE, x=4, y=7, board=self)
        ]
        self.black_pieces = [
            Pawn(   side=SIDE_BLACK, x=0, y=1, board=self),
            Pawn(   side=SIDE_BLACK, x=1, y=1, board=self),
            Pawn(   side=SIDE_BLACK, x=2, y=1, board=self),
            Pawn(   side=SIDE_BLACK, x=3, y=1, board=self),
            Pawn(   side=SIDE_BLACK, x=4, y=1, board=self),
            Pawn(   side=SIDE_BLACK, x=5, y=1, board=self),
            Pawn(   side=SIDE_BLACK, x=6, y=1, board=self),
            Pawn(   side=SIDE_BLACK, x=7, y=1, board=self),
            Rook(   side=SIDE_BLACK, x=0, y=0, board=self),
            Rook(   side=SIDE_BLACK, x=7, y=0, board=self),
            Knight( side=SIDE_BLACK, x=1, y=0, board=self),
            Knight( side=SIDE_BLACK, x=6, y=0, board=self),
            Bishop( side=SIDE_BLACK, x=2, y=0, board=self),
            Bishop( side=SIDE_BLACK, x=5, y=0, board=self),
            Queen(  side=SIDE_BLACK, x=3, y=0, board=self),
            King(   side=SIDE_BLACK, x=4, y=0, board=self)
        ]
        
        self.selected = (-1, -1)

    def draw(self):
        self.canvas.delete("square")
        colour = WHITE_COLOUR
        square_size = self.chess.square_size
        for row in range(BOARD_SIZE):
            colour = WHITE_COLOUR if colour == BLACK_COLOUR else BLACK_COLOUR
            for col in range(BOARD_SIZE):
                x1 = col * square_size
                y1 = (7 - row) * square_size
                x2 = x1 + square_size
                y2 = y1 + square_size
                if (col == self.selected[0]) and (row == self.selected[1]):
                    self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill=SELECTED_COLOUR, tags="square")
                else:
                    self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill=colour, tags="square")
                colour = WHITE_COLOUR if colour == BLACK_COLOUR else BLACK_COLOUR
        
    def draw_pieces(self):
        self.canvas.delete("piece")
        for piece in self.white_pieces:
            piece.draw()
        for piece in self.black_pieces:
            piece.draw()

    def find_piece(self, x, y, side):
        pieces = self.white_pieces if side == SIDE_WHITE else self.black_pieces
        for piece in pieces:
            if (piece.boardX == x) and (piece.boardY == y):
                return piece
                
    def select_piece(self, x, y, side):
        piece = self.find_piece(x, y, side)
        self.selected = (x, y)
        return piece