from PIL import ImageTk
from common import *

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


def forward(side):
    return 1 if side == SIDE_BLACK else -1


def side_of(piece):
    return SIDE_WHITE if piece.startswith(PREFIX_WHITE) else SIDE_BLACK


def is_on_side(piece, side):
    return side_of(piece) == side


def is_type(piece, type_name):
    return piece.endswith(type_name)


def __check_board(position, board):
    return (board & (1 << position)) == 0


def __clearance_mask(friend_board, enemy_board):
    return (~friend_board) | enemy_board


def calculate_pawn(x, y, friend_board, enemy_board, fw, en_passent_targets):
    accessable_squares = 0

    position = offset_of(x, y + fw)
    if __check_board(position, enemy_board) and __check_board(position, friend_board):
        accessable_squares |= 1 << position

        behind = y - fw
        has_not_moved = ((behind == 0) or (behind == 7)) and (behind >= 0) and (behind < BOARD_SIZE)
        if has_not_moved:
            position = offset_of(x, y + 2 * fw)
            if __check_board(position, enemy_board) and __check_board(position, friend_board):
                accessable_squares |= 1 << position

    position = offset_of(x + 1, y + fw)
    if not(__check_board(position, enemy_board)) or ((x + 1, y + fw) in en_passent_targets):
        accessable_squares |= 1 << position

    position = offset_of(x - 1, y + fw)
    if not(__check_board(position, enemy_board)) or ((x - 1, y + fw) in en_passent_targets):
        accessable_squares |= 1 << position

    return accessable_squares


def __handle_direction(x, y, dir_valid, accessable_squares, friend_board, enemy_board):
    position = offset_of(x, y)
    if is_on_board(x, y) and __check_board(position, friend_board) and dir_valid:
        accessable_squares |= 1 << position
        if not __check_board(position, enemy_board):
            dir_valid = False
    else:
        dir_valid = False
    return accessable_squares, dir_valid


def calculate_rook(x, y, friend_board, enemy_board, fw):
    accessable_squares = 0
    count = 1
    t = True
    b = True
    l = True
    r = True
    while t or b or l or r:
        accessable_squares, r = __handle_direction(x + count, y, r, accessable_squares, friend_board, enemy_board)
        accessable_squares, l = __handle_direction(x - count, y, l, accessable_squares, friend_board, enemy_board)
        accessable_squares, b = __handle_direction(x, y + count, b, accessable_squares, friend_board, enemy_board)
        accessable_squares, t = __handle_direction(x, y - count, t, accessable_squares, friend_board, enemy_board)
        count += 1
    return accessable_squares


def calculate_knight(x, y, friend_board, enemy_board, fw):
    accessible_squares = 0

    targets = [
        (x + 1, y + 2 * fw),
        (x + 2, y + 1 * fw),
        (x - 1, y + 2 * fw),
        (x - 2, y + 1 * fw),
        (x + 1, y - 2 * fw),
        (x + 2, y - 1 * fw),
        (x - 1, y - 2 * fw),
        (x - 2, y - 1 * fw),
    ]

    for target in targets:
        x = target[0]
        y = target[1]
        if is_on_board(x, y):
            accessible_squares |= coords_to_flag(x, y)
    
    accessible_squares &= __clearance_mask(friend_board, enemy_board)
    return accessible_squares


def calculate_bishop(x, y, friend_board, enemy_board, fw):
    accessable_squares = 0
    count = 1
    tl = True
    bl = True
    tr = True
    br = True
    while tl or bl or tr or br:
        cx = x + count
        cy = y + count
        accessable_squares, br = __handle_direction(cx, cy, br, accessable_squares, friend_board, enemy_board)
        cx = x - count
        cy = y + count
        accessable_squares, bl = __handle_direction(cx, cy, bl, accessable_squares, friend_board, enemy_board)
        cx = x + count
        cy = y - count
        accessable_squares, tr = __handle_direction(cx, cy, tr, accessable_squares, friend_board, enemy_board)
        cx = x - count
        cy = y - count
        accessable_squares, tl = __handle_direction(cx, cy, tl, accessable_squares, friend_board, enemy_board)
        count += 1
    return accessable_squares


def calculate_queen(x, y, friend_board, enemy_board, fw):
    straight_accessable_squares = calculate_rook(x, y, friend_board, enemy_board, fw)
    diagonal_accessable_squares = calculate_bishop(x, y, friend_board, enemy_board, fw)
    accessable_squares = straight_accessable_squares | diagonal_accessable_squares
    return accessable_squares


def calculate_king(x, y, friend_board, enemy_board, fw):
    accessible_squares = 0

    targets = [
        (x + 1, y),
        (x - 1, y),
        (x, y + fw),
        (x, y - fw),
        (x + 1, y + fw),
        (x - 1, y + fw),
        (x + 1, y - fw),
        (x - 1, y - fw)
    ]

    for target in targets:
        x = target[0]
        y = target[1]
        if is_on_board(x, y):
            accessible_squares |= coords_to_flag(x, y)
    
    accessible_squares &= __clearance_mask(friend_board, enemy_board)
    return accessible_squares


piece_calculators = {
    NAME_PAWN: calculate_pawn, NAME_ROOK: calculate_rook, NAME_KNIGHT: calculate_knight,
    NAME_BISHOP: calculate_bishop, NAME_QUEEN: calculate_queen, NAME_KING: calculate_king
}

def calculate_piece(piece_type, x, y, side, friend_board, enemy_board, en_passent_targets):
    calculator = piece_calculators[piece_type]
    fw = forward(side)
    if piece_type == NAME_PAWN:
        return calculator(x, y, friend_board, enemy_board, fw, en_passent_targets)
    else:
        return calculator(x, y, friend_board, enemy_board, fw)