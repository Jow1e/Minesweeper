import time
from tinkoff import Minesweeper
from tinkoff.bots import BotMerge


w, h = map(int, input("Field size: ").split())
n_mines = int(input("Number of mines: "))
use_bot = input("Use bot? y/n: ")
use_bot = (use_bot == "y")

time_del = float(input("Time sleep between moves: ")) if use_bot else 0

board = Minesweeper(size=(w, h), n_mines=n_mines)

bot = BotMerge(board) if use_bot else None

board.play(bot, sleep_time=time_del)
