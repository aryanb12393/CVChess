import cv2

points = []
final_points = []

def select_points(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        if len(points) < 4:
            points.append((x, y))
            cv2.circle(image_copy, (x, y), 5, (0, 0, 255), -1)
            cv2.imshow("Image", image_copy)

image_path = "IMG_0726.jpg"
image = cv2.imread(image_path)

if image is None:
    print(f"Error: Could not load image at {image_path}")
    exit()

while True:

    image_copy = image.copy()

    points = []

    cv2.namedWindow("Image")
    cv2.setMouseCallback("Image", select_points)

    while len(points) < 4:
        cv2.imshow("Image", image_copy)
        key = cv2.waitKey(1) & 0xFF

    x_coords = [p[0] for p in points]
    y_coords = [p[1] for p in points]

    # left x, right x
    x_min = min(x_coords)
    x_max = max(x_coords)
    
    # top y, bottom y
    y_min = min(y_coords)
    y_max = max(y_coords)

    cropped_image = image[y_min:y_max, x_min:x_max]

    cv2.imshow("Cropped Image", cropped_image)
    cv2.waitKey(1)

    reset = input("Are you happy with the crop? (enter y/n): ").strip().lower()

    if reset == "y":
        print("Exiting...")
        final_points.append(x_min)
        final_points.append(x_max)
        final_points.append(y_min)
        final_points.append(y_max)
        break
    elif reset == "n":
        cv2.destroyWindow("Cropped Image")
        print("Restarting selection...")
        continue
    else:
        print("Invalid input. Please crop again.")
        cv2.destroyWindow("Cropped Image")
        continue

cv2.destroyAllWindows()
print(final_points)