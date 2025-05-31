import cv2
import numpy as np

# Step 1: Load the image
image = cv2.imread("screenshot.png")

# Step 2: Convert to HSV color space for better color segmentation
hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

# Step 3: Define HSV range for yellow color (adjust based on your image)
lower_yellow = np.array([20, 100, 100])  # Lower bound for yellow
upper_yellow = np.array([40, 255, 255])  # Upper bound for yellow

# Step 4: Create a binary mask for yellow regions
yellow_mask = cv2.inRange(hsv_image, lower_yellow, upper_yellow)

# Optional: Clean up the mask (remove noise and fill gaps)
kernel = np.ones((1, 1), np.uint8)
yellow_mask = cv2.morphologyEx(yellow_mask, cv2.MORPH_OPEN, kernel)  # Remove small noise
yellow_mask = cv2.morphologyEx(yellow_mask, cv2.MORPH_CLOSE, kernel)  # Fill small gaps

# Step 5: Find contours in the yellow mask
contours, _ = cv2.findContours(yellow_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Step 6: Iterate through contours to find the star shape
star_contour = None
for contour in contours:
    # Approximate the contour to a polygon
    epsilon = 0.03 * cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, epsilon, True)

    # A star typically has 10 vertices (adjust based on your icon)
    if len(approx) == 10:
        star_contour = contour
        break

# Step 7: Draw the detected star contour or bounding box
if star_contour is not None:
    # Option 1: Draw the contour
    cv2.drawContours(image, [star_contour], -1, (0, 255, 0), 2)

    # Option 2: Draw a bounding box around the star
    x, y, w, h = cv2.boundingRect(star_contour)
    cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

    print("Star icon detected!")
else:
    print("Star icon not found.")

# Step 8: Display the results
cv2.imshow("Original Image", image)
cv2.imshow("Yellow Mask", yellow_mask)
cv2.waitKey(0)
cv2.destroyAllWindows()