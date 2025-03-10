from tkinter import Tk, filedialog
import numpy as np
import cv2

def get_duration(video_path):
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    duration_seconds = total_frames / fps
    cap.release()
    return duration_seconds

def display_vids(video1_path, video2_path):
    cap1 = cv2.VideoCapture(video1_path)
    cap2 = cv2.VideoCapture(video2_path)
    # Find the duration of each video
    duration_seconds1 = get_duration(video1_path)
    duration_seconds2 = get_duration(video2_path)

    # Use the longer duration for the loop termination
    max_duration = max(duration_seconds1, duration_seconds2)

    while True:
        ret1, frame1 = cap1.read()
        ret2, frame2 = cap2.read()

        if not ret1 or not ret2:
            break  # Break the loop if any video ends

        # Resize frames to have the same height (assuming videos have the same resolution)
        height, width = frame1.shape[:2]
        frame2 = cv2.resize(frame2, (width, height))

        # Display videos side by side
        combined_frame = cv2.hconcat([frame1, frame2])
        cv2.imshow('Side-by-Side Videos', combined_frame)

        # Break the loop if the user presses 'q'
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

    # Release the video capture objects and close the window
    cap1.release()
    cap2.release()
    cv2.destroyAllWindows()


def main():
    root_dir = 'D:\\'
    root = Tk()
    root.withdraw()  # Hide the main window

    # Ask the user to select the first video file
    video1_path = filedialog.askopenfilename(
        initialdir=root_dir,
        title="Select the first video file",
        filetypes=(("MP4 files", "*.mp4"), ("All files", "*.*"))
    )

    # Ask the user to select the second video file
    video2_path = filedialog.askopenfilename(
        initialdir=root_dir,
        title="Select the first video file",
        filetypes=(("MP4 files", "*.mp4"), ("All files", "*.*"))
    )

    if not video1_path or not video2_path:
        print("No file selected. Exiting.")
        return

    display_vids(video1_path, video2_path)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

