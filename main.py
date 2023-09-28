from copy import deepcopy
import pygame


breadth, length = 750,750
ROWS, COLS = 8,8
block_size = breadth//COLS

# rgb
RED_PIECE = (189,146,104)
GREY_PIECE = (112,128,144)
BLACK_BORDER = (0, 0, 0)
CYAN_MOVE = (153, 204,255)

crown_image = pygame.transform.scale(pygame.image.load('crown.png'), (40, 20))


def algo_prune_alphabeta(position, alpha, beta, depth, max_player, game):
    if depth == 0 or position.is_winner() != None:
        return position.evaluation_function(), position
    
    if max_player:
        maxEval = float('-inf')
        best_move = None
        for move in all_moves(position, GREY_PIECE, game):
            evaluation = algo_prune_alphabeta(move,alpha, beta, depth-1, False, game)[0]

            if evaluation > maxEval:
                maxEval = evaluation
                best_move = move
            alpha = max(alpha, maxEval)
            if alpha >= beta:
                break
                
        
        return maxEval, best_move
    else:
        minEval = float('inf')
        best_move = None
        for move in all_moves(position, RED_PIECE, game):
            evaluation = algo_prune_alphabeta(move, alpha, beta, depth-1, True, game)[0]
            
            if evaluation < minEval:
                minEval = evaluation
                best_move = move
            beta = min(beta, minEval)
            if(beta <= alpha):
                break
        
        return minEval, best_move


def check_move(piece, move, board, game, skip):
    board.move(piece, move[0], move[1])
    if skip:
        board.remove_piece(skip)

    return board


def all_moves(board, color, game):
    moves = []

    for piece in board.give_pieces(color):
        valid_moves = board.validity_move(piece)
        for move, skip in valid_moves.items():
            temp_board = deepcopy(board)
            temp_piece = temp_board.get_piece(piece.row, piece.col)
            new_board = check_move(temp_piece, move, temp_board, game, skip)
            moves.append(new_board)
    
    return moves




class Piece:
    PADDING = 11
    OUTLINE = 6

    def __init__(self, row, col, color):
        self.row = row
        self.col = col
        self.color = color
        self.king = False
        self.x = 0
        self.y = 0
        self.get_pos()

    def get_pos(self):
        self.x = block_size * self.col + block_size // 2
        self.y = block_size * self.row + block_size // 2

    def is_king(self):
        self.king = True
    
    def draw(self, win):
        radius = block_size//2 - self.PADDING
        pygame.draw.circle(win, BLACK_BORDER, (self.x, self.y), radius + self.OUTLINE)
        pygame.draw.circle(win, self.color, (self.x, self.y), radius)
        if self.king:
            win.blit(crown_image, (self.x - crown_image.get_width() // 2, self.y - crown_image.get_height() // 2))

    def move(self, row, col):
        self.row = row
        self.col = col
        self.get_pos()

    def __repr__(self):
        return str(self.color)







class Game:
    def __init__(self, win):
        self._init()
        self.win = win
    
    def update(self):
        self.board.draw(self.win)
        self.draw_valid_moves(self.valid_moves)
        pygame.display.update()

    def _init(self):
        self.selected = None
        self.board = Board()
        self.turn = RED_PIECE
        self.valid_moves = {}

    def is_winner(self):
        return self.board.is_winner()

    def reset(self):
        self._init()

    def select(self, row, col):
        if self.selected:
            result = self._move(row, col)
            if not result:
                self.selected = None
                self.select(row, col)
        
        piece = self.board.get_piece(row, col)
        if piece != 0 and piece.color == self.turn:
            self.selected = piece
            self.valid_moves = self.board.validity_move(piece)
            return True
            
        return False

    def _move(self, row, col):
        piece = self.board.get_piece(row, col)
        if self.selected and piece == 0 and (row, col) in self.valid_moves:
            self.board.move(self.selected, row, col)
            skipped = self.valid_moves[(row, col)]
            if skipped:
                self.board.remove_piece(skipped)
            self.changing_chances()
        else:
            return False

        return True

    def draw_valid_moves(self, moves):
        for move in moves:
            row, col = move
            pygame.draw.circle(self.win, CYAN_MOVE, (col * block_size + block_size//2, row * block_size + block_size//2), 15)

    def changing_chances(self):
        self.valid_moves = {}
        if self.turn == RED_PIECE:
            self.turn = GREY_PIECE
        else:
            self.turn = RED_PIECE

    def fetch_board(self):
        return self.board

    def changing_move(self, board):
        self.board = board
        self.changing_chances()











class Board:
    def __init__(self):
        self.board = []
        self.RED_PIECE_left = self.GREY_PIECE_left = 12
        self.RED_PIECE_kings = self.GREY_PIECE_kings = 0
        self.create_board()
    
    def make_square(self, win):
        win.fill((240,230,140))
        for row in range(ROWS):
            for col in range(row % 2, COLS, 2):
                pygame.draw.rect(win, (107,142,35), (row*block_size, col *block_size, block_size, block_size))

    def evaluation_function(self):
        return self.GREY_PIECE_left - self.RED_PIECE_left + (self.GREY_PIECE_kings * 0.5 - self.RED_PIECE_kings * 0.5)

    def give_pieces(self, color):
        pieces = []
        for row in self.board:
            for piece in row:
                if piece != 0 and piece.color == color:
                    pieces.append(piece)
        return pieces

    def move(self, piece, row, col):
        self.board[piece.row][piece.col], self.board[row][col] = self.board[row][col], self.board[piece.row][piece.col]
        piece.move(row, col)

        if row == ROWS - 1 or row == 0:
            piece.is_king()
            if piece.color == GREY_PIECE:
                self.GREY_PIECE_kings += 1
            else:
                self.RED_PIECE_kings += 1 

    def get_piece(self, row, col):
        return self.board[row][col]

    def create_board(self):
        for row in range(ROWS):
            self.board.append([])
            for col in range(COLS):
                if col % 2 == ((row +  1) % 2):
                    if row < 3:
                        self.board[row].append(Piece(row, col, GREY_PIECE))
                    elif row > 4:
                        self.board[row].append(Piece(row, col, RED_PIECE))
                    else:
                        self.board[row].append(0)
                else:
                    self.board[row].append(0)
        
    def draw(self, win):
        self.make_square(win)
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece != 0:
                    piece.draw(win)

    def remove_piece(self, pieces):
        for piece in pieces:
            self.board[piece.row][piece.col] = 0
            # if piece!=0:
            if piece.color == RED_PIECE:
                self.RED_PIECE_left -= 1
            else:
                self.GREY_PIECE_left -= 1
    
    def is_winner(self):
        if self.RED_PIECE_left <= 0:
            return GREY_PIECE
        elif self.GREY_PIECE_left <= 0:
            return RED_PIECE
        
        return None 
    
    def validity_move(self, piece):
        moves = {}
        left = piece.col - 1
        right = piece.col + 1
        row = piece.row

        if piece.color == RED_PIECE or piece.king:
            moves.update(self.go_left(row -1, max(row-3, -1), -1, piece.color, left))
            moves.update(self.go_right(row -1, max(row-3, -1), -1, piece.color, right))
        if piece.color == GREY_PIECE or piece.king:
            moves.update(self.go_left(row +1, min(row+3, ROWS), 1, piece.color, left))
            moves.update(self.go_right(row +1, min(row+3, ROWS), 1, piece.color, right))
    
        return moves

    def go_left(self, start, stop, step, color, left, skipped=[]):
        moves = {}
        last = []
        for r in range(start, stop, step):
            if left < 0:
                break
            
            current = self.board[r][left]
            if current == 0:
                if skipped and not last:
                    break
                elif skipped:
                    moves[(r, left)] = last + skipped
                else:
                    moves[(r, left)] = last
                
                if last:
                    if step == -1:
                        row = max(r-3, 0)
                    else:
                        row = min(r+3, ROWS)
                    moves.update(self.go_left(r+step, row, step, color, left-1,skipped=last))
                    moves.update(self.go_right(r+step, row, step, color, left+1,skipped=last))
                break
            elif current.color == color:
                break
            else:
                last = [current]

            left -= 1
        
        return moves

    def go_right(self, start, stop, step, color, right, skipped=[]):
        moves = {}
        last = []
        for r in range(start, stop, step):
            if right >= COLS:
                break
            
            current = self.board[r][right]
            if current == 0:
                if skipped and not last:
                    break
                elif skipped:
                    moves[(r,right)] = last + skipped
                else:
                    moves[(r, right)] = last
                
                if last:
                    if step == -1:
                        row = max(r-3, 0)
                    else:
                        row = min(r+3, ROWS)
                    moves.update(self.go_left(r+step, row, step, color, right-1,skipped=last))
                    moves.update(self.go_right(r+step, row, step, color, right+1,skipped=last))
                break
            elif current.color == color:
                break
            else:
                last = [current]

            right += 1
        
        return moves

frames_per_second = 60

WIN = pygame.display.set_mode((breadth, length))
pygame.display.set_caption('Welcome to my game of Checkers(AI vs Human) CS235')

def get_pos_from_mouse(pos):
    x, y = pos
    row = y // block_size
    col = x // block_size
    return row, col

def main():
    
    run = True
    clock = pygame.time.Clock()
    game = Game(WIN)

    while run:
        clock.tick(frames_per_second)
        
        if game.turn == GREY_PIECE:
            value, new_board = algo_prune_alphabeta(game.fetch_board(),float('-inf'),float('inf'),1 , GREY_PIECE, game)
            game.changing_move(new_board)

        if game.is_winner() != None:
            if game.is_winner()==RED_PIECE:
                print("YOU WON")
            else:
                print("YOU LOST")
            run = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
             run = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                row, col = get_pos_from_mouse(pos)
                game.select(row, col)

        game.update()
    
    pygame.quit()

main()