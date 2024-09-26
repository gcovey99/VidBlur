import cv2
import os
from tkinter import Tk, filedialog, messagebox, simpledialog

def apply_motion_blur(video_path, output_video_path, custom_fps, blend_factor=0.7, blur_kernel_size=(5, 5)):
    try:
        cap = cv2.VideoCapture(video_path)

        # Get the width and height of the video
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # Create a VideoWriter object to save the new video
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_video_path, fourcc, custom_fps, (width, height))

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

            # Apply a blur to the blended frame
            blurred_frame = cv2.GaussianBlur(blended_frame, blur_kernel_size, 0)

            # Write the blurred frame to the output video
            out.write(blurred_frame)

            # Update frames for the next iteration (move to the next frame in sequence)
            prev_frame2 = prev_frame1
            prev_frame1 = current_frame
            current_frame = next_frame
      
        cap.release()
        out.release()

        # Show success message
        Tk().withdraw()
        messagebox.showinfo("Success", "Video Complete: Motion blur is added.")
    except Exception as e:
        # Show error message
        Tk().withdraw()
        messagebox.showerror("Error", f"Error: {e}")
        print(f"Error: {e}")

def select_video_file():
    # Select video file
    Tk().withdraw() 
    video_path = filedialog.askopenfilename(title="Select a video file", filetypes=[("Video files", "*.mp4;*.avi;*.mov")])

    if not video_path:
        print("No video file selected. Exiting.")
        return None, None

    # Extract the folder and base name from the selected file
    video_folder = os.path.dirname(video_path)
    video_filename = os.path.basename(video_path)
    base_name = os.path.splitext(video_filename)[0]

    output_video_path = os.path.join(video_folder, f"{base_name}_blurred.mp4")

    return video_path, output_video_path

def custom_frame_rate(default_fps):
    # Enter custom frame rate
    Tk().withdraw()
    try:
        custom_fps = simpledialog.askfloat("Frame Rate", f"Enter the desired frame rate (default: {default_fps}):", initialvalue=default_fps)
        if custom_fps is None or custom_fps <= 0:
            raise ValueError("Invalid frame rate entered.")
        return custom_fps
    except Exception as e:
        messagebox.showerror("Invalid Input", "Please enter a valid frame rate.")
        return default_fps

if __name__ == "__main__":
    video_path, output_video_path = select_video_file()

    if video_path and output_video_path:
        # Get default FPS from the video
        cap = cv2.VideoCapture(video_path)
        default_fps = int(cap.get(cv2.CAP_PROP_FPS))
        cap.release()

        # Get the desired frame rate from the user
        custom_fps = custom_frame_rate(default_fps)

        # Apply motion blur with the input frame rate
        apply_motion_blur(video_path, output_video_path, custom_fps)
