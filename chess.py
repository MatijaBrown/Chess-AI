from collections import deque

from common import *
import pieces


MOVE_TYPE_IRREVERSIBLE      = 1 << 2
MOVE_TYPE_PAWN_MOVE         = 1 << 3
MOVE_TYPE_CASTLING          = 1 << 4
MOVE_TYPE_PROMOTION         = 1 << 5
MOVE_TYPE_PAWN_DOUBLE_MOVE  = 1 << 6
MOVE_TYPE_TAKING            = 1 << 7
MOVE_TYPE_KING_MOVE         = 1 << 8
MOVE_TYPE_ROOK_MOVE         = 1 << 9
MOVE_TYPE_EN_PASSENT        = 1 << 10


class Move:
    
    def __init__(self, frm: int, to: int, moving: int, taking: int, is_en_passent: bool) -> None:
        self.frm = frm
        self.to = to
        self.moving = moving
        self.taken = taking

        self.flags = self._generate_flags(is_en_passent)

    def _generate_flags(self, is_en_passent: bool):
        flags = 0

        if self.taken != NULL_PIECE:
            flags |= MOVE_TYPE_TAKING | MOVE_TYPE_IRREVERSIBLE

        if abs(self.moving) == PAWN:
            flags |= MOVE_TYPE_IRREVERSIBLE
            if (self.to < 8) or (self.to > 55):
                flags |= MOVE_TYPE_PROMOTION
            elif abs(self.to - self.frm) == 16:
                flags |= MOVE_TYPE_PAWN_DOUBLE_MOVE
            
            if is_en_passent:
                flags |= MOVE_TYPE_EN_PASSENT

        if abs(self.moving) == KING:
            flags |= MOVE_TYPE_KING_MOVE
            if abs(self.to - self.frm) == 2:
                flags |= MOVE_TYPE_CASTLING

        if abs(self.moving) == ROOK:
            flags |= MOVE_TYPE_ROOK_MOVE
         
        return flags

    def count(self) -> int:
        if not(self.flags & MOVE_TYPE_TAKING) and not(self.flags & MOVE_TYPE_PAWN_MOVE):
            return 1
        else:
            return 0


class IrreversibleInformation:
    
    def __init__(self) -> None:
        self._en_passent_targets_history = deque()
        self._white_castling_kingside_history = deque()
        self._white_castling_queenside_history = deque()
        self._black_castling_kingside_history = deque()
        self._black_castling_queenside_history = deque()
        self._halfmove_clock_history = deque()
        self._fullmove_count_history = deque()

        self._en_passent_targets_history.append(0)
        self._white_castling_kingside_history.append(False)
        self._white_castling_queenside_history.append(False)
        self._black_castling_kingside_history.append(False)
        self._black_castling_queenside_history.append(False)
        self._halfmove_clock_history.append(0)
        self._fullmove_count_history.append(0)

    @property
    def en_passent_targets(self):
        return self._en_passent_targets_history[-1]

    @en_passent_targets.setter
    def en_passent_targets(self, value):
        self._en_passent_targets_history[-1] = value

    @property
    def white_castling_kingside(self):
        return self._white_castling_kingside_history[-1]

    @white_castling_kingside.setter
    def white_castling_kingside(self, value):
        self._white_castling_kingside_history[-1] = value

    @property
    def white_castling_queenside(self):
        return self._white_castling_queenside_history[-1]

    @white_castling_queenside.setter
    def white_castling_queenside(self, value):
        self._white_castling_queenside_history[-1] = value

    @property
    def black_castling_kingside(self):
        return self._black_castling_kingside_history[-1]

    @black_castling_kingside.setter
    def black_castling_kingside(self, value):
        self._black_castling_kingside_history[-1] = value

    @property
    def black_castling_queenside(self):
        return self._black_castling_queenside_history[-1]

    @black_castling_queenside.setter
    def black_castling_queenside(self, value):
        self._black_castling_queenside_history[-1] = value

    @property
    def halfmove_clock(self):
        return self._halfmove_clock_history[-1]

    @halfmove_clock.setter
    def halfmove_clock(self, value):
        self._halfmove_clock_history[-1] = value
        
    @property
    def fullmove_count(self):
        return self._fullmove_count_history[-1]

    @fullmove_count.setter
    def fullmove_count(self, value):
        self._fullmove_count_history[-1] = value

    def save(self):
        self._en_passent_targets_history.append(self.en_passent_targets)
        self._white_castling_kingside_history.append(self.white_castling_kingside)
        self._white_castling_queenside_history.append(self.white_castling_queenside)
        self._black_castling_kingside_history.append(self.black_castling_kingside)
        self._black_castling_queenside_history.append(self.black_castling_queenside)
        self._halfmove_clock_history.append(self.halfmove_clock)
        self._fullmove_count_history.append(self.fullmove_count)

    def restore(self):
        self._en_passent_targets_history.pop()
        self._white_castling_kingside_history.pop()
        self._white_castling_queenside_history.pop()
        self._black_castling_kingside_history.pop()
        self._black_castling_queenside_history.pop()
        self._halfmove_clock_history.pop()
        self._fullmove_count_history.pop()


class ChessPosition:
    
    def __init__(self, fen: str) -> None:
        self.white_pieces = {
            PAWN: 0, ROOK: 0, KNIGHT: 0, BISHOP: 0, QUEEN: 0, KING: 0
        }
        self.black_pieces = {
            PAWN: 0, ROOK: 0, KNIGHT: 0, BISHOP: 0, QUEEN: 0, KING: 0
        }

        self.pieces = {
            WHITE * PAWN: [], WHITE * ROOK: [], WHITE * KNIGHT: [], WHITE * BISHOP: [], WHITE * QUEEN: [], WHITE * KING: [],
            BLACK * PAWN: [], BLACK * ROOK: [], BLACK * KNIGHT: [], BLACK * BISHOP: [], BLACK * QUEEN: [], BLACK * KING: []
        }

        self.white_squares = 0
        self.black_squares = 0

        self.attacks = []
        self.white_attacks = 0
        self.black_attacks = 0

        self.white_blockers = 0
        self.black_blockers = 0

        self.legal_moves = []

        self.draw = False
        self.checkmate = False

        self._restore_info = IrreversibleInformation()

        self.side_to_move = NO_SIDE

        self._move_history = []

        self._load(fen)

    def evaluate(self) -> int:
        result = 0
        for piece in self.pieces:
            result += side_of(piece) * PIECE_VALUES[abs(piece)] * len(self.pieces[piece])
        return result

    def _set_piece(self, piece: int, off: int):
        pt = abs(piece)
        side = side_of(piece)
        if side == WHITE:
            self.white_pieces[pt] |= flag(off)
            self.white_squares |= flag(off)
        else:
            self.black_pieces[pt] |= flag(off)
            self.black_squares |= flag(off)
        self.pieces[piece].append(off)

    def _calculate_attacks(self):
        self.attacks = []
        self.white_attacks = 0
        self.black_attacks = 0

        occupied = self.white_squares | self.black_squares

        for y in range(BOARD_SIZE):
            for x in range(BOARD_SIZE):
                location = offset_of(x, y)

                piece = self.piece_at(location)
                side = side_of(piece)
                piece = abs(piece)

                if piece == PAWN:
                    self.attacks.append(pieces.calculate_pawn(location, side, self))
                elif piece == KNIGHT:
                    self.attacks.append(pieces.calculate_knight(location))
                elif piece == BISHOP:
                    at = pieces.calculate_bishop(location, occupied)
                    self.attacks.append(at)
                elif piece == ROOK:
                    at = pieces.calculate_rook(location, occupied)
                    self.attacks.append(at)
                elif piece == QUEEN:
                    at = pieces.calculate_queen(location, occupied)
                    self.attacks.append(at)
                elif piece == KING:
                    self.attacks.append(pieces.calculate_king(location))
                else:
                    self.attacks.append(0)
                
                if side == WHITE:
                    self.white_attacks |= self.attacks[-1]
                elif side == BLACK:
                    self.black_attacks |= self.attacks[-1]

    def _get_piece_moves(self, piece: int, location: int) -> int:
        same_squares = self.white_squares if self.side_to_move == WHITE else self.black_squares

        if piece == PAWN:
            return pieces.pawn_movements(location, self.attacks[location], self.side_to_move, self.white_squares, self.black_squares, self.en_passent_targets)
        elif piece == KING:
            illegal_squares = self.black_attacks if self.side_to_move == WHITE else self.white_attacks
            return self.attacks[location] & ~same_squares & ~illegal_squares
        else:
            return self.attacks[location] & ~same_squares

    def _get_attack_info(self, king):
        n = 0
        attackers = []
        attacker_locations = []
        for piece in PIECES:
            for location in self.pieces[-self.side_to_move * piece]:
                if self.attacks[location] & king:
                    n += 1
                    attackers.append(piece)
                    attacker_locations.append(location)
        return n, attackers, attacker_locations

    def _single_slider_king_attack_vector(self, slider_loc: int, king: int):
        occupied = self.white_squares | self.black_squares
        attacker = flag(slider_loc)

        mask = pieces.calculate_bishop_tlbr(slider_loc, occupied)
        if king & mask:
            return mask & ~king
        mask = pieces.calculate_bishop_trbl(slider_loc, occupied)
        if king & mask:
            return mask & ~king
        mask = pieces.calculate_rook_horiz(slider_loc, occupied)
        if king & mask:
            return mask & ~king
        mask = pieces.calculate_rook_vert(slider_loc, occupied)
        if king & mask:
            return mask & ~king

    def _calculate_legal_moves_check(self, king):
        legal_moves = {}

        count, attackers, locations = self._get_attack_info(king)

        single = count == 1
        slider = single and ((attackers[0] == BISHOP) or (attackers[0] == ROOK) or (attackers[0] == QUEEN))

        occupied = self.white_squares | self.black_squares
        occupied_no_king = occupied & ~king
        
        enemy_pieces = self.black_pieces if self.side_to_move == WHITE else self.white_pieces
        pinners = enemy_pieces[BISHOP] | enemy_pieces[ROOK] | enemy_pieces[QUEEN]
        potentially_pinned = self._get_potentially_pinned()

        for piece in PIECES:
            for location in self.pieces[self.side_to_move * piece]:
                # First calculate as usual
                target = self._get_piece_moves(piece, location)

                # then make sure the move either blocks or removes the attacker
                if single:
                    if piece != KING:
                        attacker = flag(locations[0])
                        legal_mask = attacker
                        if slider:
                            legal_mask |= self._single_slider_king_attack_vector(locations[0], king)
                        target &= legal_mask

                        target &= self._pinn_piece(target, pinners, location, occupied, king)
                elif piece != KING:
                    target = 0
                
                # Make sure king doesn't move to square blocked by the king
                if piece == KING:
                    for i in range(len(attackers)): # Length of attackers and locations is obviously equal, so just loop over one and use both.
                        if attackers[i] == BISHOP:
                            invalid_squares = pieces.calculate_bishop(locations[i], occupied_no_king) # What would the bishop attack if the king weren't there?
                            target &= ~invalid_squares
                        elif attackers[i] == ROOK:
                            invalid_squares = pieces.calculate_rook(locations[i], occupied_no_king) # What would the bishop attack if the king weren't there?
                            target &= ~invalid_squares
                        elif attackers[i] == QUEEN:
                            invalid_squares = pieces.calculate_queen(locations[i], occupied_no_king) # What would the bishop attack if the king weren't there?
                            target &= ~invalid_squares

                if target:
                    legal_moves[location] = target

        return legal_moves

    def _get_potentially_pinned(self) -> int:
        location_king = self.pieces[self.side_to_move * KING][0]

        blockers = (self.white_squares & self.black_attacks) if self.side_to_move == WHITE else (self.black_squares & self.white_attacks)

        return blockers & pieces.calculate_queen(location_king, self.white_squares | self.black_squares)

    def _pinn_piece(self, target: int, pinners: int, location: int, occupied: int, king: int):
        mask = pieces.calculate_bishop_tlbr(location, occupied)
        if (pinners & mask) and (king & mask):
            return target & mask
        mask = pieces.calculate_bishop_trbl(location, occupied)
        if (pinners & mask) and (king & mask):
            return target & mask
        mask = pieces.calculate_rook_horiz(location, occupied)
        if (pinners & mask) and (king & mask):
            return target & mask
        mask = pieces.calculate_rook_vert(location, occupied)
        if (pinners & mask) and (king & mask):
            return target & mask
        return target # Target is not pinned.

    def _generate_castling(self):
        kingside = flag(5) | flag(6) | flag(7)
        queenside = flag(0) | flag(1) | flag(2) | flag(3)

        if self.side_to_move == WHITE:
            kingside = flip(kingside)
            queenside = flip(queenside)

        enemy_attacks = self.black_attacks if self.side_to_move == WHITE else self.white_attacks
        rooks = self.white_pieces[ROOK] if self.side_to_move == WHITE else self.black_pieces[ROOK]

        everything = self.white_squares | self.black_squares | enemy_attacks
        empty = everything & ~rooks

        kngside = self._restore_info.white_castling_kingside if self.side_to_move == WHITE else self._restore_info.black_castling_kingside
        qunside = self._restore_info.white_castling_queenside if self.side_to_move == WHITE else self._restore_info.black_castling_queenside

        allowance_mask = 0

        if (kingside & empty == 0) and kngside:
            allowance_mask |= flag(self.pieces[self.side_to_move * KING][0] + 2)
        if (queenside & empty == 0) and qunside:
            allowance_mask |= flag(self.pieces[self.side_to_move * KING][0] - 2)

        return allowance_mask

    def _calculate_legal_moves_not_check(self, king: int):
        legal_moves = {}

        enemy_pieces = self.black_pieces if self.side_to_move == WHITE else self.white_pieces

        occupied = self.white_squares | self.black_squares

        pinners = enemy_pieces[BISHOP] | enemy_pieces[ROOK] | enemy_pieces[QUEEN]
        potentially_pinned = self._get_potentially_pinned()

        for piece in PIECES:
            for location in self.pieces[self.side_to_move * piece]:
                # First calculate as usual
                target = self._get_piece_moves(piece, location)

                # If it is a potentially pinned piece, mask by legal locations
                if potentially_pinned & flag(location):
                    target = self._pinn_piece(target, pinners, location, occupied, king)

                if piece == KING:
                    target |= self._generate_castling()

                if target:
                    legal_moves[location] = target

        return legal_moves

    def _calculate_legal_moves(self):
        enemy_attacks = self.black_attacks if self.side_to_move == WHITE else self.white_attacks
        king = self.white_pieces[KING] if self.side_to_move == WHITE else self.black_pieces[KING]
        if king & enemy_attacks:
            self.legal_moves = self._calculate_legal_moves_check(king)
            if len(self.legal_moves) == 0:
                self.checkmate = True
                self.draw = False
        else:
            self.legal_moves = self._calculate_legal_moves_not_check(king)
            if len(self.legal_moves) == 0:
                self.checkmate = False
                self.draw = True

    def _new_move(self, side: int, generate_responses: bool):
        self.side_to_move = side

        if generate_responses:
            self._calculate_attacks()
            self._calculate_legal_moves()
        else:
            self.attacks = []
            self.legal_moves = {}

    def _load(self, fen: str):
        x = 0
        y = 0
        secs = fen.split(' ')

        # Pieces
        for c in secs[0]:
            token = c.lower()
            side = WHITE if c.isupper() else BLACK
            off = offset_of(x, y)
            if token == "p":
                self._set_piece(side * PAWN, off)
            elif token == 'r':
                self._set_piece(side * ROOK, off)
            elif token == 'n':
                self._set_piece(side * KNIGHT, off)
            elif token == 'b':
                self._set_piece(side * BISHOP, off)
            elif token == 'q':
                self._set_piece(side * QUEEN, off)
            elif token == 'k':
                self._set_piece(side * KING, off)
            elif token == '/':
                x = 0
                y += 1
                continue
            elif token.isdigit():
                x += int(token) - 1
            x += 1

        # Side to move
        side_to_move = WHITE if secs[1] == 'w' else BLACK

        # castling
        self._restore_info.white_castling_kingside = False
        self._restore_info.white_castling_queenside = False
        self._restore_info.black_castling_kingside = False
        self._restore_info.black_castling_queenside = False
        for token in secs[2]:
            if token == 'K':
                self._restore_info.white_castling_kingside = True
            elif token == 'Q':
                self._restore_info.white_castling_queenside = True
            elif token == 'k':
                self._restore_info.black_castling_kingside = True
            elif token == 'q':
                self._restore_info.black_castling_queenside = True

        # en-passent
        i = 0
        while (i < len(secs[3])) and (secs[3][i] != '-'):
            self._restore_info.en_passent_targets |= flag_from_square_name(secs[3][i:(i + 2)])
            i += 2
        
        # halfmove clock
        self._restore_info.halfmove_clock = int(secs[4])

        # move counter
        self._restore_info.fullmove_count = int(secs[5])

        self._new_move(side_to_move, True)

    def piece_at(self, offset: int) -> int:
        flg = flag(offset)
        
        to_look = self.white_pieces if self.white_squares & flg else (self.black_pieces if self.black_squares & flg else None)
        if to_look is None:
            return NULL_PIECE
        for piece in to_look.keys():
            if to_look[piece] & flg:
                return piece * (WHITE if self.white_squares & flg else BLACK)
        return NULL_PIECE

    # XOR (^) Will set bits which overlap to zero, which removes the old position, and sets bits that don't overlap to 1, which will set the new piece to its position.
    def _place_piece(self, moving: int, frm_loc: int, to_loc: int):
        frm = flag(frm_loc)
        to = flag(to_loc)
        frmTo = frm | to

        if self.side_to_move == WHITE:
            self.white_pieces[abs(moving)] ^= frmTo
            self.white_squares ^= frmTo
        elif self.side_to_move == BLACK:
            self.black_pieces[abs(moving)] ^= frmTo
            self.black_squares ^= frmTo

        self.pieces[moving].remove(frm_loc)
        self.pieces[moving].append(to_loc)

    def _take_piece(self, taking: int, loc: int, en_passent: bool):
        if taking == NULL_PIECE:
            return

        to = flag(loc)

        if en_passent:
            self.pieces[taking].remove(loc - self.side_to_move * BOARD_SIZE)
            to = flag(loc - self.side_to_move * BOARD_SIZE)
        else:
            self.pieces[taking].remove(loc)

        if self.side_to_move == WHITE:
            self.black_pieces[abs(taking)] ^= to
            self.black_squares ^= to
        elif self.side_to_move == BLACK:
            self.white_pieces[abs(taking)] ^= to
            self.white_squares ^= to

    def _handle_castling(self, move: Move):
        if move.to > move.frm: # Kingside
            self._place_piece(self.side_to_move * ROOK, move.to + 1, move.to - 1)
        elif move.to < move.frm: # Queenside
            self._place_piece(self.side_to_move * ROOK, move.to - 2, move.to + 1)

    def _uncastle(self, move: Move):
        if move.to > move.frm: # Kingside
            self._place_piece(self.side_to_move * ROOK, move.to - 1, move.to + 1)
        elif move.to < move.frm: # Queenside
            self._place_piece(self.side_to_move * ROOK, move.to + 1, move.to - 2)

    def _handle_promotion(self, move: Move):
        pos = flag(move.to)

        if self.side_to_move == WHITE:
            self.white_pieces[PAWN] &= ~pos
            self.white_pieces[QUEEN] |= pos
        elif self.side_to_move == BLACK:
            self.black_pieces[PAWN] &= ~pos
            self.black_pieces[QUEEN] |= pos

        self.pieces[self.side_to_move * PAWN].remove(move.to)
        self.pieces[self.side_to_move * QUEEN].append(move.to)

    def _unpromote(self, move: Move):
        pos = flag(move.to)

        if self.side_to_move == WHITE:
            self.white_pieces[PAWN] |= pos
            self.white_pieces[QUEEN] &= ~pos
        elif self.side_to_move == BLACK:
            self.black_pieces[PAWN] |= pos
            self.black_pieces[QUEEN] &= ~pos

        self.pieces[self.side_to_move * PAWN].append(move.to)
        self.pieces[self.side_to_move * QUEEN].remove(move.to)

    def _evalute_move_flags(self, move: Move):
        flags = move.flags

        if flags & MOVE_TYPE_CASTLING:
            self._handle_castling(move)

        if flags & MOVE_TYPE_KING_MOVE:
            if self.side_to_move == WHITE:
                self._restore_info.white_castling_kingside = False
                self._restore_info.white_castling_queenside = False
            elif self.side_to_move == BLACK:
                self._restore_info.black_castling_kingside = False
                self._restore_info.black_castling_queenside = False

        if flags & MOVE_TYPE_ROOK_MOVE:
            if self.side_to_move == WHITE:
                if (move.frm == 56) and self._restore_info.white_castling_queenside:
                    self._restore_info.white_castling_queenside = False
                elif (move.frm == 63) and self._restore_info.white_castling_kingside:
                    self._restore_info.white_castling_kingside = False
            elif self.side_to_move == BLACK:
                if (move.frm == 0) and self._restore_info.black_castling_queenside:
                    self._restore_info.black_castling_queenside = False
                elif (move.frm == 7) and self._restore_info.black_castling_kingside:
                    self._restore_info.black_castling_kingside = False
            
        if flags & MOVE_TYPE_PAWN_DOUBLE_MOVE:
            flg = flag(move.to + self.side_to_move * BOARD_SIZE)
            self.en_passent_targets |= flg

        if flags & MOVE_TYPE_PROMOTION:
            self._handle_promotion(move)

    def _undo_flags(self, move: Move):
        flags = move.flags

        if flags & MOVE_TYPE_CASTLING:
            self._uncastle(move)

        if flags & MOVE_TYPE_PROMOTION:
            self._unpromote(move)

    def move(self, move: Move, generate_responses: bool):
        self._restore_info.save()
        self.en_passent_targets = 0

        self._place_piece(move.moving, move.frm, move.to)
        self._take_piece(move.taken, move.to, move.flags & MOVE_TYPE_EN_PASSENT)

        self._evalute_move_flags(move)

        self._move_history.append(move)

        self._restore_info.halfmove_clock += move.count()

        self._new_move(-self.side_to_move, generate_responses)

    def _untake_piece(self, taking: int, loc: int, en_passent: bool):
        if taking == NULL_PIECE:
            return

        to = flag(loc)

        if en_passent:
            self.pieces[taking].append(loc - self.side_to_move * BOARD_SIZE)
            to = flag(loc - self.side_to_move * BOARD_SIZE)
        else:
            self.pieces[taking].append(loc)

        if self.side_to_move == WHITE:
            self.black_pieces[abs(taking)] ^= to
            self.black_squares ^= to
        elif self.side_to_move == BLACK:
            self.white_pieces[abs(taking)] ^= to
            self.white_squares ^= to

    def undo_last_move(self):
        self.draw = False
        self.checkmate = False

        move = self._move_history.pop()
        self._restore_info.restore()

        self.side_to_move = -self.side_to_move

        self._undo_flags(move)

        self._place_piece(move.moving, move.to, move.frm)
        self._untake_piece(move.taken, move.to, move.flags & MOVE_TYPE_EN_PASSENT)

    @property
    def en_passent_targets(self):
        return self._restore_info.en_passent_targets

    @en_passent_targets.setter
    def en_passent_targets(self, value):
        self._restore_info.en_passent_targets = value

    def __hash__(self) -> int:
        pass