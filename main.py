from chess import Chess

import tkinter as tk

def run():
    top = tk.Tk()
    top.title("Simple Python Chess")

    chess = Chess(top)
    chess.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.TRUE, padx=4, pady=4)
    chess.draw()

    top.mainloop()

if __name__ == "__main__":
    run()