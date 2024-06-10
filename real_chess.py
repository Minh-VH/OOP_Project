import pygame

class Board:
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
                        j * self.square_side, i * self.square_side, self.square_side, self.square_side))

    def draw_chess_board(self, screen):
        for i in range(self.dimension):
            for j in range(self.dimension):
                color = self.LIGHT_BLUE if (i + j) % 2 == 1 else self.WHITE
                pygame.draw.rect(screen, color, (j * self.square_side, i * self.square_side, self.square_side, self.square_side))

    def highlight_squares(self, screen, valid_moves, start_pos):
        for move in valid_moves:
            if self.is_valid_move(start_pos, move):
                pygame.draw.rect(screen, self.YELLOW, (move[1] * self.square_side, move[0] * self.square_side, self.square_side, self.square_side))

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
                # Make the move
                self.make_temporary_move(start_pos, end_pos)
                # Check if the move leaves the player in check
                if not self.is_in_check(self.whiteTurn):
                    # Revert the temporary move
                    self.revert_temporary_move(start_pos, end_pos, piece_str)
                    return True
                # Revert the temporary move
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

    def is_checkmate(self, white_turn):
        if not self.is_in_check(white_turn):
            return False
        for row in range(self.dimension):
            for col in range(self.dimension):
                piece_str = self.board[row][col]
                if piece_str != "--" and piece_str[0] == ("w" if white_turn else "b"):
                    piece = self.piece_from_string(piece_str)
                    if piece:
                        valid_moves = piece.get_valid_moves((row, col), self)
                        for move in valid_moves:
                            self.make_temporary_move((row, col), move)
                            if not self.is_in_check(white_turn):
                                self.revert_temporary_move((row, col), move, piece_str)
                                return False
                            self.revert_temporary_move((row, col), move, piece_str)
        return True

    def is_stalemate(self, white_turn):
        if self.is_in_check(white_turn):
            return False
        for row in range(self.dimension):
            for col in range(self.dimension):
                piece_str = self.board[row][col]
                if piece_str != "--" and piece_str[0] == ("w" if white_turn else "b"):
                    piece = self.piece_from_string(piece_str)
                    if piece:
                        valid_moves = piece.get_valid_moves((row, col), self)
                        for move in valid_moves:
                            self.make_temporary_move((row, col), move)
                            if not self.is_in_check(white_turn):
                                self.revert_temporary_move((row, col), move, piece_str)
                                return False
                            self.revert_temporary_move((row, col), move, piece_str)
        return True

class Piece:
    def __init__(self, color):
        self.color = color
        self.moves = []

    def get_valid_moves(self, position, board):
        raise NotImplementedError

class Pawn(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.en_passant = False
        self.promotion = False

    def get_valid_moves(self, position, board):
        self.moves = []
        row, col = position
        piece = board.board[row][col]
        direction = -1 if piece == "wp" else 1
        start_row = 6 if piece == "wp" else 1

        # Single move forward
        if board.board[row + direction][col] == "--":
            self.moves.append((row + direction, col))
            # Double move forward
            if row == start_row and board.board[row + 2 * direction][col] == "--":
                self.moves.append((row + 2 * direction, col))

        # Capture moves
        if col - 1 >= 0 and board.board[row + direction][col - 1] != "--" and board.board[row + direction][col - 1][0] != piece[0]:
            self.moves.append((row + direction, col - 1))
        if col + 1 < board.dimension and board.board[row + direction][col + 1] != "--" and board.board[row + direction][col + 1][0] != piece[0]:
            self.moves.append((row + direction, col + 1))

        # En passant capture
        if board.en_passant_target and row + direction == board.en_passant_target[0] and abs(col - board.en_passant_target[1]) == 1:
            self.moves.append(board.en_passant_target)

        return self.moves

    def move(self, start_pos, end_pos, board):
        piece = board.board[start_pos[0]][start_pos[1]]
        # Handle en passant capture
        if abs(end_pos[0] - start_pos[0]) == 1 and abs(end_pos[1] - start_pos[1]) == 1 and board.board[end_pos[0]][end_pos[1]] == "--":
            if board.whiteTurn:
                board.board[end_pos[0] + 1][end_pos[1]] = "--"
            else:
                board.board[end_pos[0] - 1][end_pos[1]] = "--"
        board.board[start_pos[0]][start_pos[1]] = "--"
        board.board[end_pos[0]][end_pos[1]] = piece
        # Update en_passant_target
        if abs(end_pos[0] - start_pos[0]) == 2:
            board.en_passant_target = ((end_pos[0] + start_pos[0]) // 2, end_pos[1])
        else:
            board.en_passant_target = None
        # Handle promotion
        if end_pos[0] == 0 or end_pos[0] == 7:
            self.promote_pawn(end_pos, board)

    def promote_pawn(self, pos, board):
        while True:
            promotion_choice = input("Promote pawn to (Q, R, B, K): ").upper()
            if promotion_choice in ['Q', 'R', 'B', 'K']:
                board.board[pos[0]][pos[1]] = board.board[pos[0]][pos[1]][0] + promotion_choice
                board.load_image()  # Reload images to ensure the new piece is drawn correctly
                break
            else:
                print("Invalid choice. Please choose Q, R, B, or K.")

class Knight(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.potential_moves = [
            (2, 1), (2, -1), (-2, 1), (-2, -1),
            (1, 2), (1, -2), (-1, 2), (-1, -2)
        ]

    def get_valid_moves(self, position, board):
        self.moves = []
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
    def __init__(self, color):
        super().__init__(color)
        self.directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

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

class Rook(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

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

class Queen(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

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

class King(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.potential_moves = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]

    def get_valid_moves(self, position, board):
        self.moves = []
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

def main():
    play = True
    selected_piece = None
    start_pos = None
    valid_moves = []

    pygame.init()
    screen = pygame.display.set_mode((512, 512))
    gs = Board()

    while play:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                play = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                col = pos[0] // gs.square_side
                row = pos[1] // gs.square_side

                if selected_piece:
                    end_pos = (row, col)
                    if gs.is_valid_move(start_pos, end_pos):
                        gs.move_piece(start_pos, end_pos)
                        if gs.is_in_check(not gs.whiteTurn):
                            if gs.is_checkmate(not gs.whiteTurn):
                                print("Checkmate! White wins!" if gs.whiteTurn else "Checkmate! Black wins!")
                                play = False
                            elif gs.is_stalemate(not gs.whiteTurn):
                                print("Stalemate! It's a draw!")
                                play = False
                    selected_piece = None
                    start_pos = None
                    valid_moves = []
                else:
                    if gs.board[row][col] != "--":
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

        gs.draw_chess_board(screen)
        if valid_moves:
            gs.highlight_squares(screen, valid_moves, start_pos)
        gs.draw_pieces(screen)
        pygame.display.flip()
    pygame.quit()

main()
