import pygame
import sys
import time


class Board:
	"""
	class mô phỏng bàn cờ và thế cờ hiện tại
	thuộc tính:
		whiteTurn: xác định đang là lượt của trắng hay đen
		dimension: chiều của bàn cờ
		square_size : kích thước của 1 ô trong bàn cờ
		en_passant_target: mục tiêu sẽ bắt tốt qua đường  ( nếu có)
		các màu sắc: dùng đê trang trí
		images: lưu hình ảnh png của từng quân cờ
	phương thức:
		load_image: tải ảnh quân cờ lên
		draw_piece: vẽ từng quân cờ lên bàn cờ
		draw_chess_board: vẽ bàn cờ
		highlight_squares: tô màu những nước đi có thể đi được của từng quân cờ trong 1 thế cờ 
		piece_from_string: hàm chuyển đổi ký hiệu quân cờ trong bàn cờ sang class nhanh hơn
		move_piece: thực hiện di chuyển quân cờ
		is_valid_move: xác định xem nước đi người chơi muốn đi có hợp lệ không (nước đi này có dẫn tới vua bị chiếu , vua đang bị chiếu nhưng không tìm cách bảo vệ)
		make_temporary_move: giả sử đi nước đi của người chơi muốn đi rồi kiểm tra xem có hợp lệ không
		revert_temporary_move: nếu không hợp lệ sẽ trả lại thế cờ cũ
		is_in_check: kiểm tra xem vua có đang bị chiếu không
		find_king: xác định vị trí của vua



	"""
	def __init__(self):
		self.board = [["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
					  ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
					  ["--", "--", "--", "--", "--", "--", "--", "--"],
					  ["--", "--", "--", "--", "--", "--", "--", "--"],
					  ["--", "--", "--", "--", "--", "--", "--", "--"],
					  ["--", "--", "--", "--", "--", "--", "--", "--"],
					  ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
					  ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]
		self.whiteTurn = True
		self.dimension = 8
		self.square_side = 64
		self.en_passant_target = None

		self.LIGHT_BLUE = (66, 191, 245)
		self.WHITE = (255, 255, 255)
		self.GREY = (125, 125, 125)
		self.YELLOW = (247, 244, 143)
		self.RED = (242, 2, 2)
		self.BLACK = (0, 0, 0)
		self.GREEN = (108, 245, 66)
		self.images = {}
		self.load_image()

	def load_image(self):
		piece_images = ["bR", "bN", "bB", "bQ", "bK",
						"bp", "wp", "wR", "wN", "wB", "wQ", "wK"]
		for piece_image in piece_images:
			self.images[piece_image] = pygame.transform.smoothscale(
				pygame.image.load(piece_image + ".png"), (self.square_side, self.square_side))

	def draw_pieces(self, screen):
		for i in range(self.dimension):
			for j in range(self.dimension):
				piece = self.board[i][j]
				if piece != "--":
					screen.blit(self.images[piece], pygame.Rect(
						j * self.square_side, i * self.square_side + 100, self.square_side, self.square_side))

	def draw_chess_board(self, screen):
		for i in range(self.dimension):
			for j in range(self.dimension):
				color = self.LIGHT_BLUE if (i + j) % 2 == 1 else self.WHITE
				pygame.draw.rect(screen, color, (j * self.square_side, i * self.square_side + 100, self.square_side, self.square_side))

	def highlight_squares(self, screen, valid_moves, start_pos):
		for move in valid_moves:
			if self.is_valid_move(start_pos, move):
				pygame.draw.rect(screen, self.YELLOW, (move[1] * self.square_side, move[0] * self.square_side + 100, self.square_side, self.square_side))

	def piece_from_string(self, piece_str):
		color = piece_str[0]
		piece_type = piece_str[1]
		if piece_type == 'p':
			return Pawn(color)
		elif piece_type == 'N':
			return Knight(color)
		elif piece_type == 'B':
			return Bishop(color)
		elif piece_type == 'R':
			return Rook(color)
		elif piece_type == 'Q':
			return Queen(color)
		elif piece_type == 'K':
			return King(color)
		return None

	def move_piece(self, start_pos, end_pos):
		piece_str = self.board[start_pos[0]][start_pos[1]]
		piece = self.piece_from_string(piece_str)
		if piece:
			piece.move(start_pos, end_pos, self)
		self.whiteTurn = not self.whiteTurn

	def is_valid_move(self, start_pos, end_pos):
		piece_str = self.board[start_pos[0]][start_pos[1]]
		piece = self.piece_from_string(piece_str)
		if piece:
			valid_moves = piece.get_valid_moves(start_pos, self)
			if end_pos in valid_moves:
				self.make_temporary_move(start_pos, end_pos)

				if not self.is_in_check(self.whiteTurn):
	
					self.revert_temporary_move(start_pos, end_pos, piece_str)
					return True

				self.revert_temporary_move(start_pos, end_pos, piece_str)
		return False

	def make_temporary_move(self, start_pos, end_pos):
		self.temp_piece = self.board[end_pos[0]][end_pos[1]]
		self.board[end_pos[0]][end_pos[1]] = self.board[start_pos[0]][start_pos[1]]
		self.board[start_pos[0]][start_pos[1]] = "--"

	def revert_temporary_move(self, start_pos, end_pos, piece_str):
		self.board[start_pos[0]][start_pos[1]] = piece_str
		self.board[end_pos[0]][end_pos[1]] = self.temp_piece

	def is_in_check(self, white_turn):
		king_pos = self.find_king(white_turn)
		for row in range(self.dimension):
			for col in range(self.dimension):
				piece_str = self.board[row][col]
				if piece_str != "--" and piece_str[0] != ("w" if white_turn else "b"):
					piece = self.piece_from_string(piece_str)
					if piece:
						valid_moves = piece.get_valid_moves((row, col), self)
						if king_pos in valid_moves:
							return True
		return False

	def find_king(self, white_turn):
		for row in range(self.dimension):
			for col in range(self.dimension):
				if self.board[row][col] == ("wK" if white_turn else "bK"):
					return (row, col)
		return None



class Piece:
	"""
	class các quân cờ chung:
	thuộc tính :
		color: màu của quân cờ (Trắng,đen)
		moves: các nước đi của quân cờ đó
	"""
	def __init__(self, color):
		self.color = color
		self.moves = []


class Pawn(Piece):
	"""
	class của Tốt
	thuộc tính :
		en_passant : có thể bắt tốt qua đường được hay không?
		promotion: có thể phong hậu được hay không?
	phương thức:
		get_valid_moves: tạo ra tất cả nước đi hợp lệ (đi vào ô trống hoặc ô có quân đối thủ)
		move: di chuyển quân nếu nước đi hợp lệ
		promote_pawn: phong hậu nếu hợp lệ

	"""
	def __init__(self, color):
		super().__init__(color)
		self.en_passant = False
		self.promotion = False

	def get_valid_moves(self, position, board):
		row, col = position
		piece = board.board[row][col]
		direction = -1 if piece == "wp" else 1
		start_row = 6 if piece == "wp" else 1

	
		if board.board[row + direction][col] == "--":
			self.moves.append((row + direction, col))

			if row == start_row and board.board[row + 2 * direction][col] == "--":
				self.moves.append((row + 2 * direction, col))

	
		if col - 1 >= 0 and board.board[row + direction][col - 1] != "--" and board.board[row + direction][col - 1][0] != piece[0]:
			self.moves.append((row + direction, col - 1))
		if col + 1 < board.dimension and board.board[row + direction][col + 1] != "--" and board.board[row + direction][col + 1][0] != piece[0]:
			self.moves.append((row + direction, col + 1))

	
		if board.en_passant_target and row + direction == board.en_passant_target[0] and abs(col - board.en_passant_target[1]) == 1:
			self.moves.append(board.en_passant_target)

		return self.moves

	def move(self, start_pos, end_pos, board):
		piece = board.board[start_pos[0]][start_pos[1]]

		if abs(end_pos[0] - start_pos[0]) == 1 and abs(end_pos[1] - start_pos[1]) == 1 and board.board[end_pos[0]][end_pos[1]] == "--":
			if board.whiteTurn:
				board.board[end_pos[0] + 1][end_pos[1]] = "--"
			else:
				board.board[end_pos[0] - 1][end_pos[1]] = "--"
		board.board[start_pos[0]][start_pos[1]] = "--"
		board.board[end_pos[0]][end_pos[1]] = piece

		if abs(end_pos[0] - start_pos[0]) == 2:
			board.en_passant_target = ((end_pos[0] + start_pos[0]) // 2, end_pos[1])
		else:
			board.en_passant_target = None

		if end_pos[0] == 0 or end_pos[0] == 7:
			self.promote_pawn(end_pos, board)

	def promote_pawn(self, pos, board):
		while True:
			promotion_choice = input("Promote pawn to (Q, R, B, N): ").upper()
			if promotion_choice in ['Q', 'R', 'B', 'N']:
				board.board[pos[0]][pos[1]] = board.board[pos[0]][pos[1]][0] + promotion_choice
				board.load_image()  # Reload images to ensure the new piece is drawn correctly
				break
			else:
				print("Invalid choice. Please choose Q, R, B, or K.")

class Knight(Piece):
	"""
	class của mã
	thuộc tính:
		potential_moves: tất cả nước đi có thể của mã
	phương thức:
		get_valid_moves: kiểm tra những nước đi nào là hợp lệ( đi vào ô trống hoặc ăn quân đối thủ)
		move: thực hiện di chuyển mã nếu hợp lệ
	"""
	def __init__(self, color):
		super().__init__(color)
		self.potential_moves = [
			(2, 1), (2, -1), (-2, 1), (-2, -1),
			(1, 2), (1, -2), (-1, 2), (-1, -2)
		]

	def get_valid_moves(self, position, board):
		row, col = position
		for move in self.potential_moves:
			move_row, move_col = row + move[0], col + move[1]
			if 0 <= move_row < board.dimension and 0 <= move_col < board.dimension:
				if board.board[move_row][move_col] == "--" or board.board[move_row][move_col][0] != board.board[row][col][0]:
					self.moves.append((move_row, move_col))
		return self.moves

	def move(self, start_pos, end_pos, board):
		piece = board.board[start_pos[0]][start_pos[1]]
		board.board[start_pos[0]][start_pos[1]] = "--"
		board.board[end_pos[0]][end_pos[1]] = piece

class Bishop(Piece):
	"""
	class của tượng
	thuộc tính:
		directions: tất cả nước đi có thể của tượng
	phương thức:
		get_valid_moves: kiểm tra những nước đi nào là hợp lệ( đi vào ô trống hoặc ăn quân đối thủ)
		move: thực hiện di chuyển tượng nếu hợp lệ
	"""
	def __init__(self, color):
		super().__init__(color)
		self.directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

	def get_valid_moves(self, position, board):

		row, col = position
		for direction in self.directions:
			for i in range(1, board.dimension):
				move_row = row + direction[0] * i
				move_col = col + direction[1] * i
				if 0 <= move_row < board.dimension and 0 <= move_col < board.dimension:
					if board.board[move_row][move_col] == "--":
						self.moves.append((move_row, move_col))
					elif board.board[move_row][move_col][0] != board.board[row][col][0]:
						self.moves.append((move_row, move_col))
						break
					else:
						break
				else:
					break
		return self.moves

	def move(self, start_pos, end_pos, board):
		piece = board.board[start_pos[0]][start_pos[1]]
		board.board[start_pos[0]][start_pos[1]] = "--"
		board.board[end_pos[0]][end_pos[1]] = piece

class Rook(Piece):
	"""
	class của xe
	thuộc tính:
		directions: tất cả nước đi có thể của xe
		moved: xe này đã di chuyển chưa ( để nhập thành)
	phương thức:
		get_valid_moves: kiểm tra những nước đi nào là hợp lệ( đi vào ô trống hoặc ăn quân đối thủ)
		move: thực hiện di chuyển xe nếu hợp lệ
	"""
	def __init__(self, color):
		super().__init__(color)
		self.directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
		self.moved = False

	def get_valid_moves(self, position, board):
		self.moves = []
		row, col = position
		for direction in self.directions:
			for i in range(1, board.dimension):
				move_row = row + direction[0] * i
				move_col = col + direction[1] * i
				if 0 <= move_row < board.dimension and 0 <= move_col < board.dimension:
					if board.board[move_row][move_col] == "--":
						self.moves.append((move_row, move_col))
					elif board.board[move_row][move_col][0] != board.board[row][col][0]:
						self.moves.append((move_row, move_col))
						break
					else:
						break
				else:
					break
		return self.moves

	def move(self, start_pos, end_pos, board):
		piece = board.board[start_pos[0]][start_pos[1]]
		board.board[start_pos[0]][start_pos[1]] = "--"
		board.board[end_pos[0]][end_pos[1]] = piece
		self.moved = True

class Queen(Piece):
	"""
	class của hậu
	thuộc tính:
		directions: tất cả nước đi có thể của hậu
	phương thức:
		get_valid_moves: kiểm tra những nước đi nào là hợp lệ( đi vào ô trống hoặc ăn quân đối thủ)
		move: thực hiện di chuyển hậu nếu hợp lệ
	"""
	def __init__(self, color):
		super().__init__(color)
		self.directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

	def get_valid_moves(self, position, board):

		row, col = position
		for direction in self.directions:
			for i in range(1, board.dimension):
				move_row = row + direction[0] * i
				move_col = col + direction[1] * i
				if 0 <= move_row < board.dimension and 0 <= move_col < board.dimension:
					if board.board[move_row][move_col] == "--":
						self.moves.append((move_row, move_col))
					elif board.board[move_row][move_col][0] != board.board[row][col][0]:
						self.moves.append((move_row, move_col))
						break
					else:
						break
				else:
					break
		return self.moves

	def move(self, start_pos, end_pos, board):
		piece = board.board[start_pos[0]][start_pos[1]]
		board.board[start_pos[0]][start_pos[1]] = "--"
		board.board[end_pos[0]][end_pos[1]] = piece

class King(Piece):
	"""
	class của vua
	thuộc tính:
		potential_moves: tất cả nước đi có thể của vua
		moved: vua này đã di chuyển chưa ( để nhập thành)
	phương thức:
		get_valid_moves: kiểm tra những nước đi nào là hợp lệ( đi vào ô trống hoặc ăn quân đối thủ)
		move: thực hiện di chuyển vua nếu hợp lệ
	"""
	def __init__(self, color):
		super().__init__(color)
		self.potential_moves = [
			(-1, -1), (-1, 0), (-1, 1),
			(0, -1), (0, 1),
			(1, -1), (1, 0), (1, 1),(0,2),(0,-2)
		]

		self.moved = False

	def get_valid_moves(self, position, board):
		row, col = position
		for move in self.potential_moves:
			move_row, move_col = row + move[0], col + move[1]
			if 0 <= move_row < board.dimension and 0 <= move_col < board.dimension:
				if board.board[move_row][move_col] == "--" or board.board[move_row][move_col][0] != board.board[row][col][0]:
					self.moves.append((move_row, move_col))

		return self.moves

	def move(self, start_pos, end_pos, board):
		piece = board.board[start_pos[0]][start_pos[1]]
		board.board[start_pos[0]][start_pos[1]] = "--"
		board.board[end_pos[0]][end_pos[1]] = piece
		self.moved= True



class MainMenu():
	"""
	class của menu chính
	thuộc tính:
		screen: màn hình game
		buttons: 2 nút chọn tương ướng với chế độ truyền thống và biến thể
	phương thức:
		display: hiện thị và thực hiện thao tác người chơi
		draw_text: vẽ chữ
		draw_button: thiết kế nút chọn
	"""
	def __init__(self, screen):
		self.screen = screen
		self.buttons = [
			{"text": "Normal Game", "rect": pygame.Rect(self.screen.get_width() // 2 - 100, self.screen.get_height() // 2 - 30, 200, 50), "output": 1},
			{"text": "King of the Hill", "rect": pygame.Rect(self.screen.get_width() // 2 - 100, self.screen.get_height() // 2 + 30, 200, 50), "output": 2}
		]

	def display(self):
		while True:
			self.screen.fill((0, 0, 0))
			self.draw_text("Chess Game", 64, (255, 255, 255), self.screen.get_width() // 2, self.screen.get_height() // 4)
			for button in self.buttons:
				self.draw_button(button)
			pygame.display.flip()

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_q:
						pygame.quit()
						sys.exit()
				if event.type == pygame.MOUSEBUTTONDOWN:
					if event.button == 1: 
						for button in self.buttons:
							if button["rect"].collidepoint(event.pos):
								
								return button["output"]

	def draw_text(self, text, size, color, x, y):
		font = pygame.font.Font(None, size)
		text_surface = font.render(text, True, color)
		text_rect = text_surface.get_rect()
		text_rect.midtop = (x, y)
		self.screen.blit(text_surface, text_rect)

	def draw_button(self, button):
		pygame.draw.rect(self.screen, (255, 255, 255), button["rect"], 2)
		self.draw_text(button["text"], 32, (255, 255, 255), button["rect"].centerx, button["rect"].centery - 16)

class GameOverMenu():
	"""
	class của menu khi game kết thúc
	thuộc tính:
		screen: màn hình game
	phương thức:
		display: hiện thị và thực hiện thao tác người chơi
		draw_text: vẽ chữ

	"""
	def __init__(self, screen):
		self.screen = screen
	def display(self, result):

		while True:
			self.screen.fill((0, 0, 0))
			self.draw_text("Game Over", 64, (255, 255, 255), self.screen.get_width() // 2, self.screen.get_height() // 4)
			self.draw_text(result, 32, (255, 255, 255), self.screen.get_width() // 2, self.screen.get_height() // 2)
			self.draw_text("Press any key to return to main menu", 32, (255, 255, 255), self.screen.get_width() // 2, self.screen.get_height() // 1.5)

			pygame.display.flip()

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
				if event.type == pygame.KEYDOWN:
					return
	def draw_text(self, text, size, color, x, y):
		font = pygame.font.Font(None, size)
		text_surface = font.render(text, True, color)
		text_rect = text_surface.get_rect()
		text_rect.midtop = (x, y)
		self.screen.blit(text_surface, text_rect)



def main():
	play = True
	selected_piece = None
	start_pos = None
	valid_moves = []

	


	pygame.init()
	screen = pygame.display.set_mode((512, 612))
	gs = Board()
	check_sound = pygame.mixer.Sound("check.wav")
	move_sound = pygame.mixer.Sound("move.wav")
	end_sound = pygame.mixer.Sound("end.wav")
	game_over_menu  = GameOverMenu(screen)
	capture_sound = pygame.mixer.Sound("capture.wav")
	menu = MainMenu(screen)
	choice = menu.display()

	last_move_time = time.time()
	white_time = 600  
	black_time = 600 
	while play:
		screen.fill(gs.GREY)
		gs.draw_chess_board(screen)
		if choice == 2:

			pygame.draw.rect(screen, gs.GREEN, (3 * gs.square_side, 3 * gs.square_side + 100, gs.square_side, gs.square_side))
			pygame.draw.rect(screen, gs.GREEN, (4 * gs.square_side, 3 * gs.square_side + 100, gs.square_side, gs.square_side))
			pygame.draw.rect(screen, gs.GREEN, (4 * gs.square_side, 4 * gs.square_side + 100, gs.square_side, gs.square_side))
			pygame.draw.rect(screen, gs.GREEN, (3 * gs.square_side, 4 * gs.square_side + 100, gs.square_side, gs.square_side))





		
		current_time = time.time()
		elapsed_time = current_time - last_move_time
		last_move_time = current_time

		if gs.whiteTurn:
			white_time -= elapsed_time
			if white_time <= 0:
				game_over_menu.display("Black wins on time!")

				choice =menu.display()
				gs = Board()
				white_time = 600
				black_time = 600
		else:
			black_time -= elapsed_time
			if black_time <= 0:
				game_over_menu.display("White wins on time!")
				choice = main_menu(screen)
				gs = Board()
				white_time = 600
				black_time = 600

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				play = False

			if event.type == pygame.MOUSEBUTTONDOWN:
				pos = pygame.mouse.get_pos()
				col = pos[0] // gs.square_side
				row = (pos[1] - 100) // gs.square_side

				if selected_piece:
					end_pos = (row, col)
					if gs.is_valid_move(start_pos, end_pos):
						if gs.board[end_pos[0]][end_pos[1]] != "--":
							pygame.mixer.Sound.play(capture_sound)
						gs.move_piece(start_pos, end_pos)


					#check king of the hill
						if selected_piece[1] == "K" and choice == 2:
							if (end_pos[0] == 3 and end_pos[1] == 3) or (end_pos[0] == 3 and end_pos[1] == 4) or (end_pos[0] == 4 and end_pos[1] == 3) or (end_pos[0] == 4 and end_pos[1] == 4):

								pygame.mixer.Sound.play(end_sound)
								game_over_menu.display(" White wins!" if not gs.whiteTurn else "Black wins!")

								choice =menu.display()

								gs = Board()					
								white_time = 600
								black_time = 600
					#check sound
						if gs.is_in_check(gs.whiteTurn):
							pygame.mixer.Sound.play(check_sound)
					#normal move sound
						else:
							pygame.mixer.Sound.play(move_sound)



					selected_piece = None
					start_pos = None
					valid_moves = []
				else:
					if row >= 0 and gs.board[row][col] != "--":
						piece_color = gs.board[row][col][0]
						if (piece_color == 'w' and gs.whiteTurn) or (piece_color == 'b' and not gs.whiteTurn):
							selected_piece = gs.board[row][col]
							start_pos = (row, col)
							piece_type = selected_piece[1]
							if piece_type == 'p':
								piece = Pawn(piece_color)
							elif piece_type == 'N':
								piece = Knight(piece_color)
							elif piece_type == 'B':
								piece = Bishop(piece_color)
							elif piece_type == 'R':
								piece = Rook(piece_color)
							elif piece_type == 'Q':
								piece = Queen(piece_color)
							elif piece_type == 'K':
								piece = King(piece_color)
							valid_moves = piece.get_valid_moves(start_pos, gs)


#check stalemate
		if not gs.is_in_check(gs.whiteTurn):

			temp = []

			for i in range(gs.dimension):
				for j in range(gs.dimension):
					valid_moves1	= []

					piece1 = gs.board[i][j]
					if piece1 == "--":
						continue

					
					if (piece1[0] == 'w' and  gs.whiteTurn) or (piece1[0] == 'b' and not gs.whiteTurn):
						piece_type1 = piece1[1]
						if piece_type1 == 'p':
							piece11 = Pawn(piece1[0])
						elif piece_type1 == 'N':
							piece11 = Knight(piece1[0])
						elif piece_type1 == 'B':
							piece11 = Bishop(piece1[0])
						elif piece_type1 == 'R':
							piece11 = Rook(piece1[0])
						elif piece_type1 == 'Q':
							piece11 = Queen(piece1[0])
						elif piece_type1 == 'K':
							piece11 = King(piece1[0])
					
						valid_moves1 = piece11.get_valid_moves((i,j), gs)



					for k in valid_moves1:

						if gs.is_valid_move((i,j),k):

							temp.append(1)
					if len(temp) != 0 :
						break
				if len(temp) != 0 :

					break




			if len(temp) == 0 :
				game_over_menu.display("Stalemate,it's a draw")

				choice =menu.display()
				gs = Board()
				white_time = 600
				black_time = 600
					
#check checkmate
		if gs.is_in_check(gs.whiteTurn):

			temp = []

			for i in range(gs.dimension):
				for j in range(gs.dimension):
					valid_moves1	= []

					piece1 = gs.board[i][j]
					if piece1 == "--":
						continue

					
					if (piece1[0] == 'w' and  gs.whiteTurn) or (piece1[0] == 'b' and not gs.whiteTurn):
						piece_type1 = piece1[1]
						if piece_type1 == 'p':
							piece11 = Pawn(piece1[0])
						elif piece_type1 == 'N':
							piece11 = Knight(piece1[0])
						elif piece_type1 == 'B':
							piece11 = Bishop(piece1[0])
						elif piece_type1 == 'R':
							piece11 = Rook(piece1[0])
						elif piece_type1 == 'Q':
							piece11 = Queen(piece1[0])
						elif piece_type1 == 'K':
							piece11 = King(piece1[0])
					
						valid_moves1 = piece11.get_valid_moves((i,j), gs)



					for k in valid_moves1:

						if gs.is_valid_move((i,j),k):

							temp.append(1)
					if len(temp) != 0 :
						break
				if len(temp) != 0 :

					
					break




			if len(temp) == 0 :

				pygame.mixer.Sound.play(end_sound)
				game_over_menu.display("Checkmate! White wins!" if not gs.whiteTurn else "Checkmate! Black wins!")

				choice =menu.display()

				gs = Board()					
				white_time = 600
				black_time = 600
				


		
		if valid_moves:
			gs.highlight_squares(screen, valid_moves, start_pos)
		gs.draw_pieces(screen)

		# Draw timers
		menu.draw_text(f"White: {int(white_time // 60)}:{int(white_time % 60):02d}", 32, gs.RED, 100, 20)
		menu.draw_text( f"Black: {int(black_time // 60)}:{int(black_time % 60):02d}", 32, gs.BLACK, 400, 20)

		pygame.display.flip()
	pygame.quit()

main()
