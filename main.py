import cv2
import os
import numpy as np
from tkinter import Tk, filedialog, messagebox, simpledialog

def apply_motion_blur(video_path, output_video_path, custom_fps, blend_factor=0.7):
    try:
        cap = cv2.VideoCapture(video_path)

        # Get width and height of the video
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # Define the video extension
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_video_path, fourcc, custom_fps, (width, height))

        # Get the first two frames for motion tracking
        ret, prev_frame = cap.read()
        if not ret:
            raise Exception("Failed to read the video.")
        prev_frame_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)

        while cap.isOpened():
            ret, current_frame = cap.read()
            if not ret:
                break

            # Convert the current frame to grayscale for motion detection
            current_frame_gray = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)

            # Compute the absolute difference between the current frame and the previous frame
            frame_diff = cv2.absdiff(current_frame_gray, prev_frame_gray)

            # Threshold the difference to get a binary mask of motion areas
            _, motion_mask = cv2.threshold(frame_diff, 25, 255, cv2.THRESH_BINARY)

            # Determine the direction of motion and apply appropriate directional blur
            motion_blurred_frame = apply_directional_blur(current_frame, prev_frame_gray, current_frame_gray, motion_mask)

            # Write the motion-blurred frame to the output video
            out.write(motion_blurred_frame)

            # Update the previous frame for the next iteration
            prev_frame_gray = current_frame_gray

        cap.release()
        out.release()

        # Show success message
        Tk().withdraw()
        messagebox.showinfo("Success", "Video Complete: Directional blur added based on motion direction.")
    except Exception as e:
        # Show error message if something goes wrong
        Tk().withdraw()
        messagebox.showerror("Error", f"Error: {e}")
        print(f"Error: {e}")

def apply_directional_blur(frame, prev_frame_gray, current_frame_gray, motion_mask):
    # Calculate the optical flow (motion direction) between the previous and current frames
    flow = cv2.calcOpticalFlowFarneback(prev_frame_gray, current_frame_gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)

    # Calculate the motion magnitude and angle
    mag, ang = cv2.cartToPolar(flow[..., 0], flow[..., 1])

    # Calculate average direction of motion in motion areas
    motion_direction = np.mean(ang[motion_mask > 0])

    # Determine the motion type (horizontal or vertical) based on the average direction
    if 0 <= motion_direction < np.pi / 4 or 7 * np.pi / 4 <= motion_direction <= 2 * np.pi:  # Mostly horizontal
        blur_type = 'horizontal'
        kernel = create_directional_kernel('horizontal')
    elif np.pi / 4 <= motion_direction < 3 * np.pi / 4:  # Mostly vertical
        blur_type = 'vertical'
        kernel = create_directional_kernel('vertical')
    else:
        blur_type = 'diagonal'
        kernel = create_directional_kernel('horizontal')  # Default to horizontal blur

    # Apply the selected directional blur to the entire frame
    blurred_frame = cv2.filter2D(frame, -1, kernel)

    # Use the motion mask to apply the directional blur only to motion areas
    motion_areas = cv2.bitwise_and(blurred_frame, blurred_frame, mask=motion_mask)

    # Combine the motion-blurred areas with the original frame
    inverse_mask = cv2.bitwise_not(motion_mask)
    static_areas = cv2.bitwise_and(frame, frame, mask=inverse_mask)
    result_frame = cv2.add(static_areas, motion_areas)

    return result_frame

def create_directional_kernel(direction):
    """Creates a directional kernel for horizontal or vertical motion blur"""
    kernel_size = 30
    if direction == 'horizontal':
        kernel = np.zeros((kernel_size, kernel_size))
        kernel[int((kernel_size - 1)/2), :] = np.ones(kernel_size)  # Horizontal line for blur
    elif direction == 'vertical':
        kernel = np.zeros((kernel_size, kernel_size))
        kernel[:, int((kernel_size - 1)/2)] = np.ones(kernel_size)  # Vertical line for blur
    else:
        kernel = np.eye(kernel_size)  # Diagonal blur as fallback
    return kernel / kernel_size

def select_video_file():
    Tk().withdraw() 
    video_path = filedialog.askopenfilename(title="Select a video file", filetypes=[("Video files", "*.mp4;*.avi;*.mov")])

    if not video_path:
        print("No video file selected. Exiting.")
        return None, None

    # Extract the folder and base name from the selected file
    video_folder = os.path.dirname(video_path)
    video_filename = os.path.basename(video_path)
    base_name = os.path.splitext(video_filename)[0]

    output_video_path = os.path.join(video_folder, f"{base_name}_motion_blur.mp4")

    return video_path, output_video_path

def get_custom_frame_rate(default_fps):
    # Enter custom frame rate
    Tk().withdraw()
    try:
        custom_fps = simpledialog.askfloat("Frame Rate", f"Enter the video frame rate (default: {default_fps}):", initialvalue=default_fps)
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

        # Get the user entered frame rate
        custom_fps = get_custom_frame_rate(default_fps)

        # Apply motion blur and frame rate
        apply_motion_blur(video_path, output_video_path, custom_fps)
