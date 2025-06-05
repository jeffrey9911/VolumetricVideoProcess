import cv2
import os
import glob
from pathlib import Path
import numpy as np

def extract_synchronized_frames(input_folder, output_folder):
    """
    Extract frames from multiple videos simultaneously, organizing by frame number.
    
    Args:
        input_folder (str): Path to folder containing .mp4 videos
        output_folder (str): Path where frame folders will be created
    """
    
    # Create output directory if it doesn't exist
    Path(output_folder).mkdir(parents=True, exist_ok=True)
    
    # Find all .mp4 files in the input folder
    video_pattern = os.path.join(input_folder, "*.mp4")
    video_paths = glob.glob(video_pattern)
    video_paths.sort()  # Sort for consistent ordering
    
    if not video_paths:
        print(f"No .mp4 files found in {input_folder}")
        return False
    
    print(f"Found {len(video_paths)} video files:")
    for i, path in enumerate(video_paths):
        print(f"  {i:02d}: {os.path.basename(path)}")
    
    # Open all video files
    video_captures = []
    video_frame_counts = []
    video_info = []
    
    print("\nOpening video files...")
    for i, video_path in enumerate(video_paths):
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"Error: Could not open {video_path}")
            # Clean up already opened captures
            for existing_cap in video_captures:
                existing_cap.release()
            return False
        
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        video_captures.append(cap)
        video_frame_counts.append(frame_count)
        video_info.append({
            'path': video_path,
            'frames': frame_count,
            'fps': fps,
            'width': width,
            'height': height
        })
        
        print(f"  Video {i:02d}: {frame_count} frames, {fps:.1f} FPS, {width}x{height}")
    
    # Determine the minimum frame count (stop when shortest video ends)
    min_frame_count = min(video_frame_counts)
    print(f"\nWill extract {min_frame_count} frames (limited by shortest video)")
    print(f"Total images to be created: {min_frame_count * len(video_captures)}")
    
    # Extract frames
    print(f"\nStarting frame extraction...")
    
    try:
        for frame_idx in range(min_frame_count):
            # Create folder for this frame
            frame_folder = os.path.join(output_folder, f"frame_{frame_idx:05d}")
            Path(frame_folder).mkdir(parents=True, exist_ok=True)
            
            # Progress reporting
            if frame_idx % 50 == 0 or frame_idx == min_frame_count - 1:
                progress = ((frame_idx + 1) / min_frame_count) * 100
                print(f"Processing frame {frame_idx + 1}/{min_frame_count} ({progress:.1f}%)")
            
            # Extract frame from each video
            for video_idx, cap in enumerate(video_captures):
                ret, frame = cap.read()
                
                if not ret:
                    print(f"Warning: Could not read frame {frame_idx} from video {video_idx}")
                    continue
                
                # Save the frame
                image_filename = f"image_{video_idx:05d}.jpg"
                image_path = os.path.join(frame_folder, image_filename)
                
                success = cv2.imwrite(image_path, frame)
                if not success:
                    print(f"Warning: Could not save {image_path}")
    
    except KeyboardInterrupt:
        print("\nProcessing interrupted by user")
        return False
    
    except Exception as e:
        print(f"\nError during processing: {str(e)}")
        return False
    
    finally:
        # Clean up video captures
        print("\nCleaning up...")
        for cap in video_captures:
            cap.release()
    
    print(f"\n✓ Successfully completed!")
    print(f"✓ Extracted {min_frame_count} frames from {len(video_captures)} videos")
    print(f"✓ Created {min_frame_count} frame folders with {len(video_captures)} images each")
    print(f"✓ Output saved to: {output_folder}")
    
    return True

def extract_synchronized_frames_with_options(input_folder, output_folder, 
                                           image_format='jpg', quality=95,
                                           max_frames=None, skip_frames=0):
    """
    Enhanced version with additional options.
    
    Args:
        input_folder (str): Path to folder containing .mp4 videos
        output_folder (str): Path where frame folders will be created
        image_format (str): Output image format ('jpg', 'png')
        quality (int): JPEG quality (1-100, only for jpg format)
        max_frames (int): Maximum number of frames to extract (None for all)
        skip_frames (int): Number of frames to skip between extractions
    """
    
    # Create output directory
    Path(output_folder).mkdir(parents=True, exist_ok=True)
    
    # Find all .mp4 files
    video_pattern = os.path.join(input_folder, "*.mp4")
    video_paths = glob.glob(video_pattern)
    video_paths.sort()
    
    if not video_paths:
        print(f"No .mp4 files found in {input_folder}")
        return False
    
    print(f"Configuration:")
    print(f"  Input folder: {input_folder}")
    print(f"  Output folder: {output_folder}")
    print(f"  Image format: {image_format.upper()}")
    print(f"  Quality: {quality}%" if image_format.lower() == 'jpg' else "")
    print(f"  Skip frames: {skip_frames}")
    print(f"  Max frames: {max_frames if max_frames else 'All'}")
    
    print(f"\nFound {len(video_paths)} video files:")
    
    # Open and analyze all videos
    video_captures = []
    video_info = []
    
    for i, video_path in enumerate(video_paths):
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"Error: Could not open {os.path.basename(video_path)}")
            continue
        
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        video_captures.append(cap)
        video_info.append({
            'index': i,
            'name': os.path.basename(video_path),
            'path': video_path,
            'frames': frame_count,
            'fps': fps,
            'dimensions': f"{width}x{height}"
        })
        
        print(f"  {i:02d}: {os.path.basename(video_path)} "
              f"({frame_count} frames, {fps:.1f} FPS, {width}x{height})")
    
    if not video_captures:
        print("No valid video files found!")
        return False
    
    # Calculate extraction parameters
    min_frame_count = min(info['frames'] for info in video_info)
    
    # Apply frame skipping and max frame limit
    available_frames = list(range(0, min_frame_count, skip_frames + 1))
    if max_frames and max_frames < len(available_frames):
        available_frames = available_frames[:max_frames]
    
    total_frames_to_extract = len(available_frames)
    
    print(f"\nExtraction plan:")
    print(f"  Shortest video has {min_frame_count} frames")
    print(f"  Will extract {total_frames_to_extract} frames per video")
    print(f"  Total images: {total_frames_to_extract * len(video_captures)}")
    
    # Set up image writing parameters
    if image_format.lower() == 'jpg':
        extension = '.jpg'
        write_params = [cv2.IMWRITE_JPEG_QUALITY, quality]
    else:
        extension = '.png'
        write_params = [cv2.IMWRITE_PNG_COMPRESSION, 9]
    
    # Extract frames
    print(f"\nStarting extraction...")
    
    try:
        for extract_idx, frame_idx in enumerate(available_frames):
            # Create folder for this frame
            frame_folder = os.path.join(output_folder, f"frame_{extract_idx:05d}")
            Path(frame_folder).mkdir(parents=True, exist_ok=True)
            
            # Progress reporting
            if extract_idx % 10 == 0 or extract_idx == len(available_frames) - 1:
                progress = ((extract_idx + 1) / len(available_frames)) * 100
                print(f"Extracting frame {extract_idx + 1}/{len(available_frames)} "
                      f"(source frame {frame_idx}) - {progress:.1f}%")
            
            # Set all video captures to the correct frame
            for video_idx, cap in enumerate(video_captures):
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                
                if not ret:
                    print(f"Warning: Could not read frame {frame_idx} from video {video_idx}")
                    continue
                
                # Save the frame
                image_filename = f"image_{video_idx:05d}{extension}"
                image_path = os.path.join(frame_folder, image_filename)
                
                success = cv2.imwrite(image_path, frame, write_params)
                if not success:
                    print(f"Warning: Could not save {image_path}")
    
    except KeyboardInterrupt:
        print("\nProcessing interrupted by user")
        return False
    
    except Exception as e:
        print(f"\nError during processing: {str(e)}")
        return False
    
    finally:
        # Clean up
        for cap in video_captures:
            cap.release()
    
    print(f"\n🎉 Extraction completed successfully!")
    print(f"📁 Output structure:")
    print(f"   {output_folder}/")
    print(f"   ├── frame_00000/")
    print(f"   │   ├── image_00000{extension}")
    print(f"   │   ├── image_00001{extension}")
    print(f"   │   └── ... ({len(video_captures)} images)")
    print(f"   ├── frame_00001/")
    print(f"   └── ... ({total_frames_to_extract} frame folders)")
    
    return True

def preview_extraction_plan(input_folder):
    """
    Preview what would be extracted without actually doing it.
    """
    video_pattern = os.path.join(input_folder, "*.mp4")
    video_paths = glob.glob(video_pattern)
    video_paths.sort()
    
    if not video_paths:
        print(f"No .mp4 files found in {input_folder}")
        return
    
    print(f"Preview for folder: {input_folder}")
    print(f"Found {len(video_paths)} video files:")
    
    frame_counts = []
    total_size_mb = 0
    
    for i, video_path in enumerate(video_paths):
        cap = cv2.VideoCapture(video_path)
        if cap.isOpened():
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            file_size_mb = os.path.getsize(video_path) / (1024 * 1024)
            total_size_mb += file_size_mb
            
            frame_counts.append(frame_count)
            
            print(f"  {i:02d}: {os.path.basename(video_path)}")
            print(f"      Frames: {frame_count}, FPS: {fps:.1f}, Size: {width}x{height}")
            print(f"      File size: {file_size_mb:.1f} MB")
            
            cap.release()
    
    if frame_counts:
        min_frames = min(frame_counts)
        max_frames = max(frame_counts)
        
        print(f"\nSummary:")
        print(f"  Total videos: {len(video_paths)}")
        print(f"  Total input size: {total_size_mb:.1f} MB")
        print(f"  Frame count range: {min_frames} - {max_frames}")
        print(f"  Will extract: {min_frames} frames per video")
        print(f"  Total images: {min_frames * len(video_paths)}")
        
        # Estimate output size (rough calculation)
        estimated_size_mb = (min_frames * len(video_paths) * 0.1)  # ~100KB per image
        print(f"  Estimated output size: ~{estimated_size_mb:.1f} MB")

# Example usage
if __name__ == "__main__":
    # Configuration
    input_folder = "/Users/yaojie/Desktop/output/0604-GS/v/synced_tracks"      # Folder containing .mp4 files
    output_folder = "/Users/yaojie/Desktop/output/0604-GS/synced_output" # Where frame folders will be created
    
    # Preview what will be extracted (optional)
    print("=== PREVIEW ===")
    preview_extraction_plan(input_folder)
    print("\n" + "="*50 + "\n")
    
    # Check if input folder exists
    if not os.path.exists(input_folder):
        print(f"Error: Input folder '{input_folder}' not found!")
        print("Please create the folder and add your .mp4 files, or update the path.")
    else:
        # Basic extraction
        print("Starting basic extraction...")
        success = extract_synchronized_frames(input_folder, output_folder)
        
        # Alternative: Enhanced extraction with options
        """
        print("Starting enhanced extraction...")
        success = extract_synchronized_frames_with_options(
            input_folder=input_folder,
            output_folder=output_folder,
            image_format='jpg',  # or 'png'
            quality=95,          # JPEG quality
            max_frames=100,      # Limit to first 100 frames (None for all)
            skip_frames=0        # Extract every frame (1 = every other frame)
        )
        """
        
        if success:
            print(f"\n🎉 All done! Check the '{output_folder}' folder for your extracted frames.")
        else:
            print(f"\n❌ Extraction failed. Please check the error messages above.")
