import subprocess
import json

def split_horizontal_canvas_video_ffmpeg(input_video_path, output_dir, track_width=720, track_height=1280, num_tracks=20):
    """
    Split video using FFmpeg for better codec support.
    """
    import subprocess
    import os
    from pathlib import Path
    
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
    input_video_path = "/Users/yaojie/Desktop/test_02/canv.mkv"
    output_directory = "/Users/yaojie/Desktop/test_02/v"
    
    # Try FFmpeg method first
    try:
        success = split_horizontal_canvas_video_ffmpeg(
            input_video_path=input_video_path,
            output_dir=output_directory,
            track_width=720,
            track_height=1280,
            num_tracks=20
        )
        if success:
            print("✓ FFmpeg method completed successfully!")
        else:
            print("✗ FFmpeg method failed, trying OpenCV with MJPG...")
    except Exception as e:
        print(f"✗ FFmpeg method encountered an error: {e}")
