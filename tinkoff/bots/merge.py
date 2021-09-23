import pickle
from tinkoff.bots import BotProb, BotMat
from tinkoff.bots.pattern import BotPat


class BotMerge:
	"""
	
	This bot uses BotMat, BotProb and BotPat
	
	Separately, these bots aren't really good:
		* BotMat can solve (10, 10) + 10 board (19 % win-rate)
		* BotProb can solve (10, 10) + 10 board with higher probability and sometimes wins (20, 20) + 40 (42 % win-rate)
		* BotPat can't play xD
		
	* Merged bot often (74 % win-rate) solves (20, 20) + 40 game but still not able to solve (16, 30) + 90
	
	* !!! Each win-rate was tested on 1000 games
	
	* Bot is quite sensitive to hyper parameters (`n_prob_moves` and `n_nearby_opens`)
	
	The main problems are:
		1. There are different solutions
		2. Difficult to define if prediction is good or not, if there is not enough information about cell we can't rely
			on luck
		3. Sometimes BotMat solution predicts that all around cells are mines
	
	* To solve these problems I used BotProb (it gives cells a probability of being a mine)
		But as we see, it's not enough...
	
	"""
	
	def __init__(self, board, n_prob_moves: int = 20, n_nearby_opens: int = 2, info: bool = False):
		"""
		
		:param board: game board
		:param n_prob_moves: make moves with prob bot till n_opens reaches `n_prob_moves`
		:param n_nearby_opens: use mat bot only if it is sure that cell is not mine and it has `n_nearby_opens`
		:param info: print some stuff
		
		"""
		
		self.board = board
		self.n_prob_moves = n_prob_moves
		self.info = info
		self.n_nearby_opens = n_nearby_opens
		
		self.bot_prob = BotProb(self.board)
		self.bot_mat = BotMat(self.board)
		self.bot_pat = BotPat(self.board)
	
	def act(self):
		self.bot_pat.find_patterns()
		
		for rank, file in self.bot_pat.safe_positions:
			if self.board.is_close(rank, file):
				if self.info:
					print("Pattern [1 2 1] was used")
				
				x = file + 1
				y = rank + 1
				return 1, f"{x} {y} open"
		
		if self.board.n_opens <= self.n_prob_moves:
			if self.info:
				print("Prob was used")
			
			return self.bot_prob.act()
		
		self.bot_prob.calc_probs()
		self.merge_mines_found()
		self.bot_mat.calc_matrix()
		
		answer_rank = 0
		answer_file = 0
		min_prob = 1.0
		nearby_open = 1
		
		found = False
		
		for rank in range(self.board.height):
			for file in range(self.board.width):
				cur_prob = self.bot_prob.prob_field[rank][file]
				cur_nearby_open = self.bot_prob.nearby_opens(rank, file)
				
				if self.bot_mat.valid_solution(rank, file) and cur_prob / (cur_nearby_open ** 1.5) < min_prob / (
						nearby_open ** 1.5) and cur_nearby_open >= self.n_nearby_opens:
					found = True
					answer_rank = rank
					answer_file = file
					min_prob = cur_prob
					nearby_open = cur_nearby_open
		
		if self.info:
			self.bot_mat.show()
			self.bot_prob.show()
			print("DELTA:", self.bot_mat.delta)
			print(self.bot_mat.xn)
			print("NEAR:", nearby_open)
			print("FOUND:", found)
		
		if not found:
			if self.info:
				print("Prob was used")
			
			return self.bot_prob.act()
		
		x = answer_file + 1
		y = answer_rank + 1
		
		action = f"{x} {y} open"
		
		return min_prob, action
	
	def merge_mines_found(self):
		for rank in range(self.board.height):
			for file in range(self.board.width):
				self.bot_mat.found_mines[rank][file] = self.bot_prob.found_mines[rank][file]
	
	def save(self, path: str):
		print("\n... saving bot ...")
		with open(path, "wb") as file:
			pickle.dump(self, file, pickle.HIGHEST_PROTOCOL)
		print("... bot saved!!!")
	
	@staticmethod
	def load(path: str):
		print("\n... loading bot ...")
		with open(path, "rb") as file:
			bot = pickle.load(file)
		print("... bot loaded!!!")
		return bot
