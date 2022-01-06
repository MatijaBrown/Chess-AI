import tkinter as tk

from common import *
import game
import pieces


class ChessGame:

    def __init__(self, top: tk.Tk) -> None:
        self.top = top
        self.top.protocol("WM_DELETE_WINDOW", self._destroy)

        self._setup_ui()

        self.canvas.bind("<Configure>", self._on_tk_event)
        self.canvas.bind("<Button-1>", self._on_click)

        self.ai_is_white = False

        self.running_game = None

    def _setup_ui(self):
        self.menubar = tk.Menu(self.top)

        self.filemenu = tk.Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="New Game", command=self._new_game)

        self.menubar.add_cascade(label="File", menu=self.filemenu)
        self.top.config(menu=self.menubar)

        self.gamemenu = tk.Menu(self.menubar, tearoff=0)
        self.gamemenu.add_command(label="Switch Sides", command=self._switch_sides)

        self.menubar.add_cascade(label="Game", menu=self.gamemenu)
        self.top.config(menu=self.menubar)

        self.btm_frame = tk.Frame(self.top, height=64)

        self.info_label = tk.Label(self.btm_frame, text="Waiting for game to start ...", fg=game.COLOUR_BLACK)
        self.info_label.pack(side=tk.RIGHT, padx=8, pady=5)

        self.btm_frame.pack(fill='x', side=tk.BOTTOM)

        self.square_size = 64
        self.canvas = tk.Canvas(self.top, width=self.square_size * BOARD_SIZE, height=self.square_size * BOARD_SIZE)
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, anchor="c", expand=True)


    def _switch_sides(self):
        self.ai_is_white = not self.ai_is_white
        if self.running_game:
            self.running_game.setup_players(self.ai_is_white)

    def _new_game(self):
        if self.running_game is not None:
            self.running_game.end()
        self.running_game = game.Game(self, self.ai_is_white, DEFAULT_STARTING_FEN)
        self.running_game.run()

    def _on_click(self, event):
        if self.running_game is not None:
            self.running_game.on_click(event.x, event.y)

    def _on_tk_event(self, event):
        size_x = int((event.width - 1) / BOARD_SIZE)
        size_y = int((event.height - 1) / BOARD_SIZE)
        self.square_size = min(size_x, size_y)

        if self.running_game is not None:
            self.running_game.draw()

    def _reset_game(self):
        self.running_game.end()
        self.running_game = None

    def _destroy(self):
        self._reset_game()
        self.top.destroy()