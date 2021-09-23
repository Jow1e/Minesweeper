import numpy as np
from scipy.optimize import nnls


class BotMat:
	"""
	
	Create linear equations when sees a number > 0 in cell and solves them (making matrix) with Gaussian method
	Often number of equations is less than variables, it causes many different solutions
	
	"""
	
	UNDEF = "."
	
	def __init__(self, board, eps: float = 1e-5):
		self.board = board
		self.delta = 0
		self.eps = eps
		self.solution = [[self.UNDEF] * self.board.width for _ in range(self.board.height)]
		self.xn = ...
		self.found_mines = [[False] * self.board.width for _ in range(self.board.height)]
	
	def act(self):
		if self.board.first_move:
			x = np.random.randint(1, self.board.width + 1)
			y = np.random.randint(1, self.board.height + 1)
			return 0, f"{x} {y} open"
		
		self.calc_matrix()
		
		answer_x = 0
		answer_y = 0
		found = False
		
		for rank in range(self.board.height):
			for file in range(self.board.width):
				if self.board.is_close(rank, file) and (self.valid_solution(rank, file) or not found):
					answer_x = file + 1
					answer_y = rank + 1
					found = True
		
		return self.delta, f"{answer_x} {answer_y} open"
	
	def calc_matrix(self):
		pos2idx = {}
		idx2pos = {}
		index = 0
		numbers = 0
		
		for rank in range(self.board.height):
			for file in range(self.board.width):
				if self.board.is_close(rank, file):
					near_open = False
					
					for delta_rank, delta_file in self.board.delta_index:
						new_rank = rank + delta_rank
						new_file = file + delta_file
						
						if self.board.is_open(new_rank, new_file):
							near_open = True
							break
					
					position = (rank, file)
					
					if near_open and position not in pos2idx.keys():
						pos2idx[position] = index
						idx2pos[index] = position
						index += 1
					
					if self.found_mines[rank][file]:
						numbers += 1
				
				elif self.board.field[rank][file] != 0:
					numbers += 1
		
		matrix = np.zeros(shape=(numbers, index))
		answers = np.zeros(shape=numbers)
		row = 0
		
		for rank in range(self.board.height):
			for file in range(self.board.width):
				if self.found_mines[rank][file]:
					position = (rank, file)
					column = pos2idx[position]
					matrix[row][column] = 1
					answers[row] = 1
					row += 1
				
				if self.board.is_open(rank, file) and self.board.field[rank][file] != 0:
					for delta_rank, delta_file in self.board.delta_index:
						new_rank = rank + delta_rank
						new_file = file + delta_file
						
						if self.board.is_close(new_rank, new_file):
							position = (new_rank, new_file)
							column = pos2idx[position]
							matrix[row][column] = 1
					
					answers[row] = self.board.field[rank][file]
					row += 1
		
		self.xn, self.delta = nnls(matrix, answers)
		self.xn = self.xn.tolist()
		
		self.solution = [[self.UNDEF] * self.board.width for _ in range(self.board.height)]
		for index, result in enumerate(self.xn):
			rank, file = idx2pos[index]
			self.solution[rank][file] = result
	
	def show(self):
		print("\n MAT mines prediction:")
		dist = " " * 2
		print("\n", dist, *range(1, self.board.width + 1), "\n")
		
		for rank in range(self.board.height):
			dist = " " * (4 - len(str(rank + 1)))
			print(rank + 1, end=dist)
			
			for file in range(self.board.width):
				dist = " " * len(str(file + 1))
				
				cell = self.solution[rank][file]
				cell = round(cell) if cell != self.UNDEF else cell
				print(cell, end=dist)
			
			print()
		print()
	
	def valid_solution(self, rank: int, file: int):
		sol = self.solution[rank][file]
		return self.board.is_close(rank, file) and sol != self.UNDEF and abs(sol) < self.eps
