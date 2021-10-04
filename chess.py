from board import *
from piece import SIDE_WHITE, SIDE_BLACK

import tkinter as tk

INITIAL_SQUARE_SIZE = 64

class Chess(tk.Frame):
    
    def __init__(self, top):
        self.top = top
        self.square_size = INITIAL_SQUARE_SIZE
        self.canvas_size = self.square_size * BOARD_SIZE

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

        self.status_label = tk.Label(self.statusbar, text="    White's turn    ", fg="black")
        self.status_label.pack(side=tk.LEFT, in_=self.statusbar)

        self.turn_status = SIDE_WHITE
        self.selected_piece = None

        self.quit_button = tk.Button(self.statusbar, text="Quit", fg="black", command=self.top.destroy)
        self.quit_button.pack(side=tk.RIGHT, in_=self.statusbar)
        self.statusbar.pack(expand=False, fill=tk.X, side=tk.BOTTOM)

    def click(self, event):
        x = int(event.x / self.square_size)
        y = 7 - int(event.y / self.square_size)

        self.selected_piece = self.board.select_piece(x, y, self.turn_status)

        self.refresh(None)

    def refresh(self, event):
        if event:
            sizeX = int((event.width - 1) / BOARD_SIZE)
            sizeY = int((event.height - 1) / BOARD_SIZE)
            self.square_size = min(sizeX, sizeY)

        self.board.draw()
        self.board.draw_pieces()
        self.canvas.tag_raise("piece")
        self.canvas.tag_lower("square")

    def draw(self):
        pass

    def reset(self):
        self.board.reset()
        self.refresh(None)