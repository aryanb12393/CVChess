# CVChess

CVChess is a tool designed for chess enthusiasts who want to analyze their over-the-board games, without the manual effort of transcribing their moves. By leveraging computer vision techniques, CVChess automates the process of recording chess games, making it easier to learn from mistakes and improve as a player.

## Table of Contents
* Description
* Usage
* Future Plans
* License
* Acknowledgements

## Description
As a chess enthusiast, analyzing my games has been crucial for my improvement. While online platforms like chess.com make this easy with PGN and evaluation tools, over-the-board games require manual transcription, which is tedious. CVChess automates this process by using images of the chessboard to generate a PGN of the game.

### How It Works

* **Image Capture**: The program captures images of the chessboard at each move.
* **Position Detection**: Using OpenCV's absdiff method, it calculates the difference between two consecutive board positions and maps these changes to an 8x8 grid.
* **Move Identification**: The highest brightness values in the difference map indicate where a piece has moved, from and to.
* **PGN Generation**: The program leverages Python libraries like chess for move validation and chess.pgn for generating PGNs, creating a digital record of the game.

## Usage

### Requirements
To use CVChess, you will need to install the following libraries:
* `chess`
* `chess.pgn`
* `Stockfish` (for generating evaluations)

### Setup
1. **Camera Setup**: Set up a camera directly above the chessboard. A tripod with a Bluetooth trigger (e.g., an iPhone on a tripod) is recommended for capturing images at each move, to ensure consistent angles.
2. **Image Cropping**: The values for how the image is cropped are currently hard-coded. You will need to crop the images into an 8x8 grid manually using the code commented out in the `ImageProcessing.py` module.
3. **Image Path**: Add the path where the images are stored. Ensure these photos are in JPEG format or compatible with OpenCV.
4. **Pawn Promotion**: The program assumes any pawn promotion is to a queen by default. If you underpromote, you can input the correct piece via the command line during PGN generation.

## Future Plans
I have two primary goals for future development:
1. **Chess Clock Module**: Implement a chess clock using Tkinter. This will not only be useful for rapid chess but also enable frame extraction from a video based on timestamps, eliminating the need to take photos after every move.
2. **GUI for Image Cropping**: Develop a GUI (also using Tkinter) to make the image cropping process more user-friendly. This will give users greater control over the analysis area and streamline the setup process. (Oct 2024: Completed)

## License
This project is licensed under the MIT License. See the LICENSE file for more details.

## Acknowledgements
I would like to thank Aayush Dutta and Aryan Sahai for consistently hard-fought chess games, and for their continued support and feedback on this project. A special thanks to Vivaan Khabya for his help in manually creating the PGNs from our games; CVChess is here to make that task easier for all of us.
