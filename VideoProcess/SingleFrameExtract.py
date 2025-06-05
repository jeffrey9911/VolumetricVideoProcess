import cv2
import os
import numpy as np
from pathlib import Path

def extract_and_split_frames(video_path, output_dir, frame_width=1280, frame_height=720):
    """
    Extract frames from a vertically concatenated video and split each frame 
    into individual smaller frames.
    
    Args:
        video_path (str): Path to the input video file
        output_dir (str): Directory to save extracted frames
        frame_width (int): Width of individual small videos (default: 1280)
        frame_height (int): Height of individual small videos (default: 720)
    """
    
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Open the video file
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f"Error: Could not open video file {video_path}")
        return
    
    # Get video properties
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    video_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    video_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    print(f"Video properties:")
    print(f"  Total frames: {total_frames}")
    print(f"  FPS: {fps}")
    print(f"  Dimensions: {video_width}x{video_height}")
    
    # Calculate number of small videos
    num_videos = video_height // frame_height
    print(f"  Number of concatenated videos: {num_videos}")
    
    if video_height % frame_height != 0:
        print(f"Warning: Video height ({video_height}) is not evenly divisible by frame height ({frame_height})")
    
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            break
        
        print(f"Processing frame {frame_count + 1}/{total_frames}", end='\r')
        
        # Split the frame into smaller frames
        for video_idx in range(num_videos):
            # Calculate the region for this small video
            y_start = video_idx * frame_height
            y_end = (video_idx + 1) * frame_height
            
            # Extract the sub-frame
            sub_frame = frame[y_start:y_end, 0:frame_width]
            
            # Create filename for this sub-frame
            # Format: frame_{frame_number}_video_{video_index}.jpg
            filename = f"frame_{frame_count:06d}_video_{video_idx:02d}.jpg"
            filepath = os.path.join(output_dir, filename)
            
            # Save the sub-frame
            cv2.imwrite(filepath, sub_frame)
        
        frame_count += 1
    
    cap.release()
    print(f"\nCompleted! Extracted {frame_count} frames, split into {num_videos} sub-videos each.")
    print(f"Total images saved: {frame_count * num_videos}")

def extract_and_split_frames_organized(video_path, output_dir, frame_width=1280, frame_height=720):
    """
    Same as above but organizes output into separate folders for each sub-video.
    """
    
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Open the video file
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f"Error: Could not open video file {video_path}")
        return
    
    # Get video properties
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    video_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    video_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    print(f"Video properties:")
    print(f"  Total frames: {total_frames}")
    print(f"  FPS: {fps}")
    print(f"  Dimensions: {video_width}x{video_height}")
    
    # Calculate number of small videos
    num_videos = video_height // frame_height
    print(f"  Number of concatenated videos: {num_videos}")
    
    # Create subdirectories for each video
    video_dirs = []
    for i in range(num_videos):
        video_dir = os.path.join(output_dir, f"video_{i:02d}")
        Path(video_dir).mkdir(parents=True, exist_ok=True)
        video_dirs.append(video_dir)
    
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            break
        
        print(f"Processing frame {frame_count + 1}/{total_frames}", end='\r')
        
        # Split the frame into smaller frames
        for video_idx in range(num_videos):
            # Calculate the region for this small video
            y_start = video_idx * frame_height
            y_end = (video_idx + 1) * frame_height
            
            # Extract the sub-frame
            sub_frame = frame[y_start:y_end, 0:frame_width]
            
            # Create filename for this sub-frame
            filename = f"frame_{frame_count:06d}.jpg"
            filepath = os.path.join(video_dirs[video_idx], filename)
            
            # Save the sub-frame
            cv2.imwrite(filepath, sub_frame)
        
        frame_count += 1
    
    cap.release()
    print(f"\nCompleted! Extracted {frame_count} frames, split into {num_videos} sub-videos each.")
    print(f"Total images saved: {frame_count * num_videos}")

# Example usage
if __name__ == "__main__":
    # Configuration
    input_video_path = "/Users/yaojie/Desktop/sample.mkv"  # Change this to your video path
    output_directory = "/Users/yaojie/Desktop/output/sample_output"  # Change this to your desired output directory
    
    # Option 1: Save all frames in one directory with descriptive names
    print("Option 1: All frames in one directory")
    extract_and_split_frames(
        video_path=input_video_path,
        output_dir=output_directory,
        frame_width=1280,
        frame_height=720
    )
    
    # Option 2: Save frames organized in separate folders for each sub-video
    # Uncomment the lines below if you prefer this organization
    """
    print("\nOption 2: Frames organized by sub-video")
    extract_and_split_frames_organized(
        video_path=input_video_path,
        output_dir=output_directory + "_organized",
        frame_width=1280,
        frame_height=720
    )
    """
