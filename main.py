import tkinter as tk
import application as app


def run():
    top = tk.Tk()
    top.title("Chess")
    chess = app.ChessGame(top)
    top.mainloop()


if __name__ == "__main__":
    run()