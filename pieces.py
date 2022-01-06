from common import *

_pawn_attacks_white = []
_pawn_attacks_black = []

def _calculate_pawn_movements(): # Calculate for white. For black pieces just flip these boards.
    for y in range(BOARD_SIZE):
        for x in range(BOARD_SIZE):
            if (y == 0) or (y == 7):
                _pawn_attacks_white.append(0)
                _pawn_attacks_black.append(0)
                continue
            
            location = offset_of(x, y)

            mask = 0
            if check_coords(x + 1, y - 1):
                mask |= flag(location - 7)
            if check_coords(x - 1, y - 1):
                mask |= flag(location - 9)
            _pawn_attacks_white.append(mask)

            mask = 0
            if check_coords(x + 1, y + 1):
                mask |= flag(location + 9)
            if check_coords(x - 1, y + 1):
                mask |= flag(location + 7)
            _pawn_attacks_black.append(mask)


_knight_movements = []

def _calculate_knight_movements(): # Really simple, doesn't even require bitboarding or anything.
    for y in range(BOARD_SIZE):
        for x in range(BOARD_SIZE):
            mask = 0
            for yOff in (-2, -1, 1, 2):
                for xOff in (-2, -1, 1, 2):
                    if abs(xOff) == abs(yOff):
                        continue
                    posX = x + xOff
                    posY = y + yOff
                    if check_coords(posX, posY):
                        mask |= flag(offset_of(posX, posY))
            _knight_movements.append(mask)


_rook_movements_horiz = []
_rook_movements_vert = []

def _calculate_rook_movements():
    for y in range(BOARD_SIZE):
        for x in range(BOARD_SIZE):
            vert = 0
            horiz = 0
            for my in range(BOARD_SIZE):
                vert |= flag(offset_of(x, my))
            for mx in range(BOARD_SIZE):
                horiz |= flag(offset_of(mx, y))
            _rook_movements_vert.append(vert)
            _rook_movements_horiz.append(horiz)


_bishop_movements_tlbr = []
_bishop_movements_bltr = []

def _calculate_bishop_movements():
    for y in range(BOARD_SIZE):
        for x in range(BOARD_SIZE):
            tlbr = 0
            bltr = 0
            for mx in range(BOARD_SIZE):
                dist = x - mx
                if check_coords(mx, y + dist):
                    bltr |= flag(offset_of(mx, y + dist))
                if check_coords(mx, y - dist):
                    tlbr |= flag(offset_of(mx, y - dist))
            _bishop_movements_tlbr.append(tlbr)
            _bishop_movements_bltr.append(bltr)


_king_movements = []

def _calculate_king_movements():
    for y in range(BOARD_SIZE):
        for x in range(BOARD_SIZE):
            mask = 0
            for my in (-1, 0, 1):
                for mx in (-1, 0, 1):
                    if check_coords(x + mx, y + my) and not((mx == 0) and (my == 0)):
                        mask |= flag(offset_of(x + mx, y + my))
            _king_movements.append(mask & ~flag(offset_of(x, y)))


def precalculate_movement_masks():
    _calculate_pawn_movements()
    _calculate_knight_movements()
    _calculate_rook_movements()
    _calculate_bishop_movements()
    _calculate_king_movements()

precalculate_movement_masks()


def calculate_pawn(location: int, side_to_move: int, position):
    attacks = _pawn_attacks_white if side_to_move == WHITE else _pawn_attacks_black
    
    mask = attacks[location]
    mask |= (position.en_passent_targets & attacks[location]) << 8

    return mask


def calculate_knight(location: int):
    return _knight_movements[location]


def _calculate_slider_attacks(slider: int, occupied: int):
    left_accessible = occupied - 2 * slider # Fills all bits to the left up untill and including the first occupied bit which isn't the piece itself. Bits to the right are equal to the occupied mask.
    accessible = occupied ^ left_accessible # Bits to the right are zeroed due to XOR, bits to the left only leave bits to the right of second occupied 1 from slider.
    return accessible


def calculate_rook_horiz(location: int, occupied: int):
    slider = flag(location)

    row = _rook_movements_horiz[location]
    
    r_slider = reverse(slider)
    r_occupied = reverse(occupied)

    right_attacks = _calculate_slider_attacks(slider, occupied & row) & row
    left_attacks = reverse(_calculate_slider_attacks(r_slider, r_occupied & row) & row)

    return right_attacks | left_attacks


def calculate_rook_vert(location: int, occupied: int):
    slider = flag(location)

    col = _rook_movements_vert[location]
    
    f_slider = flip(slider)
    f_occupied = flip(occupied)

    down_attacks = _calculate_slider_attacks(slider, occupied & col) & col
    up_attacks = flip(_calculate_slider_attacks(f_slider, f_occupied & col) & col)

    return down_attacks | up_attacks


def calculate_rook(location: int, occupied: int):
    horiz = calculate_rook_horiz(location, occupied)
    vert = calculate_rook_vert(location, occupied)

    return horiz | vert


def calculate_bishop_trbl(location: int, occupied: int):
    slider = flag(location)

    s = rotate45Cw(slider)
    o = rotate45Cw(occupied)

    loc = location_from_flag(s)
    row = _rook_movements_horiz[loc]

    tr = _calculate_slider_attacks(s, o & row) & row
    tr = rotateRight(rotate45Ccw(tr), 8) & _bishop_movements_bltr[location]

    r_s = reverse(s)
    r_o = reverse(o)

    bl = reverse(_calculate_slider_attacks(r_s, r_o & row) & row)
    bl = rotateRight(rotate45Ccw(bl), 8) & _bishop_movements_bltr[location]

    return tr | bl


def calculate_bishop_tlbr(location: int, occupied: int):
    slider = flag(location)

    s = rotate45Ccw(slider)
    o = rotate45Ccw(occupied)

    loc = location_from_flag(s)
    row = _rook_movements_horiz[loc]

    br = _calculate_slider_attacks(s, o & row) & row
    br = rotateRight(rotate45Cw(br), 8) & _bishop_movements_tlbr[location]

    r_s = reverse(s)
    r_o = reverse(o)

    tl = reverse(_calculate_slider_attacks(r_s, r_o & row) & row)
    tl = rotateRight(rotate45Cw(tl), 8) & _bishop_movements_tlbr[location]

    return br | tl

def calculate_bishop(location: int, occupied: int):
    trbl = calculate_bishop_trbl(location, occupied)
    tlbr = calculate_bishop_tlbr(location, occupied)

    return trbl | tlbr


def calculate_queen(location: int, occupied: int):
    return calculate_bishop(location, occupied) | calculate_rook(location, occupied)


def calculate_king(location: int):
    return _king_movements[location]


def pawn_movements(location: int, attacks: int, side: int, white_squares: int, black_squares: int, en_passent_targets: int):
    white_starting_range = range(48, 56) # Second row from bottom
    black_starting_range = range(8, 16) # Second row from top

    forward = -side

    enemy_squares = black_squares if side == WHITE else white_squares
    occupied = white_squares |  black_squares

    attacks = attacks & (enemy_squares | en_passent_targets)

    simple_moves = flag(location + 8 * forward) & ~occupied
    if simple_moves:
        if ((side == WHITE) and (location in white_starting_range)) or ((side == BLACK) and (location in black_starting_range)):
            simple_moves |= flag(location + 2 * 8 * forward) & ~occupied

    return attacks | simple_moves