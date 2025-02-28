import cv2
import screeninfo
import time
import os

def play_video(video: str):
    time.sleep(1.5) #pause for dramatic affect

    cap = cv2.VideoCapture(video)

    # Check if the video opened successfully
    if not cap.isOpened():
        print("Error: Could not open video.")
        exit()

    # Set the window size (width, height)
    window_width = 1200
    window_height = 800

    # Get the screen resolution (use the first monitor's resolution)
    screen = screeninfo.get_monitors()[0]
    screen_width = screen.width
    screen_height = screen.height

    # Calculate the position to center the window
    x_pos = (screen_width - window_width) // 2
    y_pos = (screen_height - window_height) // 2

    # Create a window and set its size
    cv2.namedWindow('Video', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Video', window_width, window_height)

    # Move the window to the center of the screen
    cv2.moveWindow('Video', x_pos, y_pos)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        cv2.imshow('Video', frame)

        # Wait for keypress, check for window close event
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):  # Press 'q' to quit
            break

        # Check if the window was closed by the user (clicking X)
        if cv2.getWindowProperty('Video', cv2.WND_PROP_VISIBLE) < 1:
            break

    # Release resources and close all OpenCV windows
    cap.release()
    cv2.destroyAllWindows()

def play_exodia():
    if os.path.exists('./media/exodia.mp4'):
        play_video('./media/exodia.mp4')
    else:
        play_video('./media.exodia_normal.mp4')
        
# play_video('./media/exodia.mp4')