import random
import numpy as np


class BotProb:
	""" gives cells a (with good accuracy) probability of being a mine """
	
	def __init__(self, board):
		self.board = board
		self.default_prob = self.board.n_mines / self.board.len
		self.prob_field = [[self.default_prob] * self.board.width for _ in range(self.board.height)]
		self.found_mines = [[False] * self.board.width for _ in range(self.board.height)]
	
	def act(self):
		if self.board.first_move:
			x = np.random.randint(1, self.board.width + 1)
			y = np.random.randint(1, self.board.height + 1)
			return 0, f"{x} {y} open"
		
		self.calc_probs()
		
		min_prob = 1.0
		answer_rank = 0
		answer_file = 0
		
		rank_dim = list(range(self.board.height))
		file_dim = list(range(self.board.width))
		
		random.shuffle(rank_dim)
		random.shuffle(file_dim)
		
		for rank in rank_dim:
			for file in file_dim:
				cur_prob = self.prob_field[rank][file]
				
				if self.board.is_close(rank, file) and min_prob > cur_prob:
					min_prob = cur_prob
					answer_rank, answer_file = rank, file
		
		x = answer_file + 1
		y = answer_rank + 1
		
		action = f"{x} {y} open"
		
		return min_prob, action
	
	def calc_probs(self):
		self.default_prob = self.board.n_mines / (self.board.len - self.board.n_opens)
		self.prob_field = [[self.default_prob] * self.board.width for _ in range(self.board.height)]
		
		for rank in range(self.board.height):
			for file in range(self.board.width):
				if self.board.is_close(rank, file):
					cell_probs = []
					
					for delta_rank, delta_file in self.board.delta_index:
						new_rank = rank + delta_rank
						new_file = file + delta_file
						
						if self.board.is_open(new_rank, new_file):
							cell = self.board.field[new_rank][new_file]
							num = 0
							
							for dd_rank, dd_file in self.board.delta_index:
								nn_rank = new_rank + dd_rank
								nn_file = new_file + dd_file
								
								if self.board.is_close(nn_rank, nn_file):
									num += 1
							
							prob = cell / num
							cell_probs.append(prob)
					
					if len(cell_probs) != 0:
						cell_real_prob = self.single_prob(cell_probs)
						self.prob_field[rank][file] = cell_real_prob
						
						if self.is_mine(rank, file):
							self.found_mines[rank][file] = True
	
	def single_prob(self, x: list):
		""" Inclusion - exclusion principle """
		x = np.array(x)
		P = 0
		for mask in range(1, 1 << len(x)):  # iterate through all subsets
			indices = self.bit_repr(mask, len(x))  # create indices i.e. boolean array of True/False
			size = np.count_nonzero(indices)  # size of subset (num of True)
			prod = np.prod(x[indices])  # Union of probs in subset
			
			P = P + prod if (size % 2) == 1 else P - prod
		
		return P
	
	@staticmethod
	def bit_repr(mask: int, mask_size: int):
		return (mask & (1 << np.arange(mask_size))) != 0
	
	def is_mine(self, rank: int, file: int):
		return self.prob_field[rank][file] > 0.9999
	
	def show(self):
		print("\n PROB mines prediction 100%:")
		dist = " " * 2
		print("\n", dist, *range(1, self.board.width + 1), "\n")
		
		for rank in range(self.board.height):
			dist = " " * (4 - len(str(rank + 1)))
			print(rank + 1, end=dist)
			
			for file in range(self.board.width):
				dist = " " * len(str(file + 1))
				
				cell = int(self.found_mines[rank][file])
				print(cell, end=dist)
			
			print()
		print()
	
	def nearby_opens(self, rank: int, file: int):
		nearby_opens = 0
		for delta_rank, delta_file in self.board.delta_index:
			new_rank = rank + delta_rank
			new_file = file + delta_file
			
			if self.board.is_open(new_rank, new_file):
				nearby_opens += 1
		
		return nearby_opens
