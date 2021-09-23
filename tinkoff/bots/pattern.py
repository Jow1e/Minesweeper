class BotPat:
	"""
	
	find pattern on board
	
	"""
	
	pat1 = [1, 2, 1]
	
	def __init__(self, board):
		self.board = board
		self.safe_positions = []
	
	def find_patterns(self):
		self.safe_positions = []
		
		for rank in range(self.board.height):
			for file in range(self.board.width):
				if self.board.field[rank][file] == 2:
					if self.board.valid_idx(rank + 1, file) and self.board.field[rank + 1][file] == 1 and \
							self.board.valid_idx(rank - 1, file) and self.board.field[rank - 1][file] == 1:
						
						self.safe_positions.append((rank, file + 1))
						self.safe_positions.append((rank, file - 1))
					elif self.board.valid_idx(rank, file + 1) and self.board.field[rank][file + 1] == 1 and \
							self.board.valid_idx(rank, file - 1) and self.board.field[rank][file - 1] == 1:
						
						self.safe_positions.append((rank - 1, file))
						self.safe_positions.append((rank + 1, file))
