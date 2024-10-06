import cv2
import numpy as np
from collections import deque
import os
from pathlib import Path

# This is the ImageProcessing Class. 
# It will handle the processing between two consecutive pictures, highlighting the difference (the move)

class ImageProcessing:
    
    def __init__(self, images_deque=deque(maxlen=2), file_names = list()):
        
        # I used a deque to store the image. 
        # Since I need to compare consecutive images, it made sense to pop from the left once I'm done with an image, and append to the right and keep repeating this.
        self.images_deque = images_deque
        # This file_names list will help with opening the images quickly
        self.file_names = file_names
        # This picture_number will be used for indexing with the file_names list
        self.picture_number = 0
        # Like the Board class, I needed a grid_tile map for handling castling. I will refactor this code and pass in the Board state to the program, however.
        self.grid_tile_map = {}
        self.populate_gt_map()


    def crop_image(self, image, values):

        return image[values[2]:values[3], values[0]:values[1]]
    
    # The cropped image will be preprocessed here to make the computation easier for the computer. 
    def pre_process_image(self, cropped_image):
        # First, the image is converted into black and white
        grey_image = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY)
        # This method uses histogram equalization to get a better contrast.  
        enhanced_image = self.enhance_contrast(grey_image)
        # Image is also blurred
        blurred_image = cv2.GaussianBlur(enhanced_image, (15,15), 0)
        return blurred_image
    
    # Same method as board class. 
    def populate_gt_map(self):
        curr_letter = 'a'
        for rows in range(8):
            for columns in range(8):
                curr_column = 8-columns
                # Uses a tuple to represent the co-ordinate, since lists aren't hashable
                self.grid_tile_map[(columns, rows)] = str(curr_letter) + str(curr_column)
            curr_letter = chr(ord(curr_letter) + 1)

    # The histogram equalisation from above is done here. 
    def enhance_contrast(self, grey_image):
        # This specifically uses a CLAHE histogram equalisation, which worked much better for me than using a binary threshold
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced_image = clahe.apply(grey_image)
        return enhanced_image

    # This method finds the highest brightness values, which indicate a turn has likely been made in these squares. 
    # I also pass in has_castled and turn here. This will be used to check for castling. 
    def find_max_brightness_values(self, abs_diff, has_castled, turn, board_array):
        
        # for debugging
        cv2.imshow("abs_diff", abs_diff)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
        # The image is going to be divided into an 8 x 8 board.
        grid_size = 8
        height, width = abs_diff.shape
        cell_height = height // grid_size
        cell_width = width // grid_size

        # A list will be used to compute the brightness so I can sort it at the end. 
        brightness_list = []
        
        # Iterates through each cell in the picture
        for row in range(grid_size):
            for col in range(grid_size):
                # This is calculating each square area. 
                y1 = row * cell_height
                y2 = (row + 1) * cell_height
                x1 = col * cell_width
                x2 = (col + 1) * cell_width
                # Uses NumPy to find the sum of pixel values in each square (which corresponds to each tile)
                cell_brightness = np.sum(abs_diff[y1:y2, x1:x2])
                # Adds it to the list as a tuple, also noting the row and the column (0-indexed, like my grid)
                brightness_list.append((cell_brightness, (row, col)))

        # Sorts the list from largest to smallest brightness values
        sorted_brightness_list = sorted(brightness_list, reverse=True)
        
        # Stored as tuple of tuples.
        first_max_position = sorted_brightness_list[0][1]
        second_max_position = sorted_brightness_list[1][1]
        
        # I take these two positions as there is a possibility the rooks brightness is brighter than the kings, or in en passant cases.
        third_max_position = sorted_brightness_list[2][1]

        if (not has_castled):
            return (first_max_position, second_max_position)
        
        fourth_max_position = sorted_brightness_list[3][1]
        # If the player whose turn it is hasn't castled, the top two squares are returned
        # This will detect if the image sees a castle. I will refactor this in my Game class to simplify the logic. 
        self.image_detects_castle([first_max_position, second_max_position, third_max_position, fourth_max_position], turn)
        return (first_max_position, second_max_position)
    
    def image_detect_en_passant(self, max_position_list, board_array):
        
        mp_idx_dict = {}

        for i in range(len(max_position_list)):
            # I find the algebraic tile
            algebraic_tile = self.grid_tile_map[max_position_list[i]]
            # Map the algebraic tile to the index. 
            mp_idx_dict[algebraic_tile] = i


    def image_detects_castle(self, max_position_list, turn):
        
        # Max_position (mp) to index dictionary. 
        mp_idx_dict = {}

        # Iterates through the 4 positions provided. 
        for i in range(len(max_position_list)):
            # I find the algebraic tile
            algebraic_tile = self.grid_tile_map[max_position_list[i]]
            # Map the algebraic tile to the index. 
            mp_idx_dict[algebraic_tile] = i

        # If the turn is white, I want to check for the first rank (1)
        if (turn == "white"):
            if "c1" in mp_idx_dict:
                return (max_position_list[mp_idx_dict["c1"]], max_position_list[mp_idx_dict["e1"]])
            else:
                return (max_position_list[mp_idx_dict["g1"]], max_position_list[mp_idx_dict["e1"]])
        
        # Otherwise, I'll check for the last rank (8)
        else:
            if "c8" in mp_idx_dict:
                return (max_position_list[mp_idx_dict["c8"]], max_position_list[mp_idx_dict["e8"]])
            else:
                return (max_position_list[mp_idx_dict["g8"]], max_position_list[mp_idx_dict["e8"]])
        
        #print(mp_idx_dict)

    # detect_first_move is an independent method since I haven't added to my deque yet. 
    def detect_first_move(self, board_array, values):
        
        # reads the initial image
        image_initial = cv2.imread(self.file_names[self.picture_number])
    
        self.picture_number += 1

        # reads the next image
        image_next = cv2.imread(self.file_names[self.picture_number])
        self.picture_number += 1    

        cropped_initial = self.crop_image(image_initial, values)
        cropped_next = self.crop_image(image_next, values)

        blurred_initial = self.pre_process_image(cropped_initial)
        blurred_next = self.pre_process_image(cropped_next)

        self.images_deque.append(blurred_next)

        abs_diff = cv2.absdiff(blurred_next, blurred_initial)

        first_max_position, second_max_position = self.find_max_brightness_values(abs_diff, has_castled=False, turn="white", board_array = board_array)
        return first_max_position, second_max_position

    def detect_move(self, has_castled, turn, board_array, values):

        prev_image = self.images_deque.popleft()

        curr_image = cv2.imread(self.file_names[self.picture_number])
        self.picture_number += 1

        cropped_curr = self.crop_image(curr_image, values)
        blurred_curr = self.pre_process_image(cropped_curr)
    
        self.images_deque.append(blurred_curr)

        abs_diff = cv2.absdiff(prev_image, blurred_curr)
    
        first_max_position, second_max_position = self.find_max_brightness_values(abs_diff, has_castled, turn, board_array)
        return first_max_position, second_max_position
    
    def read_file_names(self):
        # Put the images of the chessboard in "pics"
        directory = "pics"
        # This assumes the images can be sorted by their name, which indicates when they were created.
        files = sorted(os.listdir(directory))
        directory = Path("pics")

        for file in files:
            # ".DS_Store" file is created, and I don't want to read that in my image processing.
            if not file.startswith('.'):
                self.file_names.append(directory/file)

