import subprocess
import json
import os
from pathlib import Path

def split_grid_canvas_video_ffmpeg(input_video_path, output_dir, track_width=1080, track_height=1920, num_cols=4, num_rows=2):
    """
    Split video canvas into a grid of videos using FFmpeg.
    
    Args:
        input_video_path: Path to input video file
        output_dir: Directory to save output video tracks
        track_width: Width of each video track
        track_height: Height of each video track  
        num_cols: Number of columns in the grid
        num_rows: Number of rows in the grid
    """
    
    # Create output directory
    video_tracks_dir = os.path.join(output_dir, "video_tracks")
    Path(video_tracks_dir).mkdir(parents=True, exist_ok=True)
    
    # Get video info using FFmpeg
    probe_cmd = [
        'ffprobe', '-v', 'quiet', '-print_format', 'json', 
        '-show_format', '-show_streams', input_video_path
    ]
    
    try:
        result = subprocess.run(probe_cmd, capture_output=True, text=True, check=True)
        video_info = json.loads(result.stdout)
        video_stream = next(s for s in video_info['streams'] if s['codec_type'] == 'video')
        
        video_width = int(video_stream['width'])
        video_height = int(video_stream['height'])
        fps = eval(video_stream['r_frame_rate'])  # Convert fraction to float
        
        print(f"Video dimensions: {video_width}x{video_height}")
        print(f"FPS: {fps}")
        print(f"Expected grid: {num_cols} columns × {num_rows} rows")
        print(f"Track size: {track_width}x{track_height}")
        
    except Exception as e:
        print(f"Error getting video info: {e}")
        return False
    
    # Calculate actual number of tracks based on video dimensions
    actual_num_cols = min(num_cols, video_width // track_width)
    actual_num_rows = min(num_rows, video_height // track_height)
    total_tracks = actual_num_cols * actual_num_rows
    
    print(f"Actual grid: {actual_num_cols} columns × {actual_num_rows} rows")
    print(f"Processing {total_tracks} tracks total")
    
    # Split video using FFmpeg
    track_count = 0
    for row in range(actual_num_rows):
        for col in range(actual_num_cols):
            # Calculate crop coordinates
            x_start = col * track_width
            y_start = row * track_height
            
            # Create output filename
            output_path = os.path.join(video_tracks_dir, f"video_r{row:02d}_c{col:02d}.mp4")
            
            ffmpeg_cmd = [
                'ffmpeg', '-i', input_video_path,
                '-vf', f'crop={track_width}:{track_height}:{x_start}:{y_start}',
                '-c:v', 'libx264',  # H264 codec
                '-crf', '23',       # Quality setting
                '-preset', 'medium', # Encoding speed/quality tradeoff
                '-y',               # Overwrite output files
                output_path
            ]
            
            track_count += 1
            print(f"Processing track {track_count}/{total_tracks} (Row {row+1}, Col {col+1})...")
            print(f"  Crop coordinates: x={x_start}, y={y_start}")
            
            try:
                subprocess.run(ffmpeg_cmd, check=True, capture_output=True)
                print(f"  ✓ Created: video_r{row:02d}_c{col:02d}.mp4")
            except subprocess.CalledProcessError as e:
                print(f"  ✗ Error processing track (Row {row+1}, Col {col+1}): {e}")
                return False
    
    print(f"\n✓ Successfully split video into {total_tracks} tracks!")
    print(f"Grid layout: {actual_num_cols} columns × {actual_num_rows} rows")
    return True

def split_horizontal_canvas_video_ffmpeg(input_video_path, output_dir, track_width=720, track_height=1280, num_tracks=20):
    """
    Original function - Split video horizontally (single row) using FFmpeg.
    Kept for backward compatibility.
    """
    
    # Create output directory
    video_tracks_dir = os.path.join(output_dir, "video_tracks")
    Path(video_tracks_dir).mkdir(parents=True, exist_ok=True)
    
    # Get video info using FFmpeg
    probe_cmd = [
        'ffprobe', '-v', 'quiet', '-print_format', 'json', 
        '-show_format', '-show_streams', input_video_path
    ]
    
    try:
        result = subprocess.run(probe_cmd, capture_output=True, text=True, check=True)
        video_info = json.loads(result.stdout)
        video_stream = next(s for s in video_info['streams'] if s['codec_type'] == 'video')
        
        video_width = int(video_stream['width'])
        video_height = int(video_stream['height'])
        fps = eval(video_stream['r_frame_rate'])  # Convert fraction to float
        
        print(f"Video dimensions: {video_width}x{video_height}")
        print(f"FPS: {fps}")
        
    except Exception as e:
        print(f"Error getting video info: {e}")
        return False
    
    # Calculate actual number of tracks
    actual_num_tracks = min(num_tracks, video_width // track_width)
    print(f"Processing {actual_num_tracks} tracks")
    
    # Split video using FFmpeg
    for i in range(actual_num_tracks):
        x_start = i * track_width
        output_path = os.path.join(video_tracks_dir, f"video_{i:02d}.mp4")
        
        ffmpeg_cmd = [
            'ffmpeg', '-i', input_video_path,
            '-vf', f'crop={track_width}:{track_height}:{x_start}:0',
            '-c:v', 'libx264',  # H264 codec
            '-crf', '23',       # Quality setting
            '-preset', 'medium', # Encoding speed/quality tradeoff
            '-y',               # Overwrite output files
            output_path
        ]
        
        print(f"Processing track {i+1}/{actual_num_tracks}...")
        
        try:
            subprocess.run(ffmpeg_cmd, check=True, capture_output=True)
            print(f"✓ Created: video_{i:02d}.mp4")
        except subprocess.CalledProcessError as e:
            print(f"✗ Error processing track {i}: {e}")
            return False
    
    print(f"\n✓ Successfully split video into {actual_num_tracks} tracks!")
    return True

# Usage
if __name__ == "__main__":
    input_video_path = "/Users/yaojie/Desktop/VV-Datasets/0702-GS/take_1/input.mkv"
    output_directory = "/Users/yaojie/Desktop/VV-Datasets/0702-GS/take_1/v"
    
    # Use the new grid-based method for your 4320×3840 canvas
    # 4 columns × 2 rows of 1080×1920 videos
    try:
        success = split_grid_canvas_video_ffmpeg(
            input_video_path=input_video_path,
            output_dir=output_directory,
            track_width=1080,
            track_height=1920,
            num_cols=4,
            num_rows=2
        )
        if success:
            print("✓ Grid method completed successfully!")
        else:
            print("✗ Grid method failed")
    except Exception as e:
        print(f"✗ Grid method encountered an error: {e}")
        
    # Alternative: If you want to use the original horizontal method
    # Uncomment the lines below:
    # try:
    #     success = split_horizontal_canvas_video_ffmpeg(
    #         input_video_path=input_video_path,
    #         output_dir=output_directory,
    #         track_width=1080,
    #         track_height=1920,
    #         num_tracks=8
    #     )
    #     if success:
    #         print("✓ FFmpeg method completed successfully!")
    #     else:
    #         print("✗ FFmpeg method failed")
    # except Exception as e:
    #     print(f"✗ FFmpeg method encountered an error: {e}")