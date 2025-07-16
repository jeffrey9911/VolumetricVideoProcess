import os
import subprocess
import shutil
import argparse
from pathlib import Path

def rs_first_align(rs_path, import_path, export_path, xml_path):
    cmd = [
        rs_path, "-headless",
        "-addFolder", str(import_path),
        "-align",
        "-exportXMP",
        "-exportRegistration", f"{str(export_path)}/placeholder.txt", str(xml_path),
        "-quit"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Error running command: {' '.join(cmd)}")
        print(f"stdout: {result.stdout}")
        print(f"stderr: {result.stderr}")
        raise RuntimeError(f"COLMAP command failed with return code {result.returncode}")
        return False
    else:
        return True
    
def rs_align_with_xmp(rs_path, import_path, export_path, xml_path):
    cmd = [
        rs_path, "-headless",
        "-addFolder", str(import_path),
        "-align",
        "-exportRegistration", f"{str(export_path)}/placeholder.txt", str(xml_path),
        "-quit"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Error running command: {' '.join(cmd)}")
        print(f"stdout: {result.stdout}")
        print(f"stderr: {result.stderr}")
        raise RuntimeError(f"COLMAP command failed with return code {result.returncode}")
        return False
    else:
        return True

def check_directories(path):
    if not path.exists():
        # create the directory if it does not exist
        print(f"Creating directory: {path}")
        path.mkdir(parents=True, exist_ok=True)


def main():
    parser = argparse.ArgumentParser(description="COLMAP reconstruction pipeline for multi-frame data")
    parser.add_argument("--project_path", help="Path to the project folder containing all frames", required=True)
    parser.add_argument("--rs_exe", help="Path to RealityScan executable", required=True)
    parser.add_argument("--export_path", help="Path to export directory for RS alignment", required=True)
    parser.add_argument("--xml_path", help="Path to export profile for RS alignment", required=True)
    
    args = parser.parse_args()
    
    project_path = Path(args.project_path)
    rs_exe = Path(args.rs_exe)
    export_path_base = Path(args.export_path)
    xml_path = Path(args.xml_path)
    
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

    images_path = first_frame/"images"

    export_path = export_path_base/first_frame.name
    export_path.mkdir(parents=True, exist_ok=True)

    # get XMP file from images_path
    
    if (rs_first_align(rs_exe, images_path, export_path, xml_path)):
        print(f"First frame {first_frame.name} aligned successfully.")
        xmp_files = list(images_path.glob("*.xmp"))
        if not xmp_files:
            print(f"No XMP files found in {images_path}, skipping subsequent frames alignment.")
            exit(0)

        for xmp_file in xmp_files:
            for frame_folder in frame_folders[1:]:
                shutil.copy2(xmp_file, frame_folder/"images")
                print(f"Copied XMP file {xmp_file.name} to {frame_folder/'images'}")
    

    print("\n=== All frames processed successfully! ===")
    
    
'''  
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
    ''' 
    

if __name__ == "__main__":
    main()
