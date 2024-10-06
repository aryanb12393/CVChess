import cv2

class Cropper:
    
    # hard coded for now, consider changing.
    def __init__(self, image_path="pics/IMG_0744.jpg"):
        self.image_path = image_path
        self.points = []
        self.final_points = []
        self.image = cv2.imread(self.image_path)
        
        if self.image is None:
            raise FileNotFoundError(f"Error: Could not load image at {self.image_path}")
        
        self.image_copy = self.image.copy()

    def select_points(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN and len(self.points) < 4:
            self.points.append((x, y))
            cv2.circle(self.image_copy, (x, y), 10, (0, 0, 255), -1)
            cv2.imshow("Image", self.image_copy)

    def run_cropper(self):
        while True:
            self.image_copy = self.image.copy()
            self.points = []

            cv2.namedWindow("Image")
            cv2.setMouseCallback("Image", self.select_points)

            while len(self.points) < 4:
                cv2.imshow("Image", self.image_copy)
                key = cv2.waitKey(1) & 0xFF

            x_coords = [p[0] for p in self.points]
            y_coords = [p[1] for p in self.points]

            x_min = min(x_coords)
            x_max = max(x_coords)
            y_min = min(y_coords)
            y_max = max(y_coords)

            cropped_image = self.image[y_min:y_max, x_min:x_max]

            cv2.imshow("Cropped Image", cropped_image)
            cv2.waitKey(1)

            reset = input("Are you happy with the crop? (enter y/n): ").strip().lower()

            if reset == "y":
                self.final_points = [x_min, x_max, y_min, y_max]
                break
            elif reset == "n":
                cv2.destroyWindow("Cropped Image")
                continue
            else:
                cv2.destroyWindow("Cropped Image")
                continue

        cv2.destroyAllWindows()
        return self.final_points