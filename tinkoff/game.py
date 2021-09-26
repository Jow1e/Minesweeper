import time
import random
import pickle

from queue import Queue


class Minesweeper:
	"""
			Top left cell has coords: (1, 1)


			Board symbols:
				* Hidden: '.'
				* Flag: '?'
				* Mine: '*'

			Actions:
				* X Y Open
				* X Y Flag
				* Stop

			For playing just use `play()` method
			For testing bot use `play(bot)`

	"""
	
	HIDDEN = "."
	FLAG = "?"
	MINE = "*"
	EMPTY = "."
	
	open = "open"
	flag = "flag"
	stop = "stop"
	
	delta_index = [(0, -1), (-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1)]
	
	def __init__(self, size: tuple[int, int], n_mines: int, vis: bool = True, seed: int = None):
		"""

		:param size: (width, height) of board
		:param n_mines: number of mines on board
		:param vis: visualise board in console
		:param seed: random seed to make game repeatable

		"""
		
		random.seed(seed)
		
		self.vis = vis
		self.size = size
		self.width, self.height = size
		self.len = self.width * self.height
		self.n_mines = n_mines
		self.n_opens = 0
		
		self.first_move = True
		self.win = False
		self.lose = False
		self.stopped = False
		self.max_score = self.len - n_mines
		
		self.__mines = [[self.EMPTY] * self.width for _ in range(self.height)]
		self.field = [[self.HIDDEN] * self.width for _ in range(self.height)]
		
		if vis:
			self.show()
	
	def set_mines(self, except_rank: int, except_file: int):
		except_idx = except_rank * self.width + except_file
		
		indices = list(range(self.len))
		indices.remove(except_idx)
		
		for delta_rank, delta_file in self.delta_index:
			new_rank = except_rank + delta_rank
			new_file = except_file + delta_file
			
			if self.valid_idx(new_rank, new_file):
				new_idx = new_rank * self.width + new_file
				indices.remove(new_idx)
		
		random.shuffle(indices)
		
		indices = indices[:self.n_mines]
		indices = [(idx // self.width, idx % self.width) for idx in indices]
		
		for rank, file in indices:
			self.__mines[rank][file] = self.MINE
	
	def show(self):
		self.__show(self.field)
	
	def __show_mines(self):
		self.__show(self.__mines)
	
	def __show(self, board):
		dist = " " * 2
		print("\n", dist, *range(1, self.width + 1), "\n")
		
		for rank in range(self.height):
			dist = " " * (4 - len(str(rank + 1)))
			print(rank + 1, end=dist)
			
			for file in range(self.width):
				dist = " " * len(str(file + 1))
				print(board[rank][file], end=dist)
			
			print()
		print()
	
	def act(self, action: str):
		if action.lower() == "stop":
			self.stopped = True
		elif "save" in action.lower():
			_, file_name = action.lower().split()
			self.save(file_name)
		elif "load" in action.lower():
			_, file_name = action.lower().split()
			self.__dict__.update(self.load(file_name).__dict__)
		else:
			x, y, action = action.lower().split()
			
			file = int(x) - 1
			rank = int(y) - 1
			
			if action == self.open and self.is_close(rank, file):
				if self.first_move:
					self.set_mines(rank, file)
					self.first_move = False
				if self.is_mine(rank, file):
					self.field[rank][file] = self.MINE
					self.lose = True
				else:
					self.open_cells(rank, file)
			elif action == self.flag:
				if self.is_hidden(rank, file):
					self.field[rank][file] = self.FLAG
				elif self.is_flag(rank, file):
					self.field[rank][file] = self.HIDDEN
			else:
				print(f"Warning! Undefined action or invalid position")
			
			self.win = (self.n_opens == self.max_score)
			
			if self.vis:
				self.show()
	
	def open_cells(self, start_rank: int, start_file: int):
		""" open the required cells (using BFS) """
		
		used = [[False] * self.width for _ in range(self.height)]
		used[start_rank][start_file] = True
		
		queue = Queue()
		queue.put((start_rank, start_file))
		
		while not queue.empty():
			rank, file = queue.get()
			
			if self.is_close(rank, file):
				number = self.__calc_cell(rank, file)
				self.field[rank][file] = number
				self.n_opens += 1
			else:
				continue
			
			if number != 0:
				continue
			
			for delta_rank, delta_file in self.delta_index:
				new_rank = rank + delta_rank
				new_file = file + delta_file
				
				if self.valid_idx(new_rank, new_file) and not used[new_rank][new_file]:
					used[new_rank][new_file] = True
					queue.put((new_rank, new_file))
	
	def done(self):
		if self.stopped:
			print("Game stopped!")
		elif self.win:
			print("You win!")
		elif self.lose:
			if self.vis:
				self.__show_mines()
			print("You lose!")
		
		done = (self.win or self.lose or self.stopped)
		self.stopped = False
		
		return done
	
	def __calc_cell(self, rank: int, file: int):
		nearby_mines = 0
		for delta_rank, delta_file in self.delta_index:
			new_rank = rank + delta_rank
			new_file = file + delta_file
			
			if self.is_mine(new_rank, new_file):
				nearby_mines += 1
		
		return nearby_mines
	
	def save(self, path: str):
		print("\n... saving game ...")
		with open(path, "wb") as file:
			pickle.dump(self, file, pickle.HIGHEST_PROTOCOL)
		print("... game saved!!! \n")
		
		self.show()
	
	@staticmethod
	def load(path: str):
		print("\n... loading game ...")
		with open(path, "rb") as file:
			game_state = pickle.load(file)
		print("... game loaded!!! \n")
		
		game_state.show()
		return game_state
	
	def play(self, bot=None, sleep_time=0):
		while not self.done():
			if bot is None:
				action = input("action: ")
			else:
				time.sleep(sleep_time)
				min_prob, action = bot.act()
				
				if self.vis:
					print(min_prob, action)
			
			self.act(action)
	
	def is_hidden(self, rank: int, file: int):
		return self.valid_idx(rank, file) and self.field[rank][file] == self.HIDDEN
	
	def is_flag(self, rank: int, file: int):
		return self.valid_idx(rank, file) and self.field[rank][file] == self.FLAG
	
	def is_close(self, rank: int, file: int):
		return self.valid_idx(rank, file) and isinstance(self.field[rank][file], str)
	
	def is_open(self, rank: int, file: int):
		return self.valid_idx(rank, file) and isinstance(self.field[rank][file], int)
	
	def is_mine(self, rank: int, file: int):
		return self.valid_idx(rank, file) and self.__mines[rank][file] == self.MINE
	
	def valid_idx(self, rank: int, file: int):
		return 0 <= rank < self.height and 0 <= file < self.width
