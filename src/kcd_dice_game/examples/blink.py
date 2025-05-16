import numpy as np
import cv2
import time

# Parameters
width, height = 800, 600  # Video size
dot_radius = 20
dot_color = (0, 0, 255)  # Red dot in BGR
dot_position = (width // 2, height // 2)  # Center of the screen

# Timing parameters
# Default is 0.1 and 0.2
blink_duration = 0.1  # milliseconds
interval_duration = 0.8  # milliseconds


def main():
    # Create a window
    cv2.namedWindow("Blinking Dot", cv2.WINDOW_NORMAL)

    # Set the start time
    start_time = time.time()

    while True:
        # Create a blank black image
        img = np.zeros((height, width, 3), dtype=np.uint8)

        # Calculate elapsed time since start
        elapsed_time = time.time() - start_time

        # Total cycle time (blink + interval)
        cycle_time = blink_duration + interval_duration

        # Calculate time within the current cycle
        time_in_cycle = elapsed_time % cycle_time

        # Draw dot if we're in the blink phase
        if time_in_cycle < blink_duration:
            cv2.circle(img, dot_position, dot_radius, dot_color, -1)

        # Display the image
        cv2.imshow("Blinking Dot", img)

        # Check for exit (press 'q' to quit)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    # Clean up
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
