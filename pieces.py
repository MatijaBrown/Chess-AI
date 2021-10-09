from PIL import ImageTk

SIDE_WHITE = 1
SIDE_NONE = 0
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

EMPTY = "EMPTY"

Pieces = {
    WHITE_PAWN: None, WHITE_ROOK: None, WHITE_KNIGHT: None, WHITE_BISHOP: None, WHITE_QUEEN: None, WHITE_KING: None,
    BLACK_PAWN: None, BLACK_ROOK: None, BLACK_KNIGHT: None, BLACK_BISHOP: None, BLACK_QUEEN: None, BLACK_KING: None,
}

TAG_PIECE = "piece"

def __texture(name):
    file = "./res/" + name + ".png"
    return ImageTk.PhotoImage(file=file, width=60, height=60)


def load_textures():
    Pieces[WHITE_PAWN] = __texture(WHITE_PAWN)
    Pieces[WHITE_ROOK] = __texture(WHITE_ROOK)
    Pieces[WHITE_KNIGHT] = __texture(WHITE_KNIGHT)
    Pieces[WHITE_BISHOP] = __texture(WHITE_BISHOP)
    Pieces[WHITE_QUEEN] = __texture(WHITE_QUEEN)
    Pieces[WHITE_KING] = __texture(WHITE_KING)
    
    Pieces[BLACK_PAWN] = __texture(BLACK_PAWN)
    Pieces[BLACK_ROOK] = __texture(BLACK_ROOK)
    Pieces[BLACK_KNIGHT] = __texture(BLACK_KNIGHT)
    Pieces[BLACK_BISHOP] = __texture(BLACK_BISHOP)
    Pieces[BLACK_QUEEN] = __texture(BLACK_QUEEN)
    Pieces[BLACK_KING] = __texture(BLACK_KING)


def __to_window_choords(boardX, boardY, square_size):
    winX = boardX * square_size
    winY = boardY * square_size
    return winX, winY


def draw_piece(piece, boardX, boardY, square_size, canvas):
    if piece is EMPTY:
        return
    texture = Pieces[piece]
    x, y = __to_window_choords(boardX, boardY, square_size)
    x0 = x + int(square_size / 2)
    y0 = y + int(square_size / 2)
    canvas.create_image(x0, y0, image=texture, tags=(piece, TAG_PIECE), anchor='c')