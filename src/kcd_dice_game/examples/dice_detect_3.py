import cv2
import numpy as np
from pathlib import Path

def detect_dice(image_path):
    # Read the image
    image = cv2.imread(image_path)
    
    # Convert to HSV for better color segmentation
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # Define color ranges for each die - further expanded ranges
    color_ranges = {
        'blue': ([90, 30, 30], [150, 255, 255]),
        'red': ([0, 30, 30], [20, 255, 255]),  # Expanded red range
        'green': ([35, 30, 30], [90, 255, 255]),  # Expanded green range
        'black': ([0, 0, 0], [180, 100, 60]),  # Adjusted black range
        'white': ([0, 0, 150], [180, 60, 255]),  # Adjusted white range
        'yellow': ([15, 30, 30], [50, 255, 255])  # Expanded yellow range
    }
    
    # Add second range for red (which wraps around the hue spectrum)
    red_upper_range = ([150, 30, 30], [180, 255, 255])
    
    dice_results = {}
    detected_dice = []  # Store all detected dice for debugging
    
    # For debugging, save color masks
    debug_dir = Path(__file__).parent.parent.parent.parent / "stuff" / "debug"
    debug_dir.mkdir(exist_ok=True)
    
    # Create a composite mask for all dice to prevent overlap detection
    composite_mask = np.zeros_like(hsv[:,:,0])
    
    # First pass - detect all dice
    all_dice_contours = []
    
    # For each color, detect the die
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
        
        # Save color mask for debugging
        cv2.imwrite(str(debug_dir / f"{color}_mask.jpg"), mask)
        
        # Apply morphological operations to improve mask
        kernel = np.ones((3, 3), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        # Find contours for the dice
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter by size and shape to find dice
        min_area = 400  # Reduced minimum area to catch smaller dice
        max_area = 10000  # Maximum area to avoid detecting large objects
        
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if min_area < area < max_area:
                # Check if it's roughly square (dice shape)
                x, y, w, h = cv2.boundingRect(cnt)
                aspect_ratio = float(w) / h
                if 0.6 < aspect_ratio < 1.5:  # More lenient aspect ratio
                    all_dice_contours.append((color, cnt, x, y, w, h))
    
    # Sort dice by area (largest first) to prioritize better detections
    all_dice_contours.sort(key=lambda x: cv2.contourArea(x[1]), reverse=True)
    
    # Second pass - process each detected die
    dice_count = {color: 0 for color in color_ranges.keys()}
    
    for color, cnt, x, y, w, h in all_dice_contours:
        # Check if this area overlaps with already detected dice
        mask_roi = composite_mask[y:y+h, x:x+w]
        if np.any(mask_roi > 0):
            # There's significant overlap with an already detected die
            continue
        
        # Extract the ROI using the bounding box
        die_roi = image[y:y+h, x:x+w]
        
        # Skip small ROIs
        if w < 15 or h < 15:
            continue
            
        # Adjust dot detection thresholds for different colored dice
        if color == 'black':
            # For black dice, look for white dots
            dot_mask = cv2.inRange(die_roi, (170, 170, 170), (255, 255, 255))
        elif color == 'white':
            # For white dice, look for black dots
            dot_mask = cv2.inRange(die_roi, (0, 0, 0), (80, 80, 80))
        else:
            # For colored dice, look for white dots
            dot_mask = cv2.inRange(die_roi, (170, 170, 170), (255, 255, 255))
        
        # Save dot mask for debugging
        cv2.imwrite(str(debug_dir / f"{color}_die_{dice_count[color]}_dots.jpg"), dot_mask)
        
        # Apply morphological operations to improve dot detection
        dot_kernel = np.ones((2, 2), np.uint8)
        dot_mask = cv2.morphologyEx(dot_mask, cv2.MORPH_OPEN, dot_kernel)
        
        # Find dot contours
        dot_contours, _ = cv2.findContours(dot_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter dots more carefully
        valid_dots = []
        for dot_cnt in dot_contours:
            dot_area = cv2.contourArea(dot_cnt)
            
            # Dynamic thresholds based on die size
            min_dot_area = max(3, w * h * 0.0008)  # Lower threshold to catch small dots
            max_dot_area = max(150, w * h * 0.1)   # Higher threshold for larger dice
            
            if min_dot_area < dot_area < max_dot_area:
                # Calculate circularity
                perimeter = cv2.arcLength(dot_cnt, True)
                if perimeter > 0:
                    circularity = 4 * np.pi * dot_area / (perimeter * perimeter)
                    # More lenient circularity check
                    if circularity > 0.4:
                        valid_dots.append(dot_cnt)
        
        # Count the dots to determine dice value
        value = len(valid_dots)
        
        # Skip dice with invalid values
        if value < 1 or value > 6:
            continue
        
        # Mark this area in the composite mask to prevent overlaps
        cv2.drawContours(composite_mask, [cnt], 0, 255, -1)
        
        # Save this die's info
        dice_count[color] += 1
        die_key = f"{color}_die_{dice_count[color]}"
        dice_results[die_key] = value
        detected_dice.append((color, value, x, y, w, h))
        
        # Draw rectangle around die
        cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
        
        # Show value
        cv2.putText(image, f"{value}", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        
        # Add color label
        cv2.putText(image, color, (x, y+h+20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        # Debug: Draw circles around detected dots for verification
        for dot in valid_dots:
            # Get centroid of dot
            M = cv2.moments(dot)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"]) + x
                cy = int(M["m01"] / M["m00"]) + y
                cv2.circle(image, (cx, cy), 3, (255, 0, 255), -1)
    
    # Display results
    cv2.imshow("Dice Detection", image)
    # Save result image
    cv2.imwrite(str(debug_dir / "result.jpg"), image)
    
    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:  # 'q' or ESC key
            break
    cv2.destroyAllWindows()
    
    return dice_results

img_path = Path(__file__).parent.parent.parent.parent / "stuff" / "dice_2.jpg"
results = detect_dice(str(img_path))
print("Detected dice values:", results)