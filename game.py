import tkinter as tk
import math
import time
import threading

from common import *
import chess
import ai


COLOUR_WHITE = "#DDB88C"
COLOUR_BLACK = "#A66D4F"


SELECTED_COLOUR = "orange"
HIGHLITED_COLOUR = "khaki"


class Board:
    
    def __init__(self, app, initial_fen: str) -> None:
        self._app = app
        self._canvas = self._app.canvas
        self.position = chess.ChessPosition(initial_fen)

        self.selected_squares = 0
        self.highlighted_squares = 0

        self._piece_textures = {}

    def draw_squares(self, invert: bool):
        size = self._app.square_size

        if invert:
            self.selected_squares = flip(self.selected_squares)
            self.highlighted_squares = flip(self.highlighted_squares)

        self._canvas.delete("square")
        for i in range(BOARD_SIZE * BOARD_SIZE):
            row = math.floor(i / BOARD_SIZE)
            col = i % BOARD_SIZE

            x0 = col * size
            y0 = row * size
            x1 = x0 + size
            y1 = y0 + size

            if invert:
                colour = COLOUR_WHITE if ((row % 2 == 0) and (col % 2 != 0)) or ((row % 2 != 0) and (col % 2 == 0)) else COLOUR_BLACK
            else:
                colour = COLOUR_BLACK if ((row % 2 == 0) and (col % 2 != 0)) or ((row % 2 != 0) and (col % 2 == 0)) else COLOUR_WHITE

            if self.selected_squares & flag(i):
                colour = SELECTED_COLOUR
            elif self.highlighted_squares & flag(i):
                colour = HIGHLITED_COLOUR
            self._canvas.create_rectangle(x0, y0, x1, y1, fill=colour, tags="square")
        self._canvas.tag_lower("square")

    def _handle_piece(self, piece, x, y):
        piece_name = PIECE_NAMES[piece] + '|' + str(x) + '|' + str(y)
        filename = "res/" + PIECE_NAMES[piece] + ".png"
        if filename not in self._piece_textures:
            self._piece_textures[filename] = tk.PhotoImage(file=filename)
        self._canvas.create_image(0, 0, image=self._piece_textures[filename], tags=(piece_name, "piece"), anchor='c')
        return piece_name

    def draw_pieces(self, invert: bool):
        size = self._app.square_size

        self._canvas.delete("piece")
        for side in (WHITE, BLACK):
            for piece in PIECES:
                for location in self.position.pieces[side * piece]:
                    x = location % BOARD_SIZE
                    y = int((location - x) / BOARD_SIZE)
                    piece_name = self._handle_piece(side * piece, x, y)
                    x0 = (x * size) + int(size / 2)
                    y0 = ((7 - y if invert else y) * size) + int(size / 2)
                    self._canvas.coords(piece_name, x0, y0)

    def make_move(self, move: chess.Move):
        self.position.move(move, True)

    def unmake_laste_move(self):
        self.position.undo_last_move()

    def reset_highlighting(self):
        self.highlighted_squares = 0
        self.selected_squares = 0

    def destroy(self):
        self._canvas.delete("square")
        self._canvas.delete("piece")


class Player:
    
    def __init__(self, side: int, board: Board) -> None:
        self.side = side
        self._board = board
        self._enemy = None

    @property
    def enemy(self):
        return self._enemy

    @enemy.setter
    def enemy(self, value):
        self._enemy = value

    @property
    def board(self):
        return self._board

    @board.setter
    def board(self, value: Board):
        self._board = value

    def on_click(self, offset):
        pass

    def pick_move(self) -> chess.Move:
        pass

    def halt_picking(self):
        pass

    def switch_side(self):
        self.side *= -1


class HumanPlayer(Player):
    
    def __init__(self, side: int, board: Board) -> None:
        super().__init__(side, board)

        self._picking_event = threading.Event()

        self._frm = -1
        self.legal_targets = {}

        self.move = None

    def black_to_front(self) -> bool:
        return self.side == BLACK

    def pick_move(self) -> chess.Move:
        self._picking_event.wait()
        self._picking_event = threading.Event()
        move = self.move
        self.move = None
        return move

    def halt_picking(self):
        if not self._picking_event.is_set():
            self._frm = -1
            self._picking_event.set()

    def on_click(self, offset):
        if self._frm == offset: # re-clicking on the same square
            self._frm = -1
            self.board.reset_highlighting()
            self.board.draw_squares(self.black_to_front())
            return

        piece = self.board.position.piece_at(offset)

        if side_of(piece) == self.side:
            self._frm = offset

            self.board.selected_squares = flag(offset)

            self.legal_targets = self.board.position.legal_moves[offset]
            self.board.highlighted_squares = self.legal_targets

            self.board.draw_squares(self.black_to_front())
        elif self._frm != -1:
            moving = self.board.position.piece_at(self._frm)

            en_passent = (flag(offset) & self.board.position.en_passent_targets) != 0
            if en_passent:
                piece = self.board.position.piece_at(offset - self.side * BOARD_SIZE)

            self.move = chess.Move(self._frm, offset, moving, piece, en_passent)
            self._frm = -1
            self._picking_event.set()


class AiPlayer(Player):

    def __init__(self, side: int, board: Board) -> None:
        super().__init__(side, board)

    def pick_move(self) -> chess.Move:
        move = ai.calculate_best_move(self.board.position)
        return move


class Game:

    def __init__(self, chess_application, ai_is_white: bool, initial_fen: str) -> None:
        self._app = chess_application

        self.board = Board(self._app, initial_fen)
        
        self.player_white = None
        self.player_black = None
        self.setup_players(ai_is_white)

        self._game_running = False
        self._game_thread = threading.Thread(target=self._play, name="Chess Game Thread")

    def setup_players(self, ai_is_white: bool):
        self.black_to_front = ai_is_white
        if self.player_white and self.player_black:
            self.side_to_move().halt_picking()
        if ai_is_white:
            self.player_white = AiPlayer(WHITE, self.board)
            self.player_black = HumanPlayer(BLACK, self.board)
        elif not ai_is_white:
            self.player_white = HumanPlayer(WHITE, self.board)
            self.player_black = AiPlayer(BLACK, self.board)
        self.player_white.enemy = self.player_black
        self.player_black.enemy = self.player_white
        self.draw()

    def side_to_move(self) -> Player:
        if self.board.position.side_to_move == WHITE:
            return self.player_white
        else:
            return self.player_black

    def on_click(self, pxX, pxY):
        x = int(math.floor(pxX / self._app.square_size))
        y = int(math.floor(pxY / self._app.square_size))

        y = 7 - y if self.black_to_front else y

        off = offset_of(x, y)
        self.side_to_move().on_click(off)

    def draw(self):
        self.board.draw_squares(self.black_to_front)
        self.board.draw_pieces(self.black_to_front)

    def _play(self):
        while self._game_running:
            player = self.side_to_move()

            player_string = "White" if player.side == WHITE else "Black"
            self._app.info_label["text"] = player_string + "'s turn to move."

            if self.board.position.checkmate:
                self._app.info_label["text"] = player_string + " lost!"
                break
            if self.board.position.draw:
                self._app.info_label["text"] = "It's a draw!"
                break

            move = player.pick_move()
            if move is not None:
                self.board.selected_squares = 0
                self.board.highlighted_squares = 0
                self.board.make_move(move)
                self.draw()
            else:
                time.sleep(0.005)

    def run(self):
        self._game_running = True
        self._game_thread.start()

    def end(self):
        self._game_running = False
        self.side_to_move().halt_picking()
        self._game_thread.join()