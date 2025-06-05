import cv2
import os
import numpy as np
from pathlib import Path

def split_horizontal_canvas_video(input_video_path, output_dir, track_width=720, track_height=1280, num_tracks=20):
    """
    Split a horizontally concatenated video into separate video files.
    
    Args:
        input_video_path (str): Path to the input canvas video
        output_dir (str): Directory to save the split videos
        track_width (int): Width of each video track (default: 720)
        track_height (int): Height of each video track (default: 1280)
        num_tracks (int): Number of video tracks (default: 20)
    """
    
    # Create output directory structure
    video_tracks_dir = os.path.join(output_dir, "video_tracks")
    Path(video_tracks_dir).mkdir(parents=True, exist_ok=True)
    
    # Open the input video
    cap = cv2.VideoCapture(input_video_path)
    
    if not cap.isOpened():
        print(f"Error: Could not open video file {input_video_path}")
        return
    
    # Get video properties
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    video_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    video_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    print(f"Input video properties:")
    print(f"  Total frames: {total_frames}")
    print(f"  FPS: {fps}")
    print(f"  Dimensions: {video_width}x{video_height}")
    print(f"  Expected canvas size: {track_width * num_tracks}x{track_height}")
    
    # Verify dimensions
    if video_width != track_width * num_tracks:
        print(f"Warning: Video width ({video_width}) doesn't match expected canvas width ({track_width * num_tracks})")
    if video_height != track_height:
        print(f"Warning: Video height ({video_height}) doesn't match expected track height ({track_height})")
    
    # Calculate actual number of tracks if dimensions don't match exactly
    actual_num_tracks = min(num_tracks, video_width // track_width)
    print(f"  Processing {actual_num_tracks} video tracks")
    
    # Define codec and create VideoWriter objects
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # You can also use 'XVID' or 'H264'
    
    # Create VideoWriter objects for each track
    video_writers = []
    for i in range(actual_num_tracks):
        output_path = os.path.join(video_tracks_dir, f"video_{i:02d}.mp4")
        writer = cv2.VideoWriter(output_path, fourcc, fps, (track_width, track_height))
        if not writer.isOpened():
            print(f"Error: Could not create video writer for track {i}")
            # Clean up already created writers
            for w in video_writers:
                w.release()
            cap.release()
            return
        video_writers.append(writer)
        print(f"  Created output video: {output_path}")
    
    print(f"\nStarting video processing...")
    frame_count = 0
    
    try:
        while True:
            ret, frame = cap.read()
            
            if not ret:
                break
            
            if frame_count % 100 == 0:  # Print progress every 100 frames
                print(f"Processing frame {frame_count + 1}/{total_frames} ({((frame_count + 1)/total_frames)*100:.1f}%)")
            
            # Split the frame horizontally and write to respective videos
            for track_idx in range(actual_num_tracks):
                # Calculate the region for this track
                x_start = track_idx * track_width
                x_end = (track_idx + 1) * track_width
                
                # Extract the sub-frame for this track
                track_frame = frame[0:track_height, x_start:x_end]
                
                # Write the frame to the corresponding video file
                video_writers[track_idx].write(track_frame)
            
            frame_count += 1
    
    except KeyboardInterrupt:
        print("\nProcessing interrupted by user")
    
    except Exception as e:
        print(f"\nError during processing: {str(e)}")
    
    finally:
        # Clean up
        cap.release()
        for i, writer in enumerate(video_writers):
            writer.release()
            print(f"Saved video track {i:02d}")
        
        print(f"\nCompleted! Processed {frame_count} frames.")
        print(f"Created {actual_num_tracks} video files in: {video_tracks_dir}")

def split_horizontal_canvas_video_with_custom_codec(input_video_path, output_dir, track_width=720, track_height=1280, num_tracks=20, output_codec='H264'):
    """
    Enhanced version with custom codec support and better error handling.
    """
    
    # Create output directory structure
    video_tracks_dir = os.path.join(output_dir, "video_tracks")
    Path(video_tracks_dir).mkdir(parents=True, exist_ok=True)
    
    # Open the input video
    cap = cv2.VideoCapture(input_video_path)
    
    if not cap.isOpened():
        print(f"Error: Could not open video file {input_video_path}")
        return False
    
    # Get video properties
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    video_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    video_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    print(f"Input video properties:")
    print(f"  File: {input_video_path}")
    print(f"  Total frames: {total_frames}")
    print(f"  FPS: {fps}")
    print(f"  Dimensions: {video_width}x{video_height}")
    
    # Calculate actual number of tracks
    actual_num_tracks = min(num_tracks, video_width // track_width)
    print(f"  Processing {actual_num_tracks} video tracks")
    print(f"  Each track will be: {track_width}x{track_height}")
    
    # Define codec options
    codec_options = {
        'H264': cv2.VideoWriter_fourcc(*'H264'),
        'XVID': cv2.VideoWriter_fourcc(*'XVID'),
        'mp4v': cv2.VideoWriter_fourcc(*'mp4v'),
        'MJPG': cv2.VideoWriter_fourcc(*'MJPG')
    }
    
    if output_codec not in codec_options:
        print(f"Warning: Unknown codec {output_codec}, using mp4v")
        output_codec = 'mp4v'
    
    fourcc = codec_options[output_codec]
    
    # Create VideoWriter objects for each track
    video_writers = []
    output_paths = []
    
    for i in range(actual_num_tracks):
        output_path = os.path.join(video_tracks_dir, f"video_{i:02d}.mp4")
        output_paths.append(output_path)
        
        writer = cv2.VideoWriter(output_path, fourcc, fps, (track_width, track_height))
        
        if not writer.isOpened():
            print(f"Error: Could not create video writer for track {i}")
            # Clean up already created writers
            for w in video_writers:
                w.release()
            cap.release()
            return False
        
        video_writers.append(writer)
    
    print(f"\nOutput videos will be saved to: {video_tracks_dir}")
    print(f"Using codec: {output_codec}")
    print(f"Starting video processing...")
    
    frame_count = 0
    last_percent = -1
    
    try:
        while True:
            ret, frame = cap.read()
            
            if not ret:
                break
            
            # Progress reporting
            current_percent = int((frame_count / total_frames) * 100)
            if current_percent != last_percent and current_percent % 5 == 0:
                print(f"Progress: {current_percent}% ({frame_count}/{total_frames} frames)")
                last_percent = current_percent
            
            # Split the frame horizontally and write to respective videos
            for track_idx in range(actual_num_tracks):
                x_start = track_idx * track_width
                x_end = (track_idx + 1) * track_width
                
                # Extract and validate the sub-frame
                if x_end <= video_width:
                    track_frame = frame[0:min(track_height, video_height), x_start:x_end]
                    
                    # Resize if necessary to match expected dimensions
                    if track_frame.shape[:2] != (track_height, track_width):
                        track_frame = cv2.resize(track_frame, (track_width, track_height))
                    
                    video_writers[track_idx].write(track_frame)
            
            frame_count += 1
    
    except KeyboardInterrupt:
        print("\nProcessing interrupted by user")
        return False
    
    except Exception as e:
        print(f"\nError during processing: {str(e)}")
        return False
    
    finally:
        # Clean up
        cap.release()
        for writer in video_writers:
            writer.release()
    
    print(f"\n✓ Successfully completed!")
    print(f"✓ Processed {frame_count} frames")
    print(f"✓ Created {actual_num_tracks} video files:")
    
    for i, path in enumerate(output_paths):
        if os.path.exists(path):
            file_size = os.path.getsize(path) / (1024 * 1024)  # Size in MB
            print(f"  - video_{i:02d}.mp4 ({file_size:.1f} MB)")
    
    return True

# Example usage and utility functions
def get_video_info(video_path):
    """Get detailed information about a video file."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return None
    
    info = {
        'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
        'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        'fps': cap.get(cv2.CAP_PROP_FPS),
        'frame_count': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
        'duration': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) / cap.get(cv2.CAP_PROP_FPS)
    }
    
    cap.release()
    return info

if __name__ == "__main__":
    # Configuration
    input_video_path = "/Users/yaojie/Desktop/output/0604-GS/1lh.mkv"  # Change this to your canvas video path
    output_directory = "/Users/yaojie/Desktop/output/0604-GS/v"
    
    # Check if input video exists
    if not os.path.exists(input_video_path):
        print(f"Error: Input video file '{input_video_path}' not found!")
        print("Please update the input_video_path variable with the correct path.")
    else:
        # Get video info first
        info = get_video_info(input_video_path)
        if info:
            print("Input video analysis:")
            print(f"  Dimensions: {info['width']}x{info['height']}")
            print(f"  Duration: {info['duration']:.1f} seconds")
            print(f"  FPS: {info['fps']}")
            print(f"  Total frames: {info['frame_count']}")
            print()
        
        # Split the video
        success = split_horizontal_canvas_video_with_custom_codec(
            input_video_path=input_video_path,
            output_dir=output_directory,
            track_width=720,
            track_height=1280,
            num_tracks=20,
            output_codec='H264'  # Options: 'H264', 'XVID', 'mp4v', 'MJPG'
        )
        
        if success:
            print(f"\n🎉 All done! Check the '{output_directory}/video_tracks/' folder for your split videos.")
        else:
            print(f"\n❌ Processing failed. Please check the error messages above.")
