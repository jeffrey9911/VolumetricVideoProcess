import subprocess
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Copy colmap data from one folder to another")
    parser.add_argument("--colmap", help="Path to colmap frames")
    parser.add_argument("--nobg", help="Path to no background frames")


    args = parser.parse_args()

    colmap_path = Path(args.colmap)
    nobg_path = Path(args.nobg)

    colmap_frame_folders = sorted([d for d in colmap_path.iterdir()
                          if d.is_dir()])
    
    nobg_frame_folders = sorted([d for d in nobg_path.iterdir()
                            if d.is_dir()])

    nobg_dict = {}

    for track_folder in nobg_frame_folders:
        images = sorted([img for img in track_folder.glob("*.png")])
        nobg_dict[track_folder.name] = images
        

    #for i in len(colmap_frame_folders):

    for colmap in colmap_frame_folders:
        print(f"Processing folder: {colmap.name}")

    for track in nobg_dict:
        print(f"Processing track: {track}")
        for img in nobg_dict[track]:
            print(f"Copying {img.name} to {colmap / track}")


    print("\n=== All frames processed successfully! ===")

if __name__ == "__main__":
    main()
