import cv2
import os
from tkinter import Tk, filedialog, messagebox

def apply_motion_blur(video_path, output_video_path, blend_factor=1, blur_kernel_size=(5, 5)):
    try:
        cap = cv2.VideoCapture(video_path)

        # Get the width, height, and FPS of the video
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))

        # Define the codec and create a VideoWriter object to save the new video
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

        # Get the first three frames
        ret, prev_frame2 = cap.read()  # Two frames before the current
        if not ret:
            raise Exception("Failed to read the video.")
        ret, prev_frame1 = cap.read()  # One frame before the current
        if not ret:
            raise Exception("Not enough frames in the video.")
        ret, current_frame = cap.read()  # Current frame
        if not ret:
            raise Exception("Not enough frames in the video.")

        while cap.isOpened():
            ret, next_frame = cap.read()
            if not ret:
                break

            # Apply motion blur by blending the current frame with the past two frames
            blended_frame = cv2.addWeighted(current_frame, blend_factor, prev_frame1, blend_factor / 2, 0)

            # This is an option for adding a thrid frame to the blend
            # blended_frame = cv2.addWeighted(blended_frame, 1, prev_frame2, blend_factor / 3, 0)

            # Apply a blur to the blended frame
            blurred_frame = cv2.GaussianBlur(blended_frame, blur_kernel_size, 0)

            # Write the blurred frame to the output video
            out.write(blurred_frame)

            # Update frames for the next iteration (move to the next frame in sequence)
            prev_frame2 = prev_frame1
            prev_frame1 = current_frame
            current_frame = next_frame

        # Release the video objects
        cap.release()
        out.release()

        # Show success message
        Tk().withdraw()  # Hide the root window
        messagebox.showinfo("Success", "Video Complete: Motion blur is added.")
    except Exception as e:
        # Show error message if something goes wrong
        Tk().withdraw()  # Hide the root window
        messagebox.showerror("Error", "Error: There was an error. Please try again.")
        print(f"Error: {e}")

def select_video_file():
    # Use tkinter to open a file dialog to select a video file
    Tk().withdraw() 
    video_path = filedialog.askopenfilename(title="Select a video file", filetypes=[("Video files", "*.mp4;*.avi;*.mov")])

    if not video_path:
        print("No video file selected. Exiting.")
        return None, None

    # Extract the folder and base name from the selected file
    video_folder = os.path.dirname(video_path)
    video_filename = os.path.basename(video_path)
    base_name = os.path.splitext(video_filename)[0]

    # Name the new file
    output_video_path = os.path.join(video_folder, f"{base_name}_blurred.mp4")

    return video_path, output_video_path

# Main script execution
if __name__ == "__main__":
    video_path, output_video_path = select_video_file()

    if video_path and output_video_path:
        apply_motion_blur(video_path, output_video_path)
