import cv2
import numpy as np
from pathlib import Path

def detect_dice(image_path):
    # Read the image
    image = cv2.imread(image_path)
    
    # Convert to HSV for better color segmentation
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # Define color ranges for each die
    # These ranges will need adjustment based on your lighting conditions
    color_ranges = {
        'blue': ([90, 50, 50], [130, 255, 255]),
        'red': ([0, 50, 50], [10, 255, 255]),  # Red wraps around, might need two ranges
        'green': ([40, 50, 50], [80, 255, 255]),
        'black': ([0, 0, 0], [180, 255, 30]),
        'white': ([0, 0, 200], [180, 30, 255]),
        'yellow': ([20, 100, 100], [40, 255, 255])
    }
    
    # Add second range for red (which wraps around the hue spectrum)
    red_upper_range = ([170, 50, 50], [180, 255, 255])
    
    dice_results = {}
    detected_dice = []  # Store all detected dice for debugging
    
    # For each color, detect the die and count dots
    for color, (lower, upper) in color_ranges.items():
        # Create mask for this color
        lower = np.array(lower)
        upper = np.array(upper)
        mask = cv2.inRange(hsv, lower, upper)
        
        # Special case for red (which wraps around hue spectrum)
        if color == 'red':
            lower2 = np.array(red_upper_range[0])
            upper2 = np.array(red_upper_range[1])
            mask2 = cv2.inRange(hsv, lower2, upper2)
            mask = cv2.bitwise_or(mask, mask2)
        
        # Find contours for the dice
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter by size to avoid noise
        min_area = 500  # Adjust based on your image
        max_area = 5000  # Maximum area to avoid detecting large objects
        dice_contours = [cnt for cnt in contours if min_area < cv2.contourArea(cnt) < max_area]
        
        # Initialize counter for this color
        dice_count = 0
        
        for cnt in dice_contours:
            # Get bounding box
            x, y, w, h = cv2.boundingRect(cnt)
            die_roi = image[y:y+h, x:x+w]
            
            # Skip very small ROIs
            if w < 20 or h < 20:
                continue
                
            # Special handling for black and white dice
            if color == 'black':
                # For black dice, look for white dots
                dot_mask = cv2.inRange(die_roi, (200, 200, 200), (255, 255, 255))
            elif color == 'white':
                # For white dice, look for black dots
                dot_mask = cv2.inRange(die_roi, (0, 0, 0), (50, 50, 50))
            else:
                # For colored dice, look for white dots
                dot_mask = cv2.inRange(die_roi, (200, 200, 200), (255, 255, 255))
            
            # Find dot contours
            dot_contours, _ = cv2.findContours(dot_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Filter small dots (noise)
            min_dot_area = 5  # Adjust based on your image
            valid_dots = [cnt for cnt in dot_contours if cv2.contourArea(cnt) > min_dot_area]
            
            # Count the dots to determine dice value
            value = len(valid_dots)
            
            # Skip dice with zero value or values greater than 6
            if value == 0 or value > 6:
                continue
            
            # Save this die's info
            dice_count += 1
            die_key = f"{color}_die_{dice_count}"
            dice_results[die_key] = value
            detected_dice.append((color, value, x, y, w, h))
            
            # Draw rectangle around die and show value
            cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(image, f"{value}", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
    
    # Add debug information to the image
    for i, (color, value, x, y, w, h) in enumerate(detected_dice):
        # Add color label below each die
        cv2.putText(image, color, (x, y+h+20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    
    # Display results
    cv2.imshow("Dice Detection", image)
    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:  # 'q' or ESC key
            break
    cv2.destroyAllWindows()
    
    return dice_results

img_path = Path(__file__).parent.parent.parent.parent / "stuff" / "dice_1.jpg"
results = detect_dice(str(img_path))
print("Detected dice values:", results)