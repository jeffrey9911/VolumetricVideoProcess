import os
import subprocess
import shutil
import argparse
from pathlib import Path

def run_colmap_command(cmd, working_dir=None):
    """Run a COLMAP command using subprocess"""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=working_dir, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error running command: {' '.join(cmd)}")
        print(f"stdout: {result.stdout}")
        print(f"stderr: {result.stderr}")
        raise RuntimeError(f"COLMAP command failed with return code {result.returncode}")
    
    print("Command completed successfully")
    return result

def create_directories(frame_path):
    """Create colmap and sparse directories in frame folder"""
    colmap_dir = frame_path / "colmap"
    sparse_dir = frame_path / "sparse"
    
    colmap_dir.mkdir(exist_ok=True)
    sparse_dir.mkdir(exist_ok=True)
    
    return colmap_dir, sparse_dir

def process_first_frame(frame_path, images_path):
    """Process the first frame with full COLMAP reconstruction"""
    print(f"\n=== Processing first frame: {frame_path.name} ===")
    
    colmap_dir, sparse_dir = create_directories(frame_path)
    database_path = colmap_dir / "database.db"
    
    # Step 1: Create database and extract features
    print("Step 1: Feature extraction...")
    cmd_extract = [
        "colmap", "feature_extractor",
        "--database_path", str(database_path),
        "--image_path", str(images_path),
        "--ImageReader.camera_model", "SIMPLE_RADIAL"
    ]
    run_colmap_command(cmd_extract)
    
    # Step 2: Exhaustive matching
    print("Step 2: Exhaustive matching...")
    cmd_match = [
        "colmap", "exhaustive_matcher",
        "--database_path", str(database_path)
    ]
    run_colmap_command(cmd_match)
    
    # Step 3: Sparse reconstruction (mapping)
    print("Step 3: Sparse reconstruction...")
    cmd_mapper = [
        "colmap", "mapper",
        "--database_path", str(database_path),
        "--image_path", str(images_path),
        "--output_path", str(sparse_dir)
    ]
    run_colmap_command(cmd_mapper)
    
    print(f"First frame reconstruction completed: {frame_path.name}")
    return sparse_dir

def process_subsequent_frame(frame_path, images_path, first_frame_sparse_dir):
    """Process subsequent frames using camera parameters from first frame"""
    print(f"\n=== Processing frame: {frame_path.name} ===")
    
    colmap_dir, sparse_dir = create_directories(frame_path)
    database_path = colmap_dir / "database.db"
    
    # Find the reconstruction folder in first frame (usually "0")
    first_recon_dirs = [d for d in first_frame_sparse_dir.iterdir() if d.is_dir()]
    if not first_recon_dirs:
        raise RuntimeError(f"No reconstruction found in first frame sparse directory: {first_frame_sparse_dir}")
    
    first_recon_dir = first_recon_dirs[0]  # Usually "0"
    
    # Copy cameras.bin and images.bin from first frame
    print("Copying camera parameters from first frame...")
    cameras_src = first_recon_dir / "cameras.bin"
    images_src = first_recon_dir / "images.bin"
    points3D_src = first_recon_dir / "points3D.bin"
    
    # Create reconstruction directory in current frame
    current_recon_dir = sparse_dir / "0"
    current_recon_dir.mkdir(exist_ok=True)
    
    cameras_dst = current_recon_dir / "cameras.bin"
    images_dst = current_recon_dir / "images.bin"
    points3D_dst = current_recon_dir / "points3D.bin"
    
    if cameras_src.exists():
        shutil.copy2(cameras_src, cameras_dst)
        print(f"Copied cameras.bin")
    else:
        raise RuntimeError(f"cameras.bin not found in first frame: {cameras_src}")
    
    if images_src.exists():
        shutil.copy2(images_src, images_dst)
        print(f"Copied images.bin")
    else:
        raise RuntimeError(f"images.bin not found in first frame: {images_src}")
    
    if points3D_src.exists():
        shutil.copy2(points3D_src, points3D_dst)
        print(f"Copied points3D.bin")
    else:
        raise RuntimeError(f"points3D.bin not found in first frame: {points3D_src}")
    
    # Step 1: Create database and extract features
    print("Step 1: Feature extraction...")
    cmd_extract = [
        "colmap", "feature_extractor",
        "--database_path", str(database_path),
        "--image_path", str(images_path),
        "--ImageReader.camera_model", "SIMPLE_RADIAL"
    ]
    run_colmap_command(cmd_extract)
    
    # Step 2: Exhaustive matching
    print("Step 2: Exhaustive matching...")
    cmd_match = [
        "colmap", "exhaustive_matcher",
        "--database_path", str(database_path)
    ]
    run_colmap_command(cmd_match)
    
    # Step 3: Point triangulation
    print("Step 3: Point triangulation...")
    cmd_triangulator = [
        "colmap", "point_triangulator",
        "--database_path", str(database_path),
        "--image_path", str(images_path),
        "--input_path", str(current_recon_dir),
        "--output_path", str(current_recon_dir)
    ]
    run_colmap_command(cmd_triangulator)
    
    print(f"Frame reconstruction completed: {frame_path.name}")

def main():
    parser = argparse.ArgumentParser(description="COLMAP reconstruction pipeline for multi-frame data")
    parser.add_argument("project_path", help="Path to the project folder containing all frames")
    parser.add_argument("--colmap_exe", default="colmap", help="Path to COLMAP executable (default: colmap)")
    
    args = parser.parse_args()
    
    project_path = Path(args.project_path)
    
    if not project_path.exists():
        raise RuntimeError(f"Project path does not exist: {project_path}")
    
    # Find all frame folders
    frame_folders = sorted([d for d in project_path.iterdir() 
                          if d.is_dir() and d.name.startswith("frame_")])
    
    if not frame_folders:
        raise RuntimeError(f"No frame folders found in {project_path}")
    
    print(f"Found {len(frame_folders)} frame folders:")
    for frame in frame_folders:
        print(f"  - {frame.name}")
    
    # Process first frame
    first_frame = frame_folders[0]
    first_images_path = first_frame / "images"
    
    if not first_images_path.exists():
        raise RuntimeError(f"Images folder not found in first frame: {first_images_path}")
    
    first_sparse_dir = process_first_frame(first_frame, first_images_path)
    
    # Process subsequent frames
    for frame_folder in frame_folders[1:]:
        images_path = frame_folder / "images"
        
        if not images_path.exists():
            print(f"Warning: Images folder not found in {frame_folder.name}, skipping...")
            continue
        
        try:
            process_subsequent_frame(frame_folder, images_path, first_sparse_dir)
        except Exception as e:
            print(f"Error processing frame {frame_folder.name}: {e}")
            continue
    
    print("\n=== All frames processed successfully! ===")

if __name__ == "__main__":
    main()
