from common import *
from players import DummyPlayer

from PIL import ImageTk
import copy


textures = {
    SIDE_WHITE * PAWN: None, SIDE_WHITE * ROOK: None, SIDE_WHITE * KNIGHT: None, SIDE_WHITE * BISHOP: None, SIDE_WHITE * QUEEN: None, SIDE_WHITE * KING: None,
    SIDE_BLACK * PAWN: None, SIDE_BLACK * ROOK: None, SIDE_BLACK * KNIGHT: None, SIDE_BLACK * BISHOP: None, SIDE_BLACK * QUEEN: None, SIDE_BLACK * KING: None
}


def __texture(name):
    file = "./res/" + name + ".png"
    return ImageTk.PhotoImage(file=file, width=60, height=60)


def load_textures():
    textures[SIDE_WHITE * PAWN] = __texture("white_pawn")
    textures[SIDE_WHITE * ROOK] = __texture("white_rook")
    textures[SIDE_WHITE * KNIGHT] = __texture("white_knight")
    textures[SIDE_WHITE * BISHOP] = __texture("white_bishop")
    textures[SIDE_WHITE * QUEEN] = __texture("white_queen")
    textures[SIDE_WHITE * KING] = __texture("white_king")
    
    textures[SIDE_BLACK * PAWN] = __texture("black_pawn")
    textures[SIDE_BLACK * ROOK] = __texture("black_rook")
    textures[SIDE_BLACK * KNIGHT] = __texture("black_knight")
    textures[SIDE_BLACK * BISHOP] = __texture("black_bishop")
    textures[SIDE_BLACK * QUEEN] = __texture("black_queen")
    textures[SIDE_BLACK * KING] = __texture("black_king")


def __to_window_choords(boardX, boardY, square_size):
    winX = boardX * square_size
    winY = boardY * square_size
    return winX, winY
    

def draw_piece(piece, boardX, boardY, square_size, canvas):
    if piece == EMPTY:
        return
    texture = textures[piece]
    x, y = __to_window_choords(boardX, boardY, square_size)
    x0 = x + int(square_size / 2)
    y0 = y + int(square_size / 2)
    canvas.create_image(x0, y0, image=texture, tags=(piece, "piece"), anchor='c')


def __check_board(position, board):
    return (board & (1 << position)) == 0


def __create_dummy_player(player, oldX, oldY, newX, newY):
    board = copy.copy(player.chess_board)
    board.pieces = player.chess_board.pieces.copy()
    dummy = DummyPlayer(board, player)
    if player.side == SIDE_WHITE:
        board.player_white = dummy
    else:
        board.player_black = dummy
    board.move_piece(oldX, oldY, newX, newY)
    return dummy


def __check_check(player, enemy, fromX, fromY, toX, toY):
    dummy = __create_dummy_player(player, fromX, fromY, toX, toY)
    attacked = calculate_attacked_squares(enemy, dummy)
    if dummy.king() & attacked:
        return True
    return False


def calculate_pawn(x, y, player, enemy, checkCheck, targets_list):
    accessible_squares = 0

    if not has_square(player.board() | enemy.board(), x, y + player.forward()) and checkCheck: # Need to test forward only if really moving
        if not __check_check(player, enemy, x, y, x, y + player.forward()):
            accessible_squares |= flag_piece(x, y + player.forward())
            targets_list.append((x, y + player.forward()))
        
        behind = y - player.forward()
        if is_on_board(x, behind) and ((behind == 0) or (behind == 7)):
            if not __check_check(player, enemy, x, y, x, y + 2 * player.forward()):
                accessible_squares |= flag_piece(x, y + 2 * player.forward())
                targets_list.append((x, y + 2 * player.forward()))
                
    toX = x + 1
    toY = y + player.forward()
    if is_on_board(toX, toY) and ((has_square(enemy.board(), toX, toY) or ((toX, toY) in player.en_passent_targets)) or not checkCheck):
        if not checkCheck or not __check_check(player, enemy, x, y, toX, toY):
            accessible_squares |= flag_piece(toX, toY)
            targets_list.append((toX, toY))
            
    toX = x - 1
    toY = y + player.forward()
    if is_on_board(toX, toY) and ((has_square(enemy.board(), toX, toY) or ((toX, toY) in player.en_passent_targets)) or not checkCheck):
        if not checkCheck or not __check_check(player, enemy, x, y, toX, toY):
            accessible_squares |= flag_piece(toX, toY)
            targets_list.append((toX, toY))

    return accessible_squares


def calculate_knight(x, y, player, enemy, checkCheck, targets_list):
    targets = [
        (x + 1, y + 2),
        (x + 2, y + 1),
        (x - 1, y + 2),
        (x - 2, y + 1),
        (x + 1, y - 2),
        (x + 2, y - 1),
        (x - 1, y - 2),
        (x - 2, y - 1),
    ]

    accessable_squares = 0

    for target in targets:
        toX = target[0]
        toY = target[1]
        if is_on_board(toX, toY):
            if not checkCheck or (not has_square(player.board(), toX, toY) and not __check_check(player, enemy, x, y, toX, toY)):
                accessable_squares |= flag_piece(toX, toY)
                targets_list.append((toX, toY))

    return accessable_squares


def __handle_direction(x, y, toX, toY, dir_valid, accessable_squares, player, enemy, checkCheck, targets_list):
    if not is_on_board(toX, toY) or not dir_valid:
        return accessable_squares, False
    if not checkCheck or (not has_square(player.board(), toX, toY) and not __check_check(player, enemy, x, y, toX, toY)):
        accessable_squares |= flag_piece(toX, toY)
        targets_list.append((toX, toY))
    if has_square(player.board() | enemy.board(), toX, toY):
        dir_valid = False
    return accessable_squares, dir_valid


def calculate_rook(x, y, player, enemy, checkCheck, targets_list):
    accessable_squares = 0
    count = 1
    t = True
    b = True
    l = True
    r = True
    while t or b or l or r:
        accessable_squares, r = __handle_direction(x, y, x + count, y, r, accessable_squares, player, enemy, checkCheck, targets_list)
        accessable_squares, l = __handle_direction(x, y, x - count, y, l, accessable_squares, player, enemy, checkCheck, targets_list)
        accessable_squares, b = __handle_direction(x, y, x, y + count, b, accessable_squares, player, enemy, checkCheck, targets_list)
        accessable_squares, t = __handle_direction(x, y, x, y - count, t, accessable_squares, player, enemy, checkCheck, targets_list)
        count += 1
    return accessable_squares


def calculate_bishop(x, y, player, enemy, checkCheck, targets_list):
    accessable_squares = 0
    count = 1
    tl = True
    bl = True
    tr = True
    br = True
    while tl or bl or tr or br:
        cx = x + count
        cy = y + count
        accessable_squares, br = __handle_direction(x, y, cx, cy, br, accessable_squares, player, enemy, checkCheck, targets_list)
        cx = x - count
        cy = y + count
        accessable_squares, bl = __handle_direction(x, y, cx, cy, bl, accessable_squares, player, enemy, checkCheck, targets_list)
        cx = x + count
        cy = y - count
        accessable_squares, tr = __handle_direction(x, y, cx, cy, tr, accessable_squares, player, enemy, checkCheck, targets_list)
        cx = x - count
        cy = y - count
        accessable_squares, tl = __handle_direction(x, y, cx, cy, tl, accessable_squares, player, enemy, checkCheck, targets_list)
        count += 1
    return accessable_squares


def calculate_queen(x, y, player, enemy, checkCheck, targets_list):
    straight_accessable_squares = calculate_rook(x, y, player, enemy, checkCheck, targets_list)
    diagonal_accessable_squares = calculate_bishop(x, y, player, enemy, checkCheck, targets_list)
    accessable_squares = straight_accessable_squares | diagonal_accessable_squares
    return accessable_squares


def calculate_king(x, y, player, enemy, checkCheck, targets_list):
    targets = [
        (x + 1, y),
        (x - 1, y),
        (x, y + 1),
        (x, y - 1),
        (x + 1, y + 1),
        (x + 1, y - 1),
        (x - 1, y + 1),
        (x - 1, y - 1)
    ]

    accessable_squares = 0

    for target in targets:
        toX = target[0]
        toY = target[1]
        if is_on_board(toX, toY):
            if not checkCheck or (not has_square(player.board(), toX, toY) and not __check_check(player, enemy, x, y, toX, toY)):
                accessable_squares |= flag_piece(toX, toY)
                targets_list.append((toX, toY))

    if checkCheck:
        if player.can_castle_queenside:
            toCheck = flag_piece(x, y) | flag_piece(x - 1) | flag_piece(x - 2) | flag_piece(x - 3)
            attacked = calculate_attacked_squares(enemy, __create_dummy_player(player, x, y, x - 3, y))
            if not(toCheck & attacked):
                accessable_squares |= flag_piece(x - 2, y)
                targets_list.append((x - 2, y))
        if player.can_castle_kingside:
            toCheck = flag_piece(x, y) | flag_piece(x + 1) | flag_piece(x + 2)
            attacked = calculate_attacked_squares(enemy, __create_dummy_player(player, x, y, x + 2, y))
            if not(toCheck & attacked):
                accessable_squares |= flag_piece(x + 2, y)
                targets_list.append((x + 2, y))

    return accessable_squares


def calculate_attacked_squares(player, enemy):
    attacked_squares = 0
    pieces = enemy.chess_board.white_pieces if player.side == SIDE_WHITE else enemy.chess_board.black_pieces
    for x in range(BOARD_SIZE):
        for y in range(BOARD_SIZE):
            for piece in pieces.keys():
                piece_mask = pieces[piece]
                if has_square(piece_mask, x, y):
                    if piece == PAWN:
                        attacked_squares |= calculate_pawn(x, y, player, enemy, False, [])
                    elif piece == ROOK:
                        attacked_squares |= calculate_rook(x, y, player, enemy, False, [])
                    elif piece == KNIGHT:
                        attacked_squares |= calculate_knight(x, y, player, enemy, False, [])
                    elif piece == BISHOP:
                        attacked_squares |= calculate_bishop(x, y, player, enemy, False, [])
                    elif piece == QUEEN:
                        attacked_squares |= calculate_queen(x, y, player, enemy, False, [])
                    elif piece == KING:
                        attacked_squares |= calculate_king(x, y, player, enemy, False, [])
    return attacked_squares


def calculate_pieces(player, enemy):
    possible_moves = {}
    pieces = player.pieces()
    for x in range(BOARD_SIZE):
        for y in range(BOARD_SIZE):
            for piece in pieces.keys():
                if has_square(pieces[piece], x, y):
                    if piece == PAWN:
                        possible_moves[(x, y)] = calculate_pawn(x, y, player, enemy, True, [])
                    elif piece == ROOK:
                        possible_moves[(x, y)] = calculate_rook(x, y, player, enemy, True, [])
                    elif piece == KNIGHT:
                        possible_moves[(x, y)] = calculate_knight(x, y, player, enemy, True, [])
                    elif piece == BISHOP:
                        possible_moves[(x, y)] = calculate_bishop(x, y, player, enemy, True, [])
                    elif piece == QUEEN:
                        possible_moves[(x, y)] = calculate_queen(x, y, player, enemy, True, [])
                    elif piece == KING:
                        possible_moves[(x, y)] = calculate_king(x, y, player, enemy, True, [])
    return possible_moves



def calculate_pieces_list(player, enemy):
    targets = {}
    pieces = player.pieces()
    for x in range(BOARD_SIZE):
        for y in range(BOARD_SIZE):
            for piece in pieces.keys():
                if has_square(pieces[piece], x, y):
                    targets[(x, y)] = []
                    if piece == PAWN:
                        calculate_pawn(x, y, player, enemy, True, targets[(x, y)])
                    elif piece == ROOK:
                        calculate_rook(x, y, player, enemy, True, targets[(x, y)])
                    elif piece == KNIGHT:
                        calculate_knight(x, y, player, enemy, True, targets[(x, y)])
                    elif piece == BISHOP:
                        calculate_bishop(x, y, player, enemy, True, targets[(x, y)])
                    elif piece == QUEEN:
                        calculate_queen(x, y, player, enemy, True, targets[(x, y)])
                    elif piece == KING:
                        calculate_king(x, y, player, enemy, True, targets[(x, y)])
    return targets


def handle_en_passent_targets(player, selected, toX, toY):
    player.en_passent_targets = []
    if abs(selected[1] - toY) == 2: # check if move was en-passent
        player.en_passent_targets.append((toX, toY + player.forward()))