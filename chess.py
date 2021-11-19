from common import *

import board
import players
import pieces

import tkinter as tk

class Chess(tk.Frame):
    
    def __init__(self, top):
        self.top = top
        self.square_size = 64
        self.canvas_size = self.square_size * BOARD_SIZE

        tk.Frame.__init__(self, self.top)

        self.canvas = tk.Canvas(self, width=self.canvas_size, height=self.canvas_size, background="white")
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, anchor="c", expand=tk.TRUE)

        self.canvas.bind("<Configure>", self.refresh)
        self.canvas.bind("<Button-1>", self.__click)

        self.board = board.Board(self)

        self.player_white = players.HumanPlayer(self, SIDE_WHITE)
        self.board.player_white = self.player_white
        self.player_black = players.HumanPlayer(self, SIDE_BLACK)
        self.board.player_black = self.player_black
        self.current_side = SIDE_NONE

        self.statusbar = tk.Frame(self, height=64)
        self.new_button = tk.Button(self.statusbar, text="New", fg="black", command=self.__reset)
        self.new_button.pack(side=tk.LEFT, in_=self.statusbar)

        self.status_label = tk.Label(self.statusbar, text="    Waiting to start game...    ", fg="black")
        self.status_label.pack(side=tk.LEFT, in_=self.statusbar)

        self.quit_button = tk.Button(self.statusbar, text="Quit", fg="black", command=self.top.destroy)
        self.quit_button.pack(side=tk.RIGHT, in_=self.statusbar)
        self.statusbar.pack(expand=False, fill=tk.X, side=tk.BOTTOM)

        pieces.load_textures()

    def get_player(self, side):
        if side == SIDE_WHITE:
            return self.player_white
        elif side == SIDE_BLACK:
            return self.player_black
        elif side == SIDE_NONE:
            return None

    def get_current_player(self):
        return self.get_player(self.current_side)

    def set_side(self, side):
        if self.get_current_player():
            self.get_current_player().post_turn()
        self.current_side = side
        if self.get_current_player():
            self.get_current_player().pre_turn()
            self.status_label["text"] = "White's Turn" if self.current_side == SIDE_WHITE else "Blacks' Turn"
        self.refresh()

    def switch_side(self):
        if self.get_current_player().lost():
            self.status_label["text"] = "White won!" if self.current_side == SIDE_BLACK else "Black won!"
            self.current_side = SIDE_NONE
        elif self.get_current_player().drew():
            self.status_label["text"] = "White " if self.current_side == SIDE_BLACK else "Black " + "is in check but can't move. It's a draw!"
            self.current_side = SIDE_NONE
        self.set_side(-self.current_side)
        if self.get_current_player():
            self.get_current_player().move()

    def __click(self, event):
        if not self.get_current_player():
            return
        sX = int(event.x / self.square_size)
        sY = int(event.y / self.square_size)
        if self.get_current_player().on_click(sX, sY) or self.get_current_player().lost() or self.get_current_player().drew():
            self.switch_side()
        else:
            self.refresh()

    def refresh(self, event = None):
        if event:
            sizeX = int((event.width - 1) / BOARD_SIZE)
            sizeY = int((event.height - 1) / BOARD_SIZE)
            self.square_size = min(sizeX, sizeY)
        self.board.draw()

    def __reset(self):
        self.board.reset()
        self.refresh()
        self.get_current_player().move()