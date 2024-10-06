import chess
import chess.pgn
from stockfish import Stockfish
import image_processing_module
import cropper

class Piece():

    # The piece class captures the color of the piece and the type itself
    def __init__(self, piece_color=None, piece_type=None):
        self.piece_color = piece_color
        self.piece_type = piece_type

    # It is standard to use lower case for black pieces, and upper case for white pieces
    # Regardless of string representation, the colour is noted as a member variable
    def __str__(self):
        if self.piece_type == None:
            # Use '*' to differentiate from chess module representation
            return '*'
        if self.piece_color == 'b':
            return self.piece_type.lower()
        return self.piece_type.upper()

class Tile():

    # The Tile class has a given Piece object, a colour, and marks the tile if occupied
    def __init__(self, piece=None, tile_color=None, is_occupied=False):
        self.piece = piece or Piece()
        self.tile_color = tile_color
        self.is_occupied = is_occupied
    
    # If a Tile is printed, it only prints the Piece on it
    def __str__(self):
        return str(self.piece)


# While the Board object used in the Game class will change, none of the methods here directly change the Board state.
# This is to promote a differentiation of purpose between the Board class and the Game class.

class Board():

    def __init__(self):
        self.board = None
        self.initialise_board()
        self.place_pieces_default()
        # This grid tile map will allow O(1) access to a chess square, since I will be using a grid (a 2-D array)
        self.grid_tile_map = {}
        self.populate_gt_map()
    
    def get_tile_color(self, row_num, col_num):
        if row_num % 2:
            if col_num % 2:
                return 'w'
            return 'b'
        else:
            if col_num % 2:
                return 'b'
            return 'w'
    
    def initialise_board(self):
        # This will eventually become a list of lists (becoming a grid)
        self.board = []
        for row in range(8):
            # Does each row
            row_list = []
            for column in range(8):
                tile_color = self.get_tile_color(row, column)
                # The piece is initialised to be None, but when placing the first few pieces on the board this will change
                default_piece = Piece(None, None)
                row_list.append(Tile(default_piece, tile_color, False))
            self.board.append(row_list)

    # This populates the grid_tile_map mentioned above
    def populate_gt_map(self):
        curr_letter = 'a'
        for rows in range(8):
            for columns in range(8):
                curr_column = 8-columns
                # Uses a tuple to represent the co-ordinate, since lists aren't hashable
                self.grid_tile_map[(columns, rows)] = str(curr_letter) + str(curr_column)
            curr_letter = chr(ord(curr_letter) + 1)

    # Places on the first two ranks and last two ranks. Zero-indexed, so I use 0 and 7. 
    def place_not_pawn_helper(self, column, piece_type):
        self.board[0][column].piece = Piece('b', piece_type)
        self.board[7][column].piece = Piece('w', piece_type)
        self.board[0][column].is_occupied = True
        self.board[7][column].is_occupied = True
    
    def place_pieces_default(self):

        # Pawn placing
        for col in range(8):
            self.board[1][col].piece = Piece('b', 'p')
            self.board[6][col].piece = Piece('w', 'p')
            self.board[1][col].is_occupied = True
            self.board[6][col].is_occupied = True
        
        for col in range(8):
            # Rook
            if col == 0 or col == 7:
                self.place_not_pawn_helper(col, 'r')
            # Knight (n, k is king)
            elif col == 1 or col == 6:
                self.place_not_pawn_helper(col, 'n')
            # Bishop
            elif col == 2 or col == 5:
                self.place_not_pawn_helper(col, 'b')
            # Queen
            elif col == 3:
                self.place_not_pawn_helper(col, 'q')
            # King
            else:
                self.place_not_pawn_helper(col, 'k')

    def identify_square(self, position):
        return self.grid_tile_map[position]
    
    def __str__(self):
        board_str = ""
        for row in self.board:
            for tile in row:
                board_str += str(tile) + " "
            board_str += "\n"
        return board_str

    # This simplifies how I can access tile Information, especially in the Game class
    def __getitem__(self, position):
        row, col = position
        return self.board[row][col]

    # These methods leverage the __get__item method to make accessing relevant information easier
    def get_piece(self, position):
        return self.__getitem__(position).piece
    
    def tile_is_occupied(self, position):
        return self.__getitem__(position).is_occupied
    
    # If piece is captured, first clear the piece
    def clear_piece(self, position):
        self.__getitem__(position).piece = Piece(None, None)
        self.__getitem__(position).is_occupied = False

    # This is how I will place a piece in my grid
    def place_piece(self, piece, position):
        self.__getitem__(position).piece = piece
        self.__getitem__(position).is_occupied = True

    # Checks if a pawn can be promoted
    def pawn_is_promotable(self, position, turn):
        if (turn == "white"):
            if (position[0] == 1):
                return True
        else:
            if(position[0] == 6):
                return True
        return False

    def en_passant_possible(self, position_1, position_2, turn):

        row_pos_1, col_pos_1 = position_1
        row_pos_2, col_pos_2 = position_2
        
        # Checks if move was diagonal
        if (abs(row_pos_1 - row_pos_2) == 1 and abs(col_pos_1 - col_pos_2) == 1):
            # Checks if pawn moved to an empty square
            if (not self.tile_is_occupied(position_2)):
                # This assumes the player is playing chess correctly to focus on the detection
                return True
            
        return False
    
    def get_piece_color(self, position):
        return self.__getitem__(position=position).piece_color
    
    def to_piece_name_list(self):

        piece_name_list = []
        for row in self.board:
            row_list = []
            for tile in row:
                row_list.append(str(tile.piece))
            piece_name_list.append(row_list)
        return piece_name_list
    

# put this in different module?

class Game():

    def __init__(self, board = Board(), turn = 'white', move_num = 1, image_processing = image_processing_module.ImageProcessing()):

        self.board = board
        self.turn = turn
        self.move_num = move_num
        # Move_to_fen_map will map the move number to an FEN, a way to represent a specific chess state.
        # It will be especially useful to revisit specific moves. 
        self.move_to_fen_map = {}
        # Eval is the evaluation, which indicates who has the advantage. 
        # Calculating the eval will leverage the Stockfish API, a standard chess engine. 
        self.move_to_eval_map = {}
        # The chess module will ensure moves made are legal, and can be used to generate an FEN string.
        self.chess_module_board = chess.Board()
        self.chess_module_pgn = chess.pgn.Game()
        self.image_processing = image_processing
        self.stockfish = Stockfish()
        self.white_castled = False
        self.black_castled = False
        image_processing.read_file_names()
        self.underpromotions = False
        self.current_uci = ""
        # Deafult option is a queen
        self.pawn_promoted_to = "q"

    # After a turn, players switch.
    def switch_turn(self):

        if (self.turn == "white"):
            self.turn = "black"
        else:
            self.turn = "white"
    
    def detect_castle(self, uci_string):
        
        first_tile = uci_string[0:2]
        second_tile = uci_string[2:]
        
        rank_ft = ord(first_tile[0])
        rank_st = ord(second_tile[0])
        
        file_ft = int(first_tile[1])
        file_st = int(second_tile[1])

        return (abs(rank_ft-rank_st) == 2) and ((file_ft == file_st))

    def handle_castling(self, uci_string):

        if self.turn == "white" and not self.white_castled:
            if self.detect_castle(uci_string):
                self.white_castled = True
                if uci_string == "e1g1": 
                    # Move rook from h1 to f1
                    self.board.place_piece(Piece('w', 'r'), (7, 5))  
                    self.board.clear_piece((7, 7))
                elif uci_string == "e1c1":  
                    # Move rook from a1 to d1
                    self.board.place_piece(Piece('w', 'r'), (7, 3))  
                    self.board.clear_piece((7, 0))

        if self.turn == "black" and not self.black_castled:
            if self.detect_castle(uci_string):
                self.black_castled = True
                if uci_string == "e8g8": 
                    # Move rook from h8 to f8
                    self.board.place_piece(Piece('b', 'r'), (0, 5))  
                    self.board.clear_piece((0, 7))
                elif uci_string == "e8c8": 
                    # Move rook from a8 to d8
                    self.board.place_piece(Piece('b', 'r'), (0, 3))  
                    self.board.clear_piece((0, 0))

    def handle_en_passant(self, first_tuple, second_tuple):
        
        if (self.board.en_passant_possible(first_tuple, second_tuple, self.turn)):
            if (self.turn == "white"):
                pawn_to_be_cleared_row = second_tuple[0]+1
                pawn_to_be_cleared_column = second_tuple[1]
                self.board.clear_piece(pawn_to_be_cleared_row, pawn_to_be_cleared_column)
            else:
                pawn_to_be_cleared_row = second_tuple[0]-1
                pawn_to_be_cleared_column = second_tuple[1]
                self.board.clear_piece(pawn_to_be_cleared_row, pawn_to_be_cleared_column)

    # CCM - custom chess module, i.e. the classes I defined.
    def make_move_ccm(self, move_tuple, uci_string):

        first_tuple, second_tuple = self.detect_move_order(move_tuple, turn=self.turn)
        
        if self.board.get_piece(first_tuple).piece_type == 'k':
            self.handle_castling(uci_string)

        # Checks if pawn is on the right square for en_passant
        
        if self.board.get_piece(first_tuple).piece_type == 'p':
            self.handle_en_passant(first_tuple, second_tuple)

        # The piece is being captured
        if (self.board.__getitem__(second_tuple).is_occupied):
            self.board.clear_piece(second_tuple)
        
        piece_to_move = self.board.get_piece(first_tuple)

        if (piece_to_move.piece_type == "p" and self.board.pawn_is_promotable(first_tuple, self.turn)):
            piece_to_move.piece_type = self.pawn_promoted_to

        self.board.place_piece(piece_to_move, second_tuple)

        self.board.clear_piece(first_tuple)

        self.switch_turn()


    def make_move(self, has_castled, turn, img_values):
        
        board_array = self.board.to_piece_name_list()
        
        if (self.move_num == 1):
            move_tuple = self.image_processing.detect_first_move(board_array, img_values)
        else:
            move_tuple = self.image_processing.detect_move(has_castled, turn, board_array, img_values)

        # Verifies which is the right move, which is needed for Python chess module
        uci_string = self.detect_uci(move_tuple)
        self.current_uci = uci_string
        # En passant, promotion checks here
        self.chess_module_board.push_uci(uci_string)
                
        # Updates my custom chess board
        self.make_move_ccm(move_tuple, uci_string)

        # Maps move_num to FEN. 
        fen = self.chess_module_board.fen()
        self.move_to_fen_map[self.move_num] = fen

        # Map move_num to eval - this is expensive, commenting out for now
        self.move_to_eval_map[self.move_num] = self.get_eval(fen)

        # Increment the move number
        self.move_num += 1
        
        return self.chess_module_board

    
    def get_uci_move_string(self, position_1, position_2):

        if (self.board.get_piece(position_1).piece_type == 'p'):
                
            if (self.board.pawn_is_promotable(position_1, self.turn)):
                if (self.underpromotions):
                    self.pawn_promoted_to = input("A pawn was underpromoted. What piece was it promoted to? Piece (n/b/r): ").lower()
                return self.board.identify_square(position_1) + self.board.identify_square(position_2) + self.pawn_promoted_to

        return self.board.identify_square(position_1) + self.board.identify_square(position_2)
    
    # Eval is short for 'evaluation', or a measure of who is winning. 
    # It is measured in centipawns - an advantage of +100 indicates white is winning by 1 pawn, and -100 means black is winning by 1 pawn.
    # Chess players assign the following weightages to pieces:
    # Pawn - 100 centipawns
    # Knight/Bishop - 300 centipawns
    # Rook - 500 centipawns
    # Queen - 900 centipawns

    def get_eval(self, fen):
        
        self.stockfish.set_fen_position(fen)
        return self.stockfish.get_evaluation()

    def detect_move_squares(self, move_tuple):
        
        first_tile = move_tuple[0]
        second_tile = move_tuple[1]
        
        first_tile_square = self.board.identify_square(first_tile)
        second_tile_square = self.board.identify_square(second_tile)

        return first_tile_square, second_tile_square

    def detect_move_order(self, move_tuple, turn):
        
        first_tile_tuple = move_tuple[0]
        second_tile_tuple = move_tuple[1]

        if (self.board.__getitem__(first_tile_tuple).is_occupied and self.board.__getitem__(second_tile_tuple).is_occupied):
            return self.detect_move_order_capture(first_tile_tuple, second_tile_tuple, turn)

        if (self.board.__getitem__(first_tile_tuple).is_occupied):
            return (first_tile_tuple, second_tile_tuple)
        
        else:
            return (second_tile_tuple, first_tile_tuple)
    
    def detect_move_order_capture(self, first_tile_tuple, second_tile_tuple, turn):
       
       if (self.board.get_piece_color(first_tile_tuple) == turn):
           return (first_tile_tuple, second_tile_tuple)
       else:
           return (second_tile_tuple, first_tile_tuple)

    def detect_uci(self, move_tuple):

        move_order_tuple = self.detect_move_order(move_tuple, turn = self.turn)
        
        # First tuple is the first move, second is second move
        first_tuple = move_order_tuple[0]
        second_tuple = move_order_tuple[1]

        return self.get_uci_move_string(first_tuple, second_tuple)
    
    def get_turn(self):
        return self.turn

class Play():

    def __init__(self, game = None):
        self.game = Game()
        self.cropper = cropper.Cropper()
        self.final_points = self.cropper.run_cropper()
        self.check_underpromotions()
    
    def check_underpromotions(self):
        underpromotions = input("Was any piece underpromoted in the game? Y/N: ")
        if (underpromotions.lower() == "y"):
            self.game.underpromotions = True
        else:
            self.game.underpromotions = False
    
    def play_game(self):
        
        self.game.make_move(has_castled = False, turn = "white", img_values=self.final_points)
        node = self.game.chess_module_pgn.add_variation(chess.Move.from_uci(self.game.current_uci))
        
        print(self.game.board)
        
        for _ in range(1, len(self.game.image_processing.file_names)-1):

            if (self.game.get_turn() == "white"):
                if (not self.game.white_castled):
                    self.game.make_move(has_castled=False, turn="white", img_values=self.final_points)
                
                else:
                    self.game.make_move(has_castled=True, turn="white", img_values=self.final_points)
                
            else:
                if (not self.game.black_castled):
                    self.game.make_move(has_castled=False, turn="black", img_values=self.final_points)
                   
                else:
                    self.game.make_move(has_castled=True, turn="black", img_values=self.final_points)
                
            print(self.game.board)
            node = node.add_variation(chess.Move.from_uci(self.game.current_uci))
        
        print(self.game.chess_module_pgn)

play = Play()
play.play_game()
