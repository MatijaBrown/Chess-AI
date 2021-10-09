from board import *
INVALID = 0

from player import *

import tkinter as tk

INITIAL_SQUARE_SIZE = 64

class Chess(tk.Frame):
    
    def __init__(self, top):
        self.top = top
        self.square_size = INITIAL_SQUARE_SIZE
        self.canvas_size = self.square_size * BOARD_SIZE

        self.current_turn = INVALID
        self.player_white = HumanPlayer(self, SIDE_WHITE)
        self.player_black = HumanPlayer(self, SIDE_BLACK)

        tk.Frame.__init__(self, self.top)

        self.canvas = tk.Canvas(self, width=self.canvas_size, height=self.canvas_size, background="white")
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, anchor="c", expand=tk.TRUE)

        self.canvas.bind("<Configure>", self.refresh)
        self.canvas.bind("<Button-1>", self.click)

        self.board = Board(self)

        self.statusbar = tk.Frame(self, height=64)
        self.new_button = tk.Button(self.statusbar, text="New", fg="black", command=self.reset)
        self.new_button.pack(side=tk.LEFT, in_=self.statusbar)

        self.save_button = tk.Button(self.statusbar, text="Save", fg="black")
        self.save_button.pack(side=tk.LEFT, in_=self.statusbar)

        self.status_label = tk.Label(self.statusbar, text="    Waiting to start game...    ", fg="black")
        self.status_label.pack(side=tk.LEFT, in_=self.statusbar)

        self.quit_button = tk.Button(self.statusbar, text="Quit", fg="black", command=self.top.destroy)
        self.quit_button.pack(side=tk.RIGHT, in_=self.statusbar)
        self.statusbar.pack(expand=False, fill=tk.X, side=tk.BOTTOM)

        load_textures()

    def __current_player(self):
        if self.current_turn == SIDE_WHITE:
            return self.player_white
        else:
            return self.player_black

    def click(self, event):
        if self.current_turn == INVALID:
            return

        x = int(event.x / self.square_size)
        y = int(event.y / self.square_size)

        selected_piece = self.board.select_piece(x, y, self.current_turn)
        if selected_piece is EMPTY:
            removed = self.board.move_selected_piece(x, y)
            print("Removed:", removed)

            self.current_turn = SIDE_WHITE if self.current_turn == SIDE_BLACK else SIDE_BLACK

        self.refresh(None)

    def refresh(self, event):
        if event:
            sizeX = int((event.width - 1) / BOARD_SIZE)
            sizeY = int((event.height - 1) / BOARD_SIZE)
            self.square_size = min(sizeX, sizeY)

        self.board.draw_squares()
        self.board.draw_pieces()

    def draw(self):
        pass

    def reset(self):
        self.board.reset()
        self.refresh(None)