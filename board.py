from os import remove
from typing import cast
from pieces import *
from common import *

WHITE_COLOUR = "#DDB88C"
BLACK_COLOUR = "#A66D4F"
SELECTED_COLOUR = "orange"
HIGHLITED_COLOUR = "khaki"

STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

NONE_SELECTED = (-1, -1)


class Board():
    
    def __init__(self, chess):
        self.chess = chess
        self.canvas = self.chess.canvas

        self.selected = NONE_SELECTED

        self.pieces = {
            WHITE_PAWN: 0, WHITE_ROOK: 0, WHITE_KNIGHT: 0, WHITE_BISHOP: 0, WHITE_QUEEN: 0, WHITE_KING: 0,
            BLACK_PAWN: 0, BLACK_ROOK: 0, BLACK_KNIGHT: 0, BLACK_BISHOP: 0, BLACK_QUEEN: 0, BLACK_KING: 0
        }
        self.white_squares = 0
        self.black_squares = 0
        self.taken_squares = 0

        self.white_side_en_passent_targets = []
        self.black_side_en_passent_targets = []

        self.possible_moves = {} # (x, y) -> integer flag

    def __load_fen(self, string):
        x = 0
        y = 0
        index = 0
        while string[index] != ' ':
            c = string[index]
            position = offset_of(x, y)
            piece = PREFIX_BLACK
            if c.isupper():
                piece = PREFIX_WHITE
            if c.lower() == 'r':
                piece += NAME_ROOK
            elif c.lower() == 'n':
                piece += NAME_KNIGHT
            elif c.lower() == 'b':
                piece += NAME_BISHOP
            elif c.lower() == 'q':
                piece += NAME_QUEEN
            elif c.lower() == 'k':
                piece += NAME_KING
            elif c.lower() == 'p':
                piece += NAME_PAWN
            elif c == '/':
                y += 1
                x = -1
            elif c.isnumeric():
                x += int(c) - 1
            x += 1
            index += 1
            if piece in self.pieces.keys():
                self.pieces[piece] |= 1 << position

        index += 1
        side = SIDE_WHITE if string[index] == 'w' else SIDE_BLACK
        index += 2

        castling = string[index:(index + 4)]
        if 'K' in castling:
            self.chess.player_white.can_castle_kingside = True
            index += 1
        if 'Q' in castling:
            self.chess.player_white.can_castle_queenside = True
            index += 1
        if 'k' in castling:
            self.chess.player_black.can_castle_kingside = True
            index += 1
        if 'q' in castling:
            self.chess.player_black.can_castle_queenside = True
            index += 1
        if castling.startswith('-'):
            index += 1

        index += 1

        while string[index] != ' ':
            if string[index].isalpha():
                target = square_name_to_tuple(string[index:])
                index += 1
                if target[1] == 6:
                    self.white_side_en_passent_targets.append(target)
                elif target[1] == 3:
                    self.black_side_en_passent_targets.append(target)
                else:
                    print("ERROR: Invalid en-passent-target", target, "!")
            index += 1

        self.__recalculate_piece_flags()

        self.chess.set_side(side)

    def __recalculate_piece_flags(self):
        self.white_squares = 0
        self.black_squares = 0
        for key in self.pieces.keys():
            if key.startswith(PREFIX_WHITE):
                self.white_squares |= self.pieces[key]
            else:
                self.black_squares |= self.pieces[key]
        self.taken_squares = self.white_squares | self.black_squares

    def get_piece(self, x, y):
        if not check_bit(self.taken_squares, x, y):
            return EMPTY
        for key in self.pieces.keys():
            if check_bit(self.pieces[key], x, y):
                return key
        return EMPTY

    def reset(self):
        self.selected = NONE_SELECTED
        self.__load_fen(STARTING_FEN)
        self.__recalculate_piece_flags()

    def select_square(self, x, y):
        if self.selected == (x, y):
            self.selected = NONE_SELECTED
        else:
            self.selected = (x, y)

    def select_square_if_on_same_side(self, x, y, side):
        side_squares = self.white_squares if side == SIDE_WHITE else self.black_squares
        if check_bit(side_squares, x, y):
            self.select_square(x, y)
            return True
        else:
            return False

    def has_selected(self):
        return self.selected != NONE_SELECTED

    def __remove_piece(self, x, y):
        position = offset_of(x, y)
        piece = self.get_piece(x, y)
        if piece is EMPTY:
            return
        self.pieces[piece] &= ~(1 << position)
        self.__recalculate_piece_flags()

    def __set_piece(self, x, y, piece):
        if piece is EMPTY:
            return
        position = offset_of(x, y)
        self.__remove_piece(x, y)
        self.pieces[piece] |= 1 << position
        self.__recalculate_piece_flags()

    def __check_move_validity(self, x, y):
        accessible_squares = self.possible_moves[self.selected]
        return check_bit(accessible_squares, x, y)

    def take(self, x, y):
        self.__remove_piece(x, y)
        
    def move_piece(self, fromX, fromY, toX, toY):
        piece = self.get_piece(fromX, fromY)
        self.__remove_piece(fromX, fromY)
        self.__set_piece(toX, toY, piece)

    def __handle_en_passant_targets(self, side, toX, toY):
        self.white_side_en_passent_targets = []
        self.black_side_en_passent_targets = []
        if abs(self.selected[1] - toY) == 2:
            if side == SIDE_WHITE:
                self.black_side_en_passent_targets.append((toX, toY + 1))
            elif side == SIDE_BLACK:
                self.white_side_en_passent_targets.append((toX, toY - 1))

    def __handle_en_passent_taking(self, side, toX, toY):
        if not((toX, toY) in self.white_side_en_passent_targets if side == SIDE_WHITE else self.black_side_en_passent_targets):
            return
        direction = self.selected[0] - toX
        if abs(direction) == 1:
            fw = forward(side)
            self.take(toX, toY - fw)

    def __handle_en_passant(self, toX, toY):
        self.__handle_en_passent_taking(self.chess.current_side, toX, toY)
        self.__handle_en_passant_targets(self.chess.current_side, toX, toY)

    
    def __move_pawn(self, oldX, oldY, newX, newY):
        self.__handle_en_passant(newX, newY)
        self.move_piece(oldX, oldY, newX, newY)


    def __move_rook(self, oldX, oldY, newX, newY):
        self.move_piece(oldX, oldY, newX, newY)


    def __move_king(self, oldX, oldY, newX, newY):
        self.move_piece(oldX, oldY, newX, newY)


    def move_selected_piece(self, newX, newY):
        if self.selected == NONE_SELECTED:
            return False
        if not(self.__check_move_validity(newX, newY)):
            self.selected = NONE_SELECTED
            return False
        oX = self.selected[0]
        oY = self.selected[1]
        self.take(newX, newY)
        piece = self.get_piece(oX, oY)
        if is_type(piece, NAME_PAWN):
            self.__move_pawn(oX, oY, newX, newY)
        elif is_type(piece, NAME_ROOK):
            self.__move_rook(oX, oY, newX, newY)
        elif is_type(piece, NAME_KING):
            self.__move_king(oX, oY, newX, newY)
        else:
            self.move_piece(oX, oY, newX, newY)
        self.selected = NONE_SELECTED
        return True

    def calculate_possible_responses(self, side):
        self.possible_moves = {}
        pieces = self.white_squares if side == SIDE_WHITE else self.black_squares
        for x in range(BOARD_SIZE):
            for y in range(BOARD_SIZE):
                location = (x, y)
                position = offset_of(x, y)
                if (pieces & (1 << position)) != 0:
                    piece = self.get_piece(x, y)
                    piece_type = piece[(len(PREFIX_WHITE) if side == SIDE_WHITE else len(PREFIX_BLACK)):]
                    friend_board = self.white_squares if side == SIDE_WHITE else self.black_squares
                    enemy_board = self.black_squares if side == SIDE_WHITE else self.white_squares
                    en_passent = self.white_side_en_passent_targets if side == SIDE_WHITE else self.black_side_en_passent_targets
                    possible_responses = calculate_piece(piece_type, x, y, side, friend_board, enemy_board, en_passent)
                    self.possible_moves[location] = possible_responses
        return self.possible_moves

    def draw_squares(self):
        self.canvas.delete("square")
        colour = WHITE_COLOUR
        square_size = self.chess.square_size
        for row in range(BOARD_SIZE):
            colour = WHITE_COLOUR if colour == BLACK_COLOUR else BLACK_COLOUR
            for col in range(BOARD_SIZE):
                location = (col, 7 - row)
                position = (7 - row) * BOARD_SIZE + col
                x1 = col * square_size
                y1 = (7 - row) * square_size
                x2 = x1 + square_size
                y2 = y1 + square_size
                if location == self.selected:
                    self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill=SELECTED_COLOUR, tags="square")
                elif (self.selected in self.possible_moves.keys()) and ((self.possible_moves[self.selected] & (1 << position)) != 0):
                    self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill=HIGHLITED_COLOUR, tags="square")
                else:
                    self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill=colour, tags="square")
                colour = WHITE_COLOUR if colour == BLACK_COLOUR else BLACK_COLOUR

    def draw_pieces(self):
        self.canvas.delete(TAG_PIECE)
        for y in range(BOARD_SIZE):
            for x in range(BOARD_SIZE):
                piece = self.get_piece(x, y)
                draw_piece(piece, x, y, self.chess.square_size, self.canvas)