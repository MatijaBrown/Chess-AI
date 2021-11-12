from common import *
import pieces


WHITE_COLOUR = "#DDB88C"
BLACK_COLOUR = "#A66D4F"
SELECTED_COLOUR = "orange"
HIGHLITED_COLOUR = "khaki"


class Board():

    selected = NULL_SQUARE
    highlighted = {}

    def __init__(self, chess):
        self.chess = chess
        self.canvas = self.chess.canvas

        self.player_white = None
        self.player_black = None

        self.pieces = {
            SIDE_WHITE * PAWN: 0, SIDE_WHITE * ROOK: 0, SIDE_WHITE * KNIGHT: 0, SIDE_WHITE * BISHOP: 0, SIDE_WHITE * QUEEN: 0, SIDE_WHITE * KING: 0,
            SIDE_BLACK * PAWN: 0, SIDE_BLACK * ROOK: 0, SIDE_BLACK * KNIGHT: 0, SIDE_BLACK * BISHOP: 0, SIDE_BLACK * QUEEN: 0, SIDE_BLACK * KING: 0
        }
        self.white_pieces = { PAWN: 0, ROOK: 0, KNIGHT: 0, BISHOP: 0, QUEEN: 0, KING: 0 }
        self.black_pieces = { PAWN: 0, ROOK: 0, KNIGHT: 0, BISHOP: 0, QUEEN: 0, KING: 0 }
        self.white_squares = 0
        self.black_squares = 0

    def __get_current_player(self):
        return self.player_white if self.chess.current_side == SIDE_WHITE else self.player_black

    def __recalculate_flags(self): # TODO: Squares attacked by both sides!
        self.white_squares = 0
        self.black_squares = 0
        self.white_pieces = { PAWN: 0, ROOK: 0, KNIGHT: 0, BISHOP: 0, QUEEN: 0, KING: 0 }
        self.black_pieces = { PAWN: 0, ROOK: 0, KNIGHT: 0, BISHOP: 0, QUEEN: 0, KING: 0 }
        for key in self.pieces.keys():
            if is_on_side(key, SIDE_WHITE):
                self.white_squares |= self.pieces[key]
                self.white_pieces[abs(key)] = self.pieces[key]
            elif is_on_side(key, SIDE_BLACK):
                self.black_squares |= self.pieces[key]
                self.black_pieces[abs(key)] = self.pieces[key]
    
    def load_fen(self, fen):
        x = 0
        y = 0
        index = 0
        char = fen[index]
        while char != ' ':
            side = SIDE_WHITE if char.isupper() else SIDE_BLACK
            piece = EMPTY
            if char.isnumeric():
                x += int(char) - 1
            elif char == '/':
                x = -1
                y += 1
            elif char.lower() == 'p':
                piece = PAWN
            elif char.lower() == 'r':
                piece = ROOK
            elif char.lower() == 'n':
                piece = KNIGHT
            elif char.lower() == 'b':
                piece = BISHOP
            elif char.lower() == 'q':
                piece = QUEEN
            elif char.lower() == 'k':
                piece = KING
            if piece != EMPTY:
                self.set_piece(x, y, side * piece)
            x += 1
            index += 1
            char = fen[index]
        index += 1
        char = fen[index]
        self.chess.set_side(SIDE_WHITE if char == 'w' else SIDE_BLACK)
        index += 2
        castling = fen[index:]
        if 'K' in castling:
            self.player_white.can_castle_kingside = True
            index += 1
        if 'Q' in castling:
            self.player_white.can_castle_queenside = True
            index += 1
        if 'k' in castling:
            self.player_black.can_castle_kingside = True
            index += 1
        if 'q' in castling:
            self.player_black.can_castle_queenside = True
            index += 1
        self.chess.get_current_player().pre_turn()
        index += 1
        while fen[index] != ' ':
            if fen[index].isalpha():
                target = square_name_to_tuple(string[index:])
                index += 1
                if target[1] == 6:
                    self.player_white.en_passent_targets.append(target)
                elif target[1] == 3:
                    self.player_black.en_passent_targets.append(target)
                else:
                    print("ERROR: Invalid en-passent-target", target, "!")
            index += 1
        self.__recalculate_flags()

    def reset(self):
        for key in self.pieces.keys():
            self.pieces[key] = 0
        self.load_fen("8/p2k4/P4K2/3P2r1/8/8/3b1r2/8 w KQkq - 0 1")
        self.__recalculate_flags()

    def is_piece_at(self, boardX, boardY):
        return has_square(self.white_squares | self.black_squares, boardX, boardY)

    def get_piece_at(self, boardX, boardY):
        for key in self.pieces.keys():
            if has_square(self.pieces[key], boardX, boardY):
                return key
        return EMPTY

    def on_side(self, side, boardX, boardY):
        if side == SIDE_WHITE:
            return has_square(self.white_squares, boardX, boardY)
        elif side == SIDE_BLACK:
            return has_square(self.black_squares, boardX, boardY)

    def remove_piece(self, boardX, boardY):
        piece = self.get_piece_at(boardX, boardY)
        if piece == EMPTY:
            return
        self.pieces[piece] &= ~flag_piece(boardX, boardY)
        self.__recalculate_flags()

    def set_piece(self, boardX, boardY, piece):
        self.pieces[piece] |= flag_piece(boardX, boardY)
        self.__recalculate_flags()

    def __on_pawn_move(self, toX, toY):
        pieces.handle_en_passent_targets(self.player_black if self.chess.current_side == SIDE_WHITE else self.player_white, self.selected, toX, toY)
        if not((toX, toY) in self.__get_current_player().en_passent_targets):
            return
        fw = self.__get_current_player().forward()
        self.remove_piece(toX, toY - fw)

    def __on_rook_move(self, fromX):
        if fromX == 0:
            self.__get_current_player().can_castle_queenside = False
        if fromX == 7:
            self.__get_current_player().can_castle_kingside = False

    def __on_king_move(self, fromX, fromY, toX):
        delta = toX - fromX
        if delta == -2:
            self.move_piece(0, fromY, fromX - 1, fromY)
        elif delta == 2:
            self.move_piece(7, fromY, fromX + 1, fromY)
        self.__get_current_player().can_castle_queenside = False
        self.__get_current_player().can_castle_kingside = False

    def move_piece(self, fromX, fromY, toX, toY):
        piece = self.get_piece_at(fromX, fromY)
        self.remove_piece(toX, toY)
        self.remove_piece(fromX, fromY)
        self.set_piece(toX, toY, piece)
        if abs(piece) == PAWN:
            self.__on_pawn_move(toX, toY)
        elif abs(piece) == ROOK:
            self.__on_rook_move(fromX)
        elif abs(piece) == KING:
            self.__on_king_move(fromX, fromY, toX)
        self.__recalculate_flags()

    def __draw_squares(self):
        self.canvas.delete("square")
        colour = WHITE_COLOUR
        square_size = self.chess.square_size
        for y in range(BOARD_SIZE):
            colour = WHITE_COLOUR if colour == BLACK_COLOUR else BLACK_COLOUR
            for x in range(BOARD_SIZE):
                x1 = x * square_size
                y1 = (7 - y) * square_size
                x2 = x1 + square_size
                y2 = y1 + square_size
                if (x, 7 - y) == self.selected:
                    self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill=SELECTED_COLOUR, tags="square")
                elif (self.selected in self.highlighted.keys()) and has_square(self.highlighted[self.selected], x, 7 - y):
                    self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill=HIGHLITED_COLOUR, tags="square")
                else:
                    self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill=colour, tags="square")
                colour = WHITE_COLOUR if colour == BLACK_COLOUR else BLACK_COLOUR

    def __draw_pieces(self):
        self.canvas.delete("piece")
        for y in range(BOARD_SIZE):
            for x in range(BOARD_SIZE):
                piece = self.get_piece_at(x, y)
                pieces.draw_piece(piece, x, y, self.chess.square_size, self.canvas)

    def draw(self):
        self.__draw_squares()
        self.__draw_pieces()